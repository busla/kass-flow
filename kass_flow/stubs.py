from typing import TypedDict, Union, Any, Dict, Tuple, Literal, Type, Optional

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

