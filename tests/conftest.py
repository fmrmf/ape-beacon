from pathlib import Path
from tempfile import mkdtemp

import ape
import pytest
from ape.api.networks import LOCAL_NETWORK_NAME

from ape_beacon.test import LocalBeaconProvider

# NOTE: Ensure that we don't use local paths for these
ape.config.DATA_FOLDER = Path(mkdtemp()).resolve()
ape.config.PROJECT_FOLDER = Path(mkdtemp()).resolve()

# COPIED FROM: https://github.com/ApeWorX/ape/blob/main/tests/conftest.py


@pytest.fixture(autouse=True)
def setenviron(monkeypatch):
    """
    Sets the APE_TESTING environment variable during tests.
    With this variable set fault handling and IPython command history logging
    will be disabled in the ape console.
    """
    monkeypatch.setenv("APE_TESTING", "1")


@pytest.fixture(scope="session")
def config():
    yield ape.config


@pytest.fixture(scope="session")
def plugin_manager():
    yield ape.networks.plugin_manager


@pytest.fixture(scope="session")
def networks():
    return ape.networks


@pytest.fixture(scope="session")
def accounts():
    return ape.accounts


@pytest.fixture(scope="session")
def chain():
    return ape.chain


@pytest.fixture(scope="session")
def beacon(networks):
    return networks.beacon


@pytest.fixture(scope="session")
def ethereum(networks):
    return networks.ethereum


@pytest.fixture(scope="session")
def networks_connected_to_tester():
    # TODO: fix
    with ape.networks.beacon.local.use_provider("test"):
        yield ape.networks


@pytest.fixture(scope="session")
def beacon_tester_provider(networks_connected_to_tester):
    yield networks_connected_to_tester.provider


@pytest.fixture(scope="session")
def test_accounts(accounts):
    return accounts.test_accounts


@pytest.fixture(scope="session")
def sender(test_accounts):
    return test_accounts[0]


@pytest.fixture(scope="session")
def receiver(test_accounts):
    return test_accounts[1]


@pytest.fixture(scope="session")
def owner(test_accounts):
    return test_accounts[2]


@pytest.fixture(scope="module")
def beacon_test_provider(beacon):
    network = beacon.networks[LOCAL_NETWORK_NAME]
    return LocalBeaconProvider(
        name="adhoc",
        network=network,
        provider_settings={},
        data_folder=network.data_folder,
        request_header=network.request_header,
    )


@pytest.fixture(scope="module")
def configured_beacon_test_provider(beacon):
    network = beacon.networks[LOCAL_NETWORK_NAME]
    provider = LocalBeaconProvider(
        name="adhoc",
        network=network,
        provider_settings={},
        data_folder=network.data_folder,
        request_header=network.request_header,
    )

    # sandwich for setup and teardown
    provider.connect()
    yield provider
    provider.disconnect()
