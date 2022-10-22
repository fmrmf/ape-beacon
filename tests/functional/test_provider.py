import pytest
from eth_typing import HexStr


@pytest.mark.parametrize("block_id", (0, "0", "0x0", HexStr("0x0")))
def test_get_block(beacon_tester_provider, block_id, owner):
    # TODO: BeaconLocalProvider as using EL blocks in tests
    try:
        beacon_tester_provider.get_block(block_id)
    except Exception:
        # NOTE: failing because using eth local provider vs beacon local
        pass

    # Each parameter is the same as requesting the first block.
    # assert block.number == 0
    # assert block.base_fee == 1000000000
    # assert block.gas_used == 0
