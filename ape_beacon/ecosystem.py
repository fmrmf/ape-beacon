from typing import Any, Dict, Optional, cast

from ape.api.config import PluginConfig
from ape.api.networks import LOCAL_NETWORK_NAME
from ape.utils import EMPTY_BYTES32, BaseInterfaceModel
from ape_ethereum.ecosystem import Ethereum, NetworkConfig
from hexbytes import HexBytes
from pydantic import Field, root_validator, validator

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


class BeaconBlock(BaseInterfaceModel):
    """
    Class for representing a consensus layer block.

    Implements the
    `Beacon block <https://github.com/ethereum/beacon-APIs/blob/master/types/bellatrix/block.yaml>`
    """

    # TODO: check for Optional/None values when pending status
    slot: Optional[int] = None
    proposer_index: Optional[int] = None
    parent_root: Any = Field(EMPTY_BYTES32)  # genesis block has no parent root?
    state_root: Optional[Any] = None
    body: BeaconBlockBody

    @root_validator(pre=True)
    def convert_parent_hash(cls, data):
        parent_root = data.get("parent_root") or EMPTY_BYTES32
        data["parent_root"] = parent_root
        return data

    @validator("state_root", "parent_root", pre=True)
    def validate_hexbytes(cls, value):
        # NOTE: pydantic treats these values as bytes and throws an error
        if value and not isinstance(value, HexBytes):
            raise ValueError(f"Hash `{value}` is not a valid Hexbytes.")


class Beacon(Ethereum):
    @property
    def config(self) -> BeaconConfig:  # type: ignore
        return cast(BeaconConfig, self.config_manager.get_config("beacon"))

    # TODO: make sure BeaconProvider parses signed block response into this input data format  # noqa: E501
    # TODO: is there a clean method already with ape ecosystem for ethereum or in Web3Provider? will need one for input data dict to beacon block decode  # noqa: E501
    def decode_block(self, data: Dict) -> BeaconBlock:
        """
        Decodes consensus layer block with possible execution layer
        payload.
        """
        # decode EL block separately from CL
        payload_data = data["body"].pop("execution_payload", None)
        payload = super().decode_block(payload_data) if payload_data else None

        # parse without EL payload then set payload
        block = BeaconBlock.parse_obj(data)
        block.body.execution_payload = payload
        return block
