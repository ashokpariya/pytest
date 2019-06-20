import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--namespace", action="store", default="default", help="name of namespace"
    )
    parser.addoption(
        "--pod", action="store", default="", help="provide pod name"
    )
    parser.addoption(
        "--deployment", action="store", default="", help="name of deployment"
    )
    parser.addoption(
        "--replicaset", action="store", default="", help="name of replicaset"
    )
    parser.addoption(
        "--service", action="store", default="", help="name of service"
    )
    parser.addoption(
        "--daemonset", action="store", default="", help="name of daemonset"
    )
    parser.addoption(
        "--configmap", action="store", default="", help="name of daemonset"
    )



@pytest.fixture
def namespace(request):
    return request.config.getoption("--namespace")

@pytest.fixture
def pod(request):
    return request.config.getoption("--pod")

@pytest.fixture
def deployment(request):
    return request.config.getoption("--deployment")


@pytest.fixture
def replicaset(request):
    return request.config.getoption("--replicaset")

@pytest.fixture
def service(request):
    return request.config.getoption("--service")

@pytest.fixture
def daemonset(request):
    return request.config.getoption("--daemonset")

@pytest.fixture
def configmap(request):
    return request.config.getoption("--configmap")
