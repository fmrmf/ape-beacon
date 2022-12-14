from typing import Any, Literal, Union, get_args

from ape.types import BlockID
from eth_typing import HexStr
from hexbytes import HexBytes

BeaconBlockID = Union[int, HexStr, HexBytes, Literal["genesis", "head", "finalized"]]
"""
An ID that can match a beacon block, such as the literals ``"genesis"``, ``"head"``,
or ``"finalized"`` as well as a block number or hash (HexBytes).
"""

BytesLike = Union[bool, bytearray, bytes, int, str, memoryview]
"""
hexbytes BytesLike typing
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


def attempt_to_hexbytes(value: Any) -> Any:
    """
    Attempts to convert `value` to type HexBytes. Passes
    through `value` if not of correct input type.
    """
    if value and isinstance(value, get_args(BytesLike)):
        return HexBytes(value)

    return value
