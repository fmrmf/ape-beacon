import pytest
import requests
from ape.exceptions import ProviderNotConnectedError
from eth_typing import HexStr


def test_beacon(beacon_test_provider):
    # connected
    beacon_test_provider.connect()
    b = beacon_test_provider.beacon
    assert b is not None

    # disconnected
    beacon_test_provider.disconnect()
    with pytest.raises(ProviderNotConnectedError):
        beacon_test_provider.beacon


def test_is_connected(beacon_test_provider):
    # before connected
    actual = beacon_test_provider.is_connected
    expect = False
    assert actual == expect

    # after connected
    beacon_test_provider.connect()
    actual = beacon_test_provider.is_connected
    expect = True
    assert actual == expect

    # after disconnected
    beacon_test_provider.disconnect()
    actual = beacon_test_provider.is_connected
    expect = False
    assert actual == expect


def test_client_version(configured_beacon_test_provider):
    actual = configured_beacon_test_provider.client_version
    expect = "Lighthouse/v0.1.5 (Linux x86_64)"
    assert actual == expect


@pytest.mark.parametrize("block_id", (1, "1", "0x1", HexStr("0x1")))
def test_get_block(configured_beacon_test_provider, block_id):
    actual = configured_beacon_test_provider.get_block(block_id)
    endpoint = configured_beacon_test_provider.uri + f"/eth/v2/beacon/blocks/{block_id}"
    resp = requests.get(endpoint).json()
    block_data = resp["data"]["message"]
    expect = configured_beacon_test_provider.network.ecosystem.decode_block(block_data)
    assert actual == expect
