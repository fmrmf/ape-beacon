import pytest
from ape.api.networks import LOCAL_NETWORK_NAME

from ape_beacon.test import LocalBeaconProvider


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
