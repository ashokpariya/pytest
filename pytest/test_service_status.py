import sys
sys.path.append('/home/ubuntu/k8s_resource_tracking/acc-pyutils')
from acc_pyutils.api import KubeAPI
from acc_pyutils import exceptions as kctlexc

KAPI = KubeAPI()

def check_service_status(service, namespace):
    """
    Check service status.

    :param service: service name
    :param namespace:
    :return:
    """
    #get service info
    try:
        service_info = KAPI.get('service', service, namespace=namespace)
    except kctlexc.KctlExecutionFailed as ex:
        print ex
        assert 0
    # get cluster ip
    cluster_ip = service_info['spec']['clusterIP']

    # check reachablity for cluster ip with port
    for i in range(len(service_info['spec']['ports'])):
        port = service_info['spec']['ports'][i]['port']
        cmd = ['nc', '-zvnw', '1', cluster_ip, str(port)]
        try:
            KAPI.execute(cmd)
        except kctlexc.KctlExecutionFailed as ex:
            print ex
            assert 0

class TestService(object):
    """
    This class provides utility to check service
    status.

    """
    def test_service_status(self, service, namespace):
        check_service_status(service, namespace)
