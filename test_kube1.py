import pingparsing
import pytest
import subprocess
import time

from acc_pyutils.api import KubeAPI
from multiprocessing.pool import ThreadPool


class TestDeployment:
    @pytest.mark.skip(reason="currently not testing this")
    def test_nginx(self):
        kapi = KubeAPI()
        status, label, manifest_dir = kapi.create(
            '../acc_pyutils/tests/nginx.yml')
        assert status is True
        kapi.delete(label, manifest_dir)

    def test_pod_external_reachability(self):
        packet_count = 5
        server_ip = '10.3.0.252'
        server_port = 80
        kapi = KubeAPI()
        status, label, manifest_dir = kapi.create(
            '../acc_pyutils/tests/client-pod.yaml')
        assert status is True

        # get client pod info
        pod_info = kapi.get('pod', 'client-pod')
        host_ip = pod_info.get('hostIP')
        cmd = 'curl --connect-timeout 1 -s ' + \
             server_ip + ':' + str(server_port)
        output = kapi.kexec('client-pod', cmd)
        assert output != None
        assert "timed out" not in output.decode("utf-8")

        # verify server reachability
        cmd1 = 'ping -c ' + str(packet_count) + ' ' + server_ip
        pod_info = kapi.kexec('client-pod', cmd1)
        parser = pingparsing.PingParsing()
        parser.parse(pod_info)
        parser_output = parser.as_dict()

        assert parser_output['packet_transmit'] == parser_output['packet_receive']
        assert server_ip == parser_output['destination']

        pool = ThreadPool(processes=1)
        #check packet source on server
        async_result = pool.apply_async(self.verify_on_host, (host_ip,))
        cmd = 'nc -zvnw 1 ' + server_ip + ' ' + str(server_port)
        kapi.kexec('client-pod', cmd)
        assert async_result.get() == True
        # delete client pod
        kapi.delete(label, manifest_dir)


    def verify_on_host(self, host_ip):
        """
        Verify source of packet on server interface.

        :param: hostIP
        :return:
        """
        host_interface = 'ens5'
        server_port = 80
        cmd = ['tcpdump', '-leni', host_interface, 'port', str(server_port)]
        process = subprocess.Popen((cmd), stdout=subprocess.PIPE)
        time.sleep(10)
        process.terminate()
        while True:
            output = process.stdout.readline()
            if output == '':
                return False
            else:
                if host_ip in output.decode("utf-8").strip():
                    return True
