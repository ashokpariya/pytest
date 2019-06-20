import sys
sys.path.append('/home/ubuntu/k8s_resource_tracking/acc-pyutils')
from acc_pyutils.api import KubeAPI
from acc_pyutils import exceptions as kctlexc

KAPI = KubeAPI()

def check_deployment_status(deployment, namespace):
    """
    Check deployment status.

    :param deployment: deployment name
    :param namespace:
    :return:
    """
    # get deployment info
    try:
        deployment_info = KAPI.get('deployment', deployment, namespace=namespace)
    except kctlexc.KctlExecutionFailed as ex:
        print ex
        assert 0
    # get replicaset count from spec
    replicaset_count = deployment_info['spec']['replicas']
    deployment_status = deployment_info['status']
    # get available replicaset count
    available_replicaset = deployment_status['availableReplicas']
    ready_replicaset = deployment_status['readyReplicas']

    # compare ready and available replicacount with replicaset count
    # from spec
    assert replicaset_count == available_replicaset == ready_replicaset

    # get last updated status of replicas
    replicaset_last_updated_status = deployment_status['conditions'][0]
    assert replicaset_last_updated_status['status'] == "True"
    assert replicaset_last_updated_status['type'] == "Available"

class TestDeployment(object):
    """
    This class provides utility to check deployment
    status.

    """
    def test_deployment_status(self, deployment, namespace):
        check_deployment_status(deployment, namespace)
