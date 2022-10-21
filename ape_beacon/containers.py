from typing import Any, Optional

from ape.api.providers import BlockAPI
from hexbytes import HexBytes
from pydantic import BaseModel, validator


class BeaconExecutionPayload(BlockAPI):
    prev_randao: Any

    @validator("hash", "parent_hash", "prev_randao", pre=True)
    def validate_hexbytes(cls, value):
        # NOTE: pydantic treats these values as bytes and throws an error
        if value and not isinstance(value, HexBytes):
            raise ValueError(f"Hash `{value}` is not a valid Hexbytes.")

        return value


class BeaconBlockBody(BaseModel):
    """
    Class for representing a consensus layer block body.

    Implements the
    `Beacon block body
    <https://github.com/ethereum/beacon-APIs/blob/master/types/bellatrix/block.yaml>`
    """

    randao_reveal: Any  # Bytes96
    # eth1_data: Eth1Data  # Eth1 data vote
    graffiti: Any  # Bytes32
    # Operations
    # proposer_slashings: List[ProposerSlashing, MAX_PROPOSER_SLASHINGS]
    # attester_slashings: List[AttesterSlashing, MAX_ATTESTER_SLASHINGS]
    # attestations: List[Attestation, MAX_ATTESTATIONS]
    # deposits: List[Deposit, MAX_DEPOSITS]
    # voluntary_exits: List[SignedVoluntaryExit, MAX_VOLUNTARY_EXITS]
    # sync_aggregate: SyncAggregate
    execution_payload: Optional[BeaconExecutionPayload] = None  # NOTE: pre-merge has no payload

    # SEE: https://github.com/ethereum/consensus-specs/blob/dev/specs/bellatrix/beacon-chain.md#executionpayload  # noqa: E501
