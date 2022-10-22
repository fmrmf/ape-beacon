from typing import Literal, Union

from ape.types import BlockID
from eth_typing import HexStr
from hexbytes import HexBytes

BeaconBlockID = Union[int, HexStr, HexBytes, Literal["genesis", "head", "finalized"]]
"""
An ID that can match a beacon block, such as the literals ``"genesis"``, ``"head"``,
or ``"finalized"`` as well as a block number or hash (HexBytes).
"""


def convert_block_id(block_id: BlockID) -> BeaconBlockID:
    if block_id == "earliest":
        return "genesis"
    elif block_id == "latest":
        return "head"
    elif block_id == "pending":
        # TODO: make sure this is ok. is "pending" in eth1 land really this? (sorta?)
        return "finalized"
    return block_id
