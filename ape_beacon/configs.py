from typing import Optional

from ape.api import PluginConfig
from ape.api.networks import LOCAL_NETWORK_NAME
from pydantic import Extra


class NetworkConfig(PluginConfig):
    required_confirmations: int = 0
    block_time: int = 0

    class Config:
        extra = Extra.allow


def _create_local_config(default_provider: Optional[str] = None, **kwargs) -> NetworkConfig:
    return _create_config(required_confirmations=0, **kwargs)


def _create_config(required_confirmations: int = 2, **kwargs) -> NetworkConfig:
    # Put in own method to isolate `type: ignore` comments
    return NetworkConfig(required_confirmations=required_confirmations, **kwargs)


class BeaconConfig(PluginConfig):
    mainnet: NetworkConfig = _create_config(block_time=12)
    goerli: NetworkConfig = _create_config(block_time=12)
    local: NetworkConfig = _create_local_config()
    default_network: str = LOCAL_NETWORK_NAME
