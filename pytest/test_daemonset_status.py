import sys
from acc_pyutils.api import KubeAPI
from acc_pyutils import exceptions as kctlexc

KAPI = KubeAPI()

def check_daemonset_status(daemonset, namespace):
    """
    Check daemonset status.

    :param daemonset: daemonset name
    :param namespace:
    :return:
    """
    #get daemonset info
    try:
        daemonset_info = KAPI.get('daemonset', daemonset, namespace=namespace)
    except kctlexc.KctlExecutionFailed as ex:
        print ex
        assert 0
    # get daemonset status
    for i in range(len(daemonset_info['items'])):
        daemonset_status = daemonset_info['items'][i]['status']
        current_number_scheduled = daemonset_status['currentNumberScheduled']
        desired_number_scheduled = daemonset_status['desiredNumberScheduled']
        number_ready = daemonset_status['numberReady']
        number_unavailable = daemonset_status['numberUnavailable']
        assert current_number_scheduled == desired_number_scheduled == number_ready
        assert number_unavailable == 0


class TestDaemonset(object):
    """
    This class provides utility to check daemonset
    status.

    """
    def test_daemonset_status(self, daemonset, namespace):
        check_daemonset_status(daemonset, namespace)
