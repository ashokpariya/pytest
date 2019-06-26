import os
import pingparsing
import subprocess
import sys
import time
from acc_pyutils.api import KubeAPI
from acc_pyutils import exceptions as kctlexc, logger
from multiprocessing.pool import ThreadPool


LOG = logger.get_logger(__name__)
PWD = os.path.dirname(os.path.abspath(__file__))
KAPI = KubeAPI()
# fixme [config parameters]
PACKET_COUNT = 5
POD_MANIFEST_FILE = PWD + '/client-pod.yaml'
POD_CREATION_WAITING_TIME = 5
SERVER_IP = '10.3.0.252'
SERVER_PORT = 80
HOST_INTERFACE = 'ens5'


def verify_on_host(host_ip):
    """
    Verify source of packet on server interface.

    :param: hostIP
    :return:
    """
    cmd = ['tcpdump', '-leni', HOST_INTERFACE, 'port', str(SERVER_PORT)]
    p = subprocess.Popen((cmd), stdout=subprocess.PIPE)
    time.sleep(10)
    p.terminate()
    for row in iter(p.stdout.readline, b''):
        if host_ip in row.rstrip():
            return True
    LOG.error("packet not received from client pod")
    return False


def check_pods_external_reachability():
    """
    Check pod external reachability.

    :param:
    :return:
    """
    try:
        # create client pod
        KAPI.create(POD_MANIFEST_FILE)
        # wait for pods to get into ready state
        time.sleep(POD_CREATION_WAITING_TIME)
        # get pods info
        pod_info = KAPI.get('pod', 'client-pod')
        if 'status' in pod_info:
            #verify readiness of pods
            assert pod_info['status'].get('phase') == "Running"
            pod_ip = pod_info['status'].get('podIP')
            hostIP = pod_info['status'].get('hostIP')
            assert pod_ip != None
        else:
            LOG.error("unable to get client pod info")
            assert 0

        #prepare commnad to be executed on pod1
        cmd = 'curl --connect-timeout 1 -s ' + \
            SERVER_IP + ':' + str(SERVER_PORT)
        output = KAPI.kexec('client-pod', cmd)
        assert output != None
        if "timed out" in output:
            LOG.error("timed out while receiving data from server")
            assert 0

        # verify server reachability
        cmd1 = 'ping -c ' + str(PACKET_COUNT) + ' ' + SERVER_IP
        pod_info = KAPI.kexec('client-pod', cmd1)
        parser = pingparsing.PingParsing()
        parser.parse(pod_info)
        parser_output = parser.as_dict()

        msg = ("Expected {} received packet count, got {}".format(
            PACKET_COUNT, parser_output['packet_receive']))
        LOG.debug(msg)
        assert parser_output['packet_transmit'] == parser_output['packet_receive']
        assert SERVER_IP == parser_output['destination']

        pool = ThreadPool(processes=1)
        #check packet source on server
        async_result = pool.apply_async(verify_on_host, (host_ip,))
        cmd = 'nc -zvnw 1 ' + SERVER_IP + ' ' + str(SERVER_PORT)
        KAPI.kexec('client-pod', cmd)
        assert async_result.get() == True
    except kctlexc.KctlExecutionFailed as ex:
        LOG.error(ex)
        assert 0


class TestPodsExternalReachability(object):
    """
    This test class create client pod and
    and check its external reachability with
    provided server details.

    """
    def test_pods_reachablity(self):
        #import pdb;pdb.set_trace()
        check_pods_external_reachability()



