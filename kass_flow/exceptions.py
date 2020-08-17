from typing import Any


class Error(Exception):
    """General error exception to be extended

    Attributes:
        message -- explanation of the error
        value -- value to be printed
    """

    def __init__(self, value: Any, message: str) -> None:
        self.message = message
        self.value = value

        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.value} -> {self.message}"


class KassResponseTimeoutError(Error):
    pass


class KassResponseDataError(Error):
    pass


class KassMissingTokenError(Error):
    pass
