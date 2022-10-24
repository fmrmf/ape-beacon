import pytest
import requests
from ape.exceptions import BlockNotFoundError, ProviderNotConnectedError
from eth_typing import HexStr

from ape_beacon.exceptions import ValidatorNotFoundError


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


@pytest.mark.parametrize("block_id", ("s", 2, -1))
def test_get_block_raises_when_not_exists(configured_beacon_test_provider, block_id):
    with pytest.raises(BlockNotFoundError):
        configured_beacon_test_provider.get_block(block_id)


@pytest.mark.parametrize(
    "validator_id",
    (
        "110280",
        "0x93247f2209abcacf57b75a51dafae777f9dd38bc7053d1af526f220a7489a6d3a2753e5f3e8b1cfe39b56f43611df74a",  # noqa: E501
    ),
)
def test_get_balance(configured_beacon_test_provider, validator_id):
    actual = configured_beacon_test_provider.get_balance(validator_id)
    endpoint = (
        configured_beacon_test_provider.uri
        + f"/eth/v1/beacon/states/head/validators/{validator_id}"
    )
    resp = requests.get(endpoint).json()
    expect = int(resp["data"]["balance"])
    assert actual == expect


@pytest.mark.parametrize("validator_id", ("s", "2", "-1"))
def test_get_balance_raises_when_not_exists(configured_beacon_test_provider, validator_id):
    with pytest.raises(ValidatorNotFoundError):
        configured_beacon_test_provider.get_balance(validator_id)


def test_block_ranges_when_stop_not_none(configured_beacon_test_provider):
    expect = [(0, 1), (2, 3), (4, 5)]
    actual = [
        (start, stop)
        for start, stop in configured_beacon_test_provider.block_ranges(stop=5, page=2)
    ]
    assert actual == expect


# TODO: test_block_ranges with chain height when fix test network provider
