import ape
import pytest


@pytest.fixture(scope="session")
def networks():
    return ape.networks


@pytest.fixture(scope="session")
def accounts():
    return ape.accounts


@pytest.fixture(scope="session")
def beacon(networks):
    return networks.beacon


@pytest.fixture(scope="session")
def ethereum(networks):
    return networks.ethereum
