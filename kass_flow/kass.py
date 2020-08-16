from typing import TypedDict, Union, Any, Dict, Tuple, Literal, Type, Optional
import logging
import hmac
from json import JSONDecodeError
import hashlib
from abc import ABC, abstractmethod
import requests
from requests.exceptions import Timeout
from requests.auth import HTTPBasicAuth
from .exceptions import KassResponseDataError, KassResponseTimeoutError

logger = logging.getLogger("kass")


KassRequestPaymentDict = TypedDict(
    "KassRequestPaymentDict",
    {
        "amount": int,
        "description": str,
        "image_url": str,
        "recipient": str,
        "expires_in": int,
        "notify_url": str,
        "order": str,
        "terminal": int,
    },
)

KassResponsePaymentDict = TypedDict(
    "KassResponsePaymentDict",
    {
        "payment_id": str,
        "transaction_id": str,
        "amount": int,
        "status": str,
        "order": str,
        "completed": int,
        "signature": str,
    },
)

KassCallbackPaymentDict = TypedDict(
    "KassCallbackPaymentDict",
    {
        "payment_id": str,
        "transaction_id": str,
        "amount": int,
        "status": str,
        "order": str,
        "completed": int,
        "signature": str,
    },
)

KassErrorCodes = Literal[
    "merchant_not_found",
    "merchant_account_locked",
    "merchant_signature_incorrect",
    "recipient_not_found",
    "merchant_cannot_be_recipient",
    "payment_not_found",
    "payment_exceeds_limits",
    "invalid_data",
    "system_error",
]

KassErrorDict = TypedDict(
    "KassErrorDict",
    {"success": Literal[False], "code": str, "key": KassErrorCodes, "message": str},
)
KassSuccessDict = TypedDict(
    "KassSuccessDict", {"success": Literal[True], "id": str, "created": int}
)
KassPaymentResponseDict = TypedDict(
    "KassPaymentResponseDict",
    {"success": KassSuccessDict, "error": Optional[KassErrorDict]},
)


KassFlowResponseDict = TypedDict(
    "KassFlowResponseDict",
    {"submitted": KassRequestPaymentDict, "recieved": KassPaymentResponseDict},
)


class KassBillingBase(ABC):
    def __init__(self, kass_token: str, kass_url: str):
        self.kass_token = kass_token
        self.kass_url = kass_url
        self.kass_request_timeout: int = 5
        self._payment_token: str = ""

    @property
    def token(self) -> str:
        return self._payment_token

    def create_signature(self, data: KassCallbackPaymentDict, kass_token: str) -> str:
        msg = "{}&{}&{}&{}&{}&{}".format(
            data["payment_id"],
            data["transaction_id"],
            data["order"],
            data["amount"],
            data["status"],
            data["completed"],
        )
        signature = hmac.new(
            bytes(kass_token, "utf-8"),
            msg=bytes(msg, "utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()
        return signature

    def is_signature_valid(self, res: KassResponsePaymentDict, kass_token: str) -> bool:
        signature = self.create_signature(res, kass_token)
        return signature == res["signature"]

    def _send_payment_request(
        self, payload: KassRequestPaymentDict
    ) -> Tuple[Dict[str, Any], bool]:
        try:
            res: KassPaymentResponseDict = requests.post(
                self.kass_url,
                json=payload,
                auth=HTTPBasicAuth(self.kass_token, ""),
                timeout=self.kass_request_timeout,
            ).json()
        except Timeout:
            error_msg = f"{self.kass_url} did not respond within {self.kass_request_timeout} seconds."
            raise KassResponseTimeoutError(payload, error_msg)
        except JSONDecodeError:
            error_msg = f"Could not parse Kass response: {res}"
            raise KassResponseDataError(payload, error_msg)

        logger.debug(res)
        is_success = res.get("success") == True
        return {"received": res, "submitted": payload}, is_success

    @abstractmethod
    def create_payment_token(self, payload: KassRequestPaymentDict) -> str:
        return ""

    def dispatch(self, payload: KassRequestPaymentDict) -> Any:
        payment_token = self.create_payment_token(payload)
        invoice_data: KassRequestPaymentDict = {
            "order": payload["order"],
            "terminal": payload["terminal"],
            "amount": payload["amount"],
            "description": payload["description"],
            "image_url": payload["image_url"],
            "recipient": payload["recipient"],
            "expires_in": payload["expires_in"],
            "notify_url": f"{payload['expires_in']}/{payload['order']}/{payment_token}/",
        }
        result, is_success = self._send_payment_request(invoice_data)
        return result, is_success

    def _sign(self, **kwargs: Union[str, int]) -> str:
        msg = "&".join([str(v) for v in kwargs.values()])

        signature = hmac.new(
            bytes(self.kass_token, "utf-8"),
            msg=bytes(msg, "utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()
        return signature

    def notify(
        self,
        email_address: Union[str, None] = None,
        mobile_number: Union[str, None] = None,
    ) -> Any:
        raise NotImplementedError


class KassBilling(KassBillingBase):
    def create_payment_token(self, payload: KassRequestPaymentDict) -> str:
        if not self._payment_token:
            self._payment_token = self._sign(
                order_no=payload["order"],
                mobile=payload["recipient"],
                total=payload["amount"],
            )
        return self._payment_token
