from typing import Any, Optional

from ape_ethereum.ecosystem import Block
from pydantic import BaseModel

# TODO: use container with py-ssz https://github.com/ethereum/py-ssz?


class BeaconBlockBody(BaseModel):
    """
    Class for representing a consensus layer block body.

    Implements the
    `Beacon block body
    <https://github.com/ethereum/beacon-APIs/blob/master/types/bellatrix/block.yaml>`
    """

    # TODO: the below attributes
    randao_reveal: Any  # Bytes96 to hexbytes?
    # eth1_data: Eth1Data  # Eth1 data vote
    graffiti: Any  # Bytes32 Arbitrary data to hexbytes?
    # Operations
    # proposer_slashings: List[ProposerSlashing, MAX_PROPOSER_SLASHINGS]
    # attester_slashings: List[AttesterSlashing, MAX_ATTESTER_SLASHINGS]
    # attestations: List[Attestation, MAX_ATTESTATIONS]
    # deposits: List[Deposit, MAX_DEPOSITS]
    # voluntary_exits: List[SignedVoluntaryExit, MAX_VOLUNTARY_EXITS]
    # sync_aggregate: SyncAggregate
    # Execution
    execution_payload: Optional[Block] = None  # NOTE: pre-merge body does not have EL payload

    # TODO: decode_body() given prev_randao key in execution payload
    # SEE: https://github.com/ethereum/consensus-specs/blob/dev/specs/bellatrix/beacon-chain.md#executionpayload  # noqa: E501
