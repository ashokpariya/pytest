import os
import pingparsing
import sys
import time
from acc_pyutils.api import KubeAPI
from acc_pyutils import exceptions as kctlexc, logger


LOG = logger.get_logger(__name__)
PWD = os.path.dirname(os.path.abspath(__file__))
KAPI = KubeAPI()
PACKET_COUNT = 5
POD_MANIFEST_FILE = PWD + '/pod_create.yaml'
POD_CREATION_WAITING_TIME = 5

def check_pods_reachability():
    """
    Check pod reachability.

    :param:
    :return:
    """
    try:
        # create 2 pods
        KAPI.create(POD_MANIFEST_FILE)
        # wait for pods to get into ready state
        time.sleep(POD_CREATION_WAITING_TIME)
        # get pods info
        pod1_info = KAPI.get('pod', 'pod1')
        pod2_info = KAPI.get('pod', 'pod2')

        #verify readiness of pods
        msg = ("pod {} status is {}".format(
               pod1_info['metadata']['name'], pod1_info['status']['phase']))
        LOG.debug(msg)
        assert pod1_info['status']['phase'] == "Running"

        msg = ("pod {} status is {}".format(
               pod2_info['metadata']['name'], pod2_info['status']['phase']))
        LOG.debug(msg)
        assert pod2_info['status']['phase'] == "Running"

        pod1_ip = pod2_info['status']['podIP']
        pod2_ip = pod2_info['status']['podIP']
        assert pod1_ip != None or pod2_ip != None

        #prepare commnad to be executed on pod1
        cmd1 = 'ping -c ' + str(PACKET_COUNT) + ' ' + pod2_ip
        pod_info = KAPI.kexec('pod1', cmd1)
        parser = pingparsing.PingParsing()
        parser.parse(pod_info)
        parser_output = parser.as_dict()

        msg = ("Expected {} received packet count, got {}".format(
               PACKET_COUNT, parser_output['packet_receive']))
        LOG.debug(msg)
        assert parser_output['packet_transmit'] == parser_output['packet_receive']
        assert pod2_ip == parser_output['destination']
    except kctlexc.KctlExecutionFailed as ex:
        LOG.error(ex)
        assert 0

class TestPodsReachability(object):
    """
    This test class provides utility to create pods
    and check their reachability.

    """
    def test_pods_reachablity(self):
        check_pods_reachability()
