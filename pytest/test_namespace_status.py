import sys
from acc_pyutils import exceptions as kctlexc
from acc_pyutils.api import KubeAPI


KAPI = KubeAPI()

def check_namespace_status(namespace):
    """
    Check namespace status.

    :param namespace:
    :return:
    """
    #get namespace info
    try:
        namespace_info = KAPI.get('namespace', namespace)
    except kctlexc.KctlExecutionFailed as ex:
        print ex
        assert 0
    #check if namespace is in active state
    assert namespace_info['status']['phase'] == "Active"


class TestNamespace(object):
    """
    This class provides utility to check namespace
    status.

    """
    def test_namespace_status(self, namespace):
        check_namespace_status(namespace)
