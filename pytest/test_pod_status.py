import sys                                                                                 
sys.path.append('/home/ubuntu/k8s_resource_tracking/acc-pyutils')                                                                   
from acc_pyutils.api import KubeAPI                                                                               11,1          All
from acc_pyutils import exceptions as kctlexc

KAPI = KubeAPI()

def check_pod_status(pod, namespace):
    """
    Check pod status.

    :param pod: pod name
    :param namespace:
    :return:
    """
    #get pod status
    try:
        pod_info = KAPI.get('pod', pod, namespace=namespace)
        print "pod {} status is {}".format(
               pod_info['metadata']['name'], pod_info['status']['phase'])
    except kctlexc.KctlExecutionFailed as ex:
        print ex
        assert 0
    assert pod_info['status']['phase'] == "Running"
        