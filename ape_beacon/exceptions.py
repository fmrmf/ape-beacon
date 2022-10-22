from ape.exceptions import ProviderError


class ValidatorNotFoundError(ProviderError):
    """
    Raised when unable to find a validator
    """

    def __init__(self, validator_address: str):
        super().__init__(f"Validator address '{validator_address}' not found.")
