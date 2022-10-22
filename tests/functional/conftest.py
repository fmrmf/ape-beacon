import pytest
from ape.api import EcosystemAPI, NetworkAPI
from ape.api.networks import LOCAL_NETWORK_NAME
from ape.exceptions import ContractLogicError


class _ContractLogicError(ContractLogicError):
    pass


@pytest.fixture
def mock_network_api(mocker):
    mock = mocker.MagicMock(spec=NetworkAPI)
    mock_ecosystem = mocker.MagicMock(spec=EcosystemAPI)
    mock_ecosystem.virtual_machine_error_class = _ContractLogicError
    mock.ecosystem = mock_ecosystem
    return mock


@pytest.fixture
def mock_beacon(mocker):
    return mocker.MagicMock()


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


@pytest.fixture
def dummy_live_network(chain):
    chain.provider.network.name = "goerli"
    yield chain.provider.network
    chain.provider.network.name = LOCAL_NETWORK_NAME
