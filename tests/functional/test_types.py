import pytest
from eth_typing import HexStr
from hexbytes import HexBytes

from ape_beacon.types import attempt_to_hexbytes, convert_block_id


def test_convert_block_id_when_literal():
    # genesis
    expect = "genesis"
    actual = convert_block_id("earliest")
    assert actual == expect

    # head
    expect = "head"
    actual = convert_block_id("latest")
    assert actual == expect

    # finalized
    expect = "finalized"
    actual = convert_block_id("pending")
    assert actual == expect


@pytest.mark.parametrize("block_id", (10, "0xA", HexStr("0xA"), HexBytes("0xA")))
def test_convert_block_id_when_not_literal(block_id):
    expect = block_id
    actual = convert_block_id(block_id)
    assert actual == expect


@pytest.mark.parametrize("value", (True, b"\\x01", 1, "1", "0x1"))
def test_attempt_to_hexbytes_when_bytes_like(value):
    expect = HexBytes(value)
    actual = attempt_to_hexbytes(value)
    assert actual == expect


@pytest.mark.parametrize("value", ({"a": "b"}, ["a", "b"]))
def test_attempt_to_hexbytes_when_not_bytes_like(value):
    expect = value
    actual = attempt_to_hexbytes(value)
    assert actual == expect
