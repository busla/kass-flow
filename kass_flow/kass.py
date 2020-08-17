from typing import TypedDict, Union, Any, Dict, Tuple, Literal, Type, Optional
import logging
import hmac
from json import JSONDecodeError
import hashlib
from abc import ABC, abstractmethod
import requests
from requests.exceptions import Timeout
from requests.auth import HTTPBasicAuth
from kass_flow.exceptions import (
    KassResponseDataError,
    KassResponseTimeoutError,
    KassMissingTokenError,
)
from kass_flow.interfaces import (
    KassCallbackPaymentDict,
    KassPaymentResponseDict,
    KassRequestPaymentDict,
    KassBillingPaymentResults,
)

logger = logging.getLogger("kass")


class KassBillingBase(ABC):
    def __init__(
        self,
        kass_token: Optional[str] = None,
        kass_url: str = "https://api.kass.is/v1/payments",
    ):
        if not kass_token:
            raise KassMissingTokenError(
                kass_token, f"Kass token cannot be {kass_token}"
            )
        self.kass_token: str = kass_token
        self.kass_url: str = kass_url
        self.kass_request_timeout: int = 5
        self._payment_token: Optional[str] = None

    @property
    def token(self) -> str:
        return self._payment_token

    def create_signature(self, data: KassCallbackPaymentDict) -> str:

        msg = "{}&{}&{}&{}&{}&{}".format(
            data["payment_id"],
            data["transaction_id"],
            data["order"],
            data["amount"],
            data["status"],
            data["completed"],
        )
        signature = hmac.new(
            bytes(self.kass_token, "utf-8"),
            msg=bytes(msg, "utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()
        return signature

    def is_signature_valid(self, res: KassCallbackPaymentDict) -> bool:
        signature = self.create_signature(res)
        return signature == res["signature"]

    def _send_payment_request(
        self, payload: KassRequestPaymentDict
    ) -> Tuple[KassBillingPaymentResults, bool]:
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

    def dispatch(
        self, payload: KassRequestPaymentDict
    ) -> Tuple[KassBillingPaymentResults, bool]:
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


class KassBilling(KassBillingBase):
    def create_payment_token(self, payload: KassRequestPaymentDict) -> str:
        if not self._payment_token:
            self._payment_token = self._sign(
                order_no=payload["order"],
                mobile=payload["recipient"],
                total=payload["amount"],
            )
        return self._payment_token
