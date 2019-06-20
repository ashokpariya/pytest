import getopt
import os
import sys
import yaml

from acc_pyutils import exceptions as kctlexc, logger, utils

LOG = logger.get_logger(__name__)
PWD = os.path.dirname(os.path.abspath(__file__))
PYTEST_EXECUTE = ['pytest', '-q']


class TestExecutor(object):
    def __init__(self, **kwargs):
        if 'testcase_file' in kwargs:
            if not kwargs['testcase_file']:
                msg = ("Provide test case yaml file")
                LOG.error(msg)
                sys.exit(1)
            self.testcase_file = kwargs['testcase_file']
        else:
            msg = ("Please provide test case yaml file")
            LOG.error(msg)
            sys.exit(1)

    def read_testcase_yaml(self):
        """read testcase yaml file """
        if os.path.isfile(self.testcase_file):
            with open(self.testcase_file, 'r') as stream:
                try:
                    return yaml.load(stream, Loader=yaml.FullLoader)
                except yaml.YAMLError as exc:
                    msg = "Unable to load testcase yaml. Reason: %s" % exc
                    LOG.error(msg)
                    return None
        else:
            return None

    def prepare_command_list(self, kind, test_case, inputs):
        """prepare pytest commnad"""
        resource_name = inputs['name']
        apply_list = [test_case + ".py", "--" + kind + "=" + resource_name]
        inputs.pop('name')
        for k, v in iter(inputs.items()):
            if v is not None:
                apply_list += ["--" + k+"="+ v]
        return apply_list


    def execute_pytest(self, kind, testcase, inputs):
        """execute pytest command"""
        apply_list = self.prepare_command_list(kind, testcase, inputs)
        try:
            output = utils.execute(PYTEST_EXECUTE + apply_list)
            return True if "passed" in output else False
        except kctlexc.KctlExecutionFailed as ex:
            msg = ("Test execution failed with exception:", ex)
            LOG.error(msg)
            return False

    def run_test(self, testcase_config):
        """run test"""
        for test_case in testcase_config['tests']:
            test = test_case['test_case'].split(".")
            k8s_resource_kind = test[0]
            testcase_module = test[1]
            inputs = test_case['inputs']
            resource_name = inputs['name']
            result = self.execute_pytest(k8s_resource_kind,
            	testcase_module, inputs)
            if result:
                msg = ("Testcase %s for resource %s has passed" % (
                    test[1], resource_name))
                print(msg)
                LOG.info(msg)
            else:
                msg = ("Testcase %s for resource %s has failed" % (
                    test[1], resource_name))
                print(msg)
                LOG.error(msg)

    def execute_test(self):
    	"""verify testcase yaml and execute tests. """
        testcase_config = self.read_testcase_yaml()
        if not testcase_config:
            msg = ("Unable to load testcase yaml, check syslogs for "
                   "more info.")
            print(msg)
            LOG.error(msg)
            sys.exit(1)
        else:
            self.run_test(testcase_config)


def main(argv):
    testcase_file = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ht:")
    except getopt.GetoptError:
        msg = ("test_executor.py [-t <testcase.yaml>]")
        print(msg)
        LOG.error(msg)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("")
            sys.exit(2)
        elif opt == '-t':
            testcase_file = arg

    kwargs = {'testcase_file': testcase_file}
    try:
        obj = TestExecutor(**kwargs)
    except Exception as err:
        msg = ("Unable to initialise test executor. "
               "Check syslog for more details.")
        print(msg)
        LOG.error(msg)
        sys.exit(1)

    try:
        obj.execute_test()
    except Exception as err:
        msg = ("Unable to start test executor. "
               "Check syslog for more details.")
        print(msg)
        LOG.err(msg)
        sys.exit(err)


if __name__ == '__main__':
    # check user is root user
    if os.geteuid() != 0:
        msg = ("You need to have root privileges to run this script."
               "\n try again, using 'sudo'. Exiting.")
        print(msg)
        sys.exit(0)
    main(sys.argv[1:])
