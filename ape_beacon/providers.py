from abc import ABC
from typing import Iterator, Optional

import requests
from ape.api.networks import LOCAL_NETWORK_NAME
from ape.api.providers import BlockAPI, ProviderAPI, UpstreamProvider
from ape.api.transactions import ReceiptAPI, TransactionAPI
from ape.exceptions import (
    APINotImplementedError,
    BlockNotFoundError,
    ProviderError,
    ProviderNotConnectedError,
)
from ape.logging import logger
from ape.types import BlockID, ContractLog, LogFilter
from ape.utils import cached_property
from eth_typing import HexStr
from hexbytes import HexBytes
from web3.beacon import Beacon
from yarl import URL

from ape_beacon.exceptions import ValidatorNotFoundError
from ape_beacon.types import convert_block_id

DEFAULT_SETTINGS = {"uri": "http://localhost:5052"}


class BeaconProvider(ProviderAPI, ABC):
    """
    A base provider mixin class that uses the
    `web3.py Beacon API
    <https://web3py.readthedocs.io/en/latest/web3.beacon.html>`__ python package.
    """

    # NOTE: Read only provider given web3.py Beacon API implementation

    _beacon: Optional[Beacon] = None
    _client_version: Optional[str] = None
    cached_chain_id: Optional[int] = None

    @property
    def beacon(self) -> Beacon:
        """
        Access to the ``beacon`` object as if you did ``Beacon(uri)``.
        """
        if not self._beacon:
            raise ProviderNotConnectedError()

        return self._beacon

    @cached_property
    def client_version(self) -> str:
        """
        As if you did ``Beacon(uri).get_version()``.
        """
        if not self._beacon:
            return ""

        # NOTE: Gets reset to `None` on `connect()` and `disconnect()`.
        if self._client_version is None:
            resp = self.beacon.get_version()
            if "data" not in resp or "version" not in resp["data"]:
                return ""

            self._client_version = resp["data"]["version"]

        return self._client_version

    @property
    def max_gas(self) -> int:
        raise APINotImplementedError("max_gas is not implemented by this provider.")

    @property
    def supports_tracing(self) -> bool:
        raise APINotImplementedError("supports_tracing is not implemented by this provider.")

    def estimate_gas_cost(self, txn: TransactionAPI, **kwargs) -> int:
        raise APINotImplementedError("estimate_gas_cost is not implemented by this provider.")

    @property
    def gas_price(self) -> int:
        raise APINotImplementedError("gas_price is not implemented by this provider.")

    def get_code(self, address: str) -> bytes:
        raise APINotImplementedError("get_code is not implemented by this provider.")

    def get_contract_logs(self, log_filter: LogFilter) -> Iterator[ContractLog]:
        raise APINotImplementedError("get_contract_logs is not implemented by this provider.")

    def get_nonce(self, address: str, **kwargs) -> int:
        raise APINotImplementedError("get_nonce is not implemented by this provider.")

    def get_receipt(self, txn_hash: str) -> ReceiptAPI:
        raise APINotImplementedError("get_receipt is not implemented by this provider.")

    def get_transactions_by_block(self, block_id: BlockID) -> Iterator[TransactionAPI]:
        raise APINotImplementedError(
            "get_transactions_by_block is not implemented by this provider."
        )

    def send_call(self, txn: TransactionAPI) -> bytes:
        raise APINotImplementedError("send_call is not implemented by this provider.")

    def send_transaction(self, txn: TransactionAPI) -> ReceiptAPI:
        raise APINotImplementedError("send_transaction is not implemented by this provider.")

    # TODO: add provider methods specific to beacon, with APIs for Attestations, Deposits etc.

    @property
    def is_connected(self) -> bool:
        if self._beacon is None:
            return False

        # treat as connected if node is fully synced or syncing
        status_code = self._beacon.get_health()
        return (
            status_code == requests.status_codes.codes.ok
            or status_code == requests.status_codes.codes.partial
        )

    def update_settings(self, new_settings: dict):
        self.disconnect()
        self.provider_settings.update(new_settings)
        self.connect()

    @property
    def chain_id(self) -> int:
        default_chain_id = None
        if self.network.name not in (
            "adhoc",
            LOCAL_NETWORK_NAME,
        ) and not self.network.name.endswith("-fork"):
            # If using a live network, the chain ID is hardcoded.
            default_chain_id = self.network.chain_id
        elif self.cached_chain_id is not None:
            return self.cached_chain_id  # TODO: test

        try:
            # use deposit contract endpoint for chain ID
            resp = self.beacon.get_deposit_contract()
            if "data" in resp and "chain_id" in resp["data"]:
                self.cached_chain_id = int(resp["data"]["chain_id"])
                return self.cached_chain_id

        except requests.exceptions.HTTPError:
            if default_chain_id is not None:
                return default_chain_id

            raise  # Original error

        if default_chain_id is not None:
            return default_chain_id

        raise ProviderNotConnectedError()

    def get_block(self, block_id: BlockID) -> BlockAPI:
        """
        As if you did ``Beacon(uri).get_block(block_id)``.
        """
        beacon_block_id = convert_block_id(block_id)
        if isinstance(beacon_block_id, HexBytes):
            beacon_block_id = HexStr(beacon_block_id.hex())

        try:
            resp = self.beacon.get_block(str(beacon_block_id))
            if "data" not in resp or "message" not in resp["data"]:
                raise BlockNotFoundError(block_id)
        except requests.exceptions.HTTPError as err:
            raise BlockNotFoundError(block_id) from err

        block_data = resp["data"]["message"]
        return self.network.ecosystem.decode_block(block_data)

    def get_balance(self, address: str) -> int:
        """
        Gets the validator balance for validator address or ID on beacon chain.
        """
        try:
            resp = self.beacon.get_validator(address)
            if "data" not in resp or "balance" not in resp["data"]:
                raise ValidatorNotFoundError(address)
        except requests.exceptions.HTTPError as err:
            raise ValidatorNotFoundError(address) from err

        balance = int(resp["data"]["balance"])
        return balance

    def block_ranges(self, start=0, stop=None, page=None):
        """
        Ranges over beacon chain slot number, which is effectively
        the block number for the consensus layer.
        """
        if stop is None:
            stop = self.chain_manager.blocks.height
        if page is None:
            page = self.block_page_size

        for start_block in range(start, stop + 1, page):
            stop_block = min(stop, start_block + page - 1)
            yield start_block, stop_block


