import pytest


@pytest.fixture(scope="module")
def in_beacon(networks):
    with networks.parse_network_choice("beacon:local"):
        yield


@pytest.fixture(scope="module")
def in_ethereum(networks):
    with networks.parse_network_choice("ethereum:local"):
        yield


# SEE: https://beaconcha.in/slot/1213760
# TODO: def test_in_beacon(in_beacon, networks, chain):
