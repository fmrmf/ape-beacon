from typing import Any, Optional, get_args

from ape.api.providers import BlockAPI
from ape.utils import EMPTY_BYTES32
from hexbytes import HexBytes
from pydantic import BaseModel, validator

from .types import BytesLike


class Eth1Data(BaseModel):
    deposit_root: Any  # Bytes32
    deposit_count: int
    block_hash: Any  # EL block.hash

    @validator("block_hash", "deposit_root", pre=True)
    def convert_hexbytes(cls, value):
        if value and isinstance(value, get_args(BytesLike)):
            return HexBytes(value)

        return value

    @validator("block_hash", "deposit_root", pre=True)
    def validate_hexbytes(cls, value):
        # NOTE: pydantic treats these values as bytes and throws an error
        if value and not isinstance(value, HexBytes):
            raise ValueError(f"Hash `{value}` is not a valid Hexbytes.")

        return value


class SyncAggregate(BaseModel):
    sync_committee_bits: Any  # TODO: Bitvector[SYNC_COMMITTEE_SIZE]
    sync_committee_signature: Any  # TODO: Bytes96


class BeaconExecutionPayload(BlockAPI):
    """
    Class for representing a consensus layer block.
    """

    prev_randao: Any

    @validator("prev_randao", pre=True)
    def convert_hexbytes(cls, value):
        if value and isinstance(value, get_args(BytesLike)):
            return HexBytes(value)

        return value

    @validator("prev_randao", pre=True)
    def validate_hexbytes(cls, value):
        # NOTE: pydantic treats these values as bytes and throws an error
        if value and not isinstance(value, HexBytes):
            raise ValueError(f"Hash `{value}` is not a valid Hexbytes.")

        return value


class BeaconBlockBody(BaseModel):
    """
    Class for representing a consensus layer block body.

    Opinionated implementation of
    `Beacon block body
    <https://github.com/ethereum/beacon-APIs/blob/master/types/bellatrix/block.yaml>`
    closely following beaconcha.in slot overview.
    """

    # SEE: https://github.com/ethereum/consensus-specs/blob/v1.2.0/specs/bellatrix/beacon-chain.md  # noqa: E501
    # SEE: https://notes.ethereum.org/@vbuterin/SkeyEI3xv (old) for terminology
    # SEE: https://notes.ethereum.org/@djrtwo/Bkn3zpwxB

    randao_reveal: Any  # Bytes96
    eth1_data: Eth1Data  # Eth1 data vote
    graffiti: Any = EMPTY_BYTES32  # Bytes32 (arbitrary data)
    num_proposer_slashings: int = 0
    num_attester_slashings: int = 0
    num_attestations: int = 0
    num_deposits: int = 0
    num_voluntary_exits: int = 0
    sync_aggregate: Optional[SyncAggregate] = None  # NOTE: pre-merge has no sync agg
    execution_payload: Optional[BeaconExecutionPayload] = None  # NOTE: pre-merge has no payload

    @validator("randao_reveal", "graffiti", pre=True)
    def convert_hexbytes(cls, value):
        if value and isinstance(value, get_args(BytesLike)):
            return HexBytes(value)

        return value

    @validator("randao_reveal", "graffiti", pre=True)
    def validate_hexbytes(cls, value):
        # NOTE: pydantic treats these values as bytes and throws an error
        if value and not isinstance(value, HexBytes):
            raise ValueError(f"Hash `{value}` is not a valid Hexbytes.")

        return value

    # TODO: cached_property decordted functions for fetching more detail on num_* fields