# SEE: https://github.com/ApeWorX/ape/blob/main/src/ape_geth/provider.py#L147
class Lighthouse(BeaconProvider, UpstreamProvider):
    name: str = "lighthouse"

    @property
    def uri(self) -> str:
        if "uri" in self.provider_settings:
            # Use adhoc, scripted value
            return self.provider_settings["uri"]

        config = self.config.dict().get(self.network.ecosystem.name, None)
        if config is None:
            return DEFAULT_SETTINGS["uri"]

        # Use value from config file
        network_config = config.get(self.network.name)
        return network_config.get("uri", DEFAULT_SETTINGS["uri"])

    @property
    def _clean_uri(self) -> str:
        return str(URL(self.uri).with_user(None).with_password(None))

    @property
    def connection_str(self) -> str:
        return self.uri

    def connect(self):
        self._client_version = None  # Clear cached version when connecting to another URI.
        self._beacon = Beacon(self.uri)

        if not self.is_connected:
            # TODO: "ephemeral" lighthouse?
            raise ProviderError(f"No node found on '{self._clean_uri}'")
        elif "lighthouse" in self.client_version.lower():
            self._log_connection("Lighthouse")
            # TODO: self.concurrency = ...
            # TODO: self.block_page_size = ...
        elif "prysm" in self.client_version.lower():
            self._log_connection("Prysm")
            # TODO: self.concurrency = ...
            # TODO: self.block_page_size = ...
        elif "lodestar" in self.client_version.lower():
            self._log_connection("Lodestar")
            # TODO: self.concurrency = ...
            # TODO: self.block_page_size = ...
        elif "nimbus" in self.client_version.lower():
            self._log_connection("Nimbus")
            # TODO: self.concurrency = ...
            # TODO: self.block_page_size = ...
        elif "teku" in self.client_version.lower():
            self._log_connection("Teku")
            # TODO: self.concurrency = ...
            # TODO: self.block_page_size = ...
        else:
            client_name = self.client_version.split("/")[0]
            logger.warning(
                f"Connecting Lighthouse plugin to non-Lighthouse client '{client_name}'."
            )

        # Check for chain errors, including syncing
        try:
            # use deposit contract endpoint for chain ID
            resp = self._beacon.get_deposit_contract()
            chain_id = int(resp["data"]["chain_id"])
        except (requests.exceptions.HTTPError, KeyError) as err:
            raise ProviderError(
                err.args[0].get("message")
                if all((hasattr(err, "args"), err.args, isinstance(err.args[0], dict)))
                else "Error getting chain id."
            )

        self.network.verify_chain_id(chain_id)

    def disconnect(self):
        self._beacon = None
        self._client_version = None

    def _log_connection(self, client_name: str):
        logger.info(f"Connecting to existing {client_name} node at '{self._clean_uri}'.")
