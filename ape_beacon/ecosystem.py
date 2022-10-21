from typing import Dict, Optional, cast

from ape.api.config import PluginConfig
from ape.api.networks import LOCAL_NETWORK_NAME
from ape.api.providers import BlockAPI
from ape_ethereum.ecosystem import Ethereum, NetworkConfig

from ape_beacon.containers import BeaconBlockBody

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
    # TODO: is there a clean method already with ape ecosystem for ethereum or in Web3Provider? will need one for input data dict to beacon block decode  # noqa: E501
    def decode_block(self, data: Dict) -> BlockAPI:
        """
        Decodes consensus layer block with possible execution layer
        payload.
        """
        # decode EL block separately from CL
        payload_data = data["body"].pop("execution_payload", None)
        payload = super().decode_block(payload_data) if payload_data else None

        # map CL roots to BlockAPI hashes
        if "parent_root" in data:
            data["parent_hash"] = data.pop("parent_root")
        if "state_root" in data:
            data["hash"] = data.pop("state_root")

        # use data from EL if can (block in a block post-merge)
        if payload is not None:
            data["timestamp"] = payload.timestamp
            data["size"] = payload.size
        else:
            data["timestamp"] = 0
            data["size"] = 0

        # parse without EL payload then set payload
        block = BeaconBlock.parse_obj(data)
        block.body.execution_payload = payload
        return block
