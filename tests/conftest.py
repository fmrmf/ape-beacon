import ape
import pytest


@pytest.hookimpl(trylast=True, hookwrapper=True)
def pytest_collection_finish(session):
    with ape.networks.parse_network_choice("::test"):
        # Sets the active provider
        yield


@pytest.fixture(scope="session")
def networks():
    return ape.networks


@pytest.fixture(scope="session")
def accounts():
    return ape.accounts


@pytest.fixture(scope="session")
def networks_connected_to_tester():
    with ape.networks.parse_network_choice("::test"):
        yield ape.networks


@pytest.fixture
def networks_disconnected(networks):
    provider = networks.active_provider
    networks.active_provider = None
    yield networks
    networks.active_provider = provider


@pytest.fixture(scope="session")
def beacon(networks):
    return networks.beacon


@pytest.fixture(scope="session")
def ethereum(networks):
    return networks.ethereum


@pytest.fixture(scope="session")
def eth_tester_provider(networks_connected_to_tester):
    yield networks_connected_to_tester.provider
