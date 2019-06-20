import sys
from acc_pyutils.api import KubeAPI
from acc_pyutils import exceptions as kctlexc

KAPI = KubeAPI()

def check_configmap_status(configmap, namespace):
    """
    Check configmap status.

    :param configmap: configmap name
    :param namespace:
    :return:
    """
    try:
        configmap_info = KAPI.get('configmap', configmap, namespace=namespace)
    except kctlexc.KctlExecutionFailed as ex:
        print ex
        assert 0
    # check if configmap id is present or not
    assert configmap_info['metadata']['uid'] is not None


class TestConfigmap(object):
    """
    This class provides utility to check configmap
    status.

    """
    def test_configmap_status(self, configmap, namespace):
        check_configmap_status(configmap, namespace)
