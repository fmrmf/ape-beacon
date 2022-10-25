from ape import plugins
from ape.api.networks import LOCAL_NETWORK_NAME, NetworkAPI, create_network_type

from .configs import BeaconConfig, LighthouseNetworkConfig
from .ecosystem import NETWORKS, Beacon
from .providers import Lighthouse


@plugins.register(plugins.Config)
def config_class():
    return BeaconConfig


@plugins.register(plugins.EcosystemPlugin)
def ecosystems():
    yield Beacon


@plugins.register(plugins.NetworkPlugin)
def networks():
    for network_name, network_params in NETWORKS.items():
        yield "beacon", network_name, create_network_type(*network_params)

    # NOTE: This works for local providers, as they get chain_id from themselves
    yield "beacon", LOCAL_NETWORK_NAME, NetworkAPI


@plugins.register(plugins.ProviderPlugin)
def providers():
    for network_name in LighthouseNetworkConfig().dict():
        yield "beacon", network_name, Lighthouse
