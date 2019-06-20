import sys
sys.path.append('/home/ubuntu/k8s_resource_tracking/acc-pyutils')
from acc_pyutils.api import KubeAPI
from acc_pyutils import exceptions as kctlexc

KAPI = KubeAPI()

def check_replicaset_status(replicaset, namespace):
    """
    Check replicaset status.

    :param replicaset: replicaset name
    :param namespace:
    :return:
    """
    #get replicaset info
    try:
        replicaset_info = KAPI.get('replicaset', replicaset, namespace=namespace)
    except kctlexc.KctlExecutionFailed as ex:
        print ex
        assert 0
    # get replicaset count from spec
    replicaset_count = replicaset_info['spec']['replicas']
    replicaset_status = replicaset_info['status']
    # get available replicaset count
    available_replicaset = replicaset_status['availableReplicas']
    ready_replicaset = replicaset_status['readyReplicas']

    #compare ready and available replicacount with replicaset count
    #from spec
    assert replicaset_count == available_replicaset == ready_replicaset


class TestReplicaset(object):
    """
    This class provides utility to check replicaset
    status.

    """
    def test_replicaset_status(self, replicaset, namespace):
        check_replicaset_status(replicaset, namespace)

