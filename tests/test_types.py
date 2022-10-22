from eth_typing import HexStr
from hexbytes import HexBytes

from ape_beacon.types import convert_block_id


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


def test_convert_block_id_when_not_literal():
    # int
    expect_int = 10
    actual_int = convert_block_id(10)
    assert expect_int == actual_int

    # HexStr
    expect_hex_str = HexStr("0xA")
    actual_hex_str = convert_block_id(HexStr("0xA"))
    assert actual_hex_str == expect_hex_str

    # HexBytes
    expect_hex_bytes = HexBytes("0xA")
    actual_hex_bytes = convert_block_id(HexBytes("0xA"))
    assert actual_hex_bytes == expect_hex_bytes
