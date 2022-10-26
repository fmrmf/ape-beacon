from typing import Dict, Optional, cast

from ape.api import PluginConfig
from ape.api.networks import LOCAL_NETWORK_NAME
from ape.api.providers import BlockAPI
from ape_ethereum.ecosystem import Ethereum

from ape_beacon.containers import BeaconBlockBody, BeaconExecutionPayload

from .types import attempt_to_hexbytes

NETWORKS = {
    # chain_id, network_id
    "mainnet": (1, 1),
    "goerli": (5, 5),
}


class NetworkConfig(PluginConfig):
    required_confirmations: int = 0
    default_provider: Optional[str] = "lighthouse"
    block_time: int = 0


def _create_local_config(default_provider: Optional[str] = None, **kwargs) -> NetworkConfig:
    return _create_config(required_confirmations=0, default_provider=default_provider, **kwargs)


def _create_config(required_confirmations: int = 2, **kwargs) -> NetworkConfig:
    # Put in own method to isolate `type: ignore` comments
    return NetworkConfig(required_confirmations=required_confirmations, **kwargs)


class BeaconConfig(PluginConfig):
    mainnet: NetworkConfig = _create_config(block_time=12)
    goerli: NetworkConfig = _create_config(block_time=12)
    local: NetworkConfig = _create_local_config(default_provider="test")
    default_network: str = LOCAL_NETWORK_NAME


class BeaconBlock(BlockAPI):
    """
    Class for representing a consensus layer block.

    Implements the
    `Beacon block <https://github.com/ethereum/beacon-APIs/blob/master/types/bellatrix/block.yaml>`
    """

    proposer_index: Optional[int] = None
    body: BeaconBlockBody


class Beacon(Ethereum):
    name: str = "beacon"

    @property
    def config(self) -> BeaconConfig:  # type: ignore
        return cast(BeaconConfig, self.config_manager.get_config("beacon"))

    def decode_block(self, data: Dict) -> BlockAPI:
        """
        Decodes consensus layer block with possible execution layer
        payload.
        """
        # map CL (slot, roots) to ape BlockAPI (number, hashes)
        if "slot" in data:
            data["number"] = data.pop("slot")
        if "parent_root" in data:
            data["parent_hash"] = attempt_to_hexbytes(data.pop("parent_root"))
        if "state_root" in data:
            data["hash"] = attempt_to_hexbytes(data.pop("state_root"))

        # init beacon block timestamp and size so doesnt throw validation error if no payload
        data["timestamp"] = 0
        data["size"] = 0

        # use data from EL if can (block within a block post-merge)
        payload = None
        if "body" in data:
            # limit data retained at block level for beacon operations
            if "proposer_slashings" in data["body"]:
                data["body"]["num_proposer_slashings"] = len(data["body"].pop("proposer_slashings"))
            if "attester_slashings" in data["body"]:
                data["body"]["num_attester_slashings"] = len(data["body"].pop("attester_slashings"))
            if "attestations" in data["body"]:
                data["body"]["num_attestations"] = len(data["body"].pop("attestations"))
            if "deposits" in data["body"]:
                data["body"]["num_deposits"] = len(data["body"].pop("deposits"))
            if "voluntary_exits" in data["body"]:
                data["body"]["num_voluntary_exits"] = len(data["body"].pop("voluntary_exits"))

            payload_data = data["body"].pop("execution_payload", None)
            if payload_data is not None:
                payload_data["size"] = 0  # TODO: infer size from gas limit

                # convert from beacon API spec to an Ape BlockAPI for block in block
                if "timestamp" in payload_data:
                    data["timestamp"] = payload_data["timestamp"]
                if "block_number" in payload_data:
                    payload_data["number"] = payload_data.pop("block_number")
                if "block_hash" in payload_data:
                    payload_data["hash"] = attempt_to_hexbytes(payload_data.pop("block_hash"))
                if "parent_hash" in payload_data:
                    payload_data["parent_hash"] = attempt_to_hexbytes(
                        payload_data.pop("parent_hash")
                    )

                # decode EL block separately from CL
                prev_randao = payload_data.pop("prev_randao", None)
                payload_data = super().decode_block(payload_data).dict()
                if prev_randao is not None:
                    payload_data.update({"prev_randao": prev_randao})
                payload = BeaconExecutionPayload.parse_obj(payload_data)

        # parse without EL payload then set payload
        block = BeaconBlock.parse_obj(data)
        block.body.execution_payload = payload
        return block
