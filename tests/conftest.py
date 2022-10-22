from pathlib import Path
from tempfile import mkdtemp

import ape
import pytest

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
def beacon(networks):
    return networks.beacon


@pytest.fixture(scope="session")
def ethereum(networks):
    return networks.ethereum


@pytest.fixture(scope="session")
def networks_connected_to_tester():
    with ape.networks.beacon.local.use_provider("test"):
        yield ape.networks


@pytest.fixture(scope="session")
def beacon_tester_provider(networks_connected_to_tester):
    yield networks_connected_to_tester.provider
