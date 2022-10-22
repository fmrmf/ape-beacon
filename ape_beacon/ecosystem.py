from typing import Dict, Optional, cast

from ape.api.config import PluginConfig
from ape.api.networks import LOCAL_NETWORK_NAME
from ape.api.providers import BlockAPI
from ape_ethereum.ecosystem import Ethereum, NetworkConfig

from ape_beacon.containers import BeaconBlockBody, BeaconExecutionPayload

NETWORKS = {
    # chain_id, network_id
    "mainnet": (1, 1),
    "goerli": (5, 5),
}


def _create_network_config(
    required_confirmations: int = 7, block_time: int = 12, **kwargs
) -> NetworkConfig:
    # Helper method to isolate `type: ignore` comments.
    return NetworkConfig(
        required_confirmations=required_confirmations, block_time=block_time, **kwargs
    )  # type: ignore


def _create_local_config(default_provider: Optional[str] = None) -> NetworkConfig:
    return _create_network_config(
        required_confirmations=0, block_time=0, default_provider=default_provider
    )


class BeaconConfig(PluginConfig):
    mainnet: NetworkConfig = _create_network_config()
    local: NetworkConfig = _create_network_config(default_provider="test")
    default_network: str = LOCAL_NETWORK_NAME


class BeaconBlock(BlockAPI):
    """
    Class for representing a consensus layer block.

    Implements the
    `Beacon block <https://github.com/ethereum/beacon-APIs/blob/master/types/bellatrix/block.yaml>`
    """

    slot: Optional[int] = None
    proposer_index: Optional[int] = None
    body: BeaconBlockBody


class Beacon(Ethereum):
    @property
    def config(self) -> BeaconConfig:  # type: ignore
        return cast(BeaconConfig, self.config_manager.get_config("beacon"))

    # TODO: make sure BeaconProvider parses signed block response into this input data format  # noqa: E501
    def decode_block(self, data: Dict) -> BlockAPI:
        """
        Decodes consensus layer block with possible execution layer
        payload.
        """
        # map CL roots to ape BlockAPI hashes (block within a block)
        if "parent_root" in data:
            data["parent_hash"] = data.pop("parent_root")
        if "state_root" in data:
            data["hash"] = data.pop("state_root")

        # limit data retained at block level for beacon operations
        if "proposer_slashings" in data:
            data["num_proposer_slashings"] = len(data["proposer_slashings"])
        if "attester_slashings" in data:
            data["num_attester_slashings"] = len(data["attester_slashings"])
        if "attestations" in data:
            data["num_attestations"] = len(data["attestations"])
        if "deposits" in data:
            data["num_deposits"] = len(data["deposits"])
        if "voluntary_exits" in data:
            data["num_voluntary_exits"] = len(data["voluntary_exits"])

        # init beacon block timestamp and size so doesnt throw validation error if no payload
        data["timestamp"] = 0
        data["size"] = 0

        # use data from EL if can (block in a block post-merge)
        payload = None
        payload_data = data["body"].pop("execution_payload", None)
        if payload_data is not None:
            data["number"] = payload_data["number"]
            data["timestamp"] = payload_data["timestamp"]
            data["size"] = payload_data["size"]

            # decode EL block separately from CL
            prev_randao = payload_data.pop("prev_randao")
            payload_data = super().decode_block(payload_data).dict()
            payload_data.update({"prev_randao": prev_randao})
            payload = BeaconExecutionPayload.parse_obj(payload_data)

        # parse without EL payload then set payload
        block = BeaconBlock.parse_obj(data)
        block.body.execution_payload = payload
        return block
