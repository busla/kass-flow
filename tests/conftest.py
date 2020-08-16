# TODO: enable decorator typing in mypy when released
# TODO: figure out how to get code completion from conftest fixtures
import pytest
from kass_flow import kass


@pytest.fixture  # type: ignore
def get_kass_url() -> str:
    return "https://api.testing.kass.is/v1/payments"


@pytest.fixture  # type: ignore
def get_kass_token_test() -> str:
    return "kass_test_auth_token"


@pytest.fixture  # type: ignore
def get_kass_token_from_api_docs() -> str:
    return "um2JjfnJbEUJnCpjKiV94jqp"


@pytest.fixture  # type: ignore
def kass_callback_response() -> kass.KassCallbackPaymentDict:
    payload: kass.KassCallbackPaymentDict = {
        "payment_id": "3e6975e8-77cb-48b7-7722-3dfe47677bbc",
        "transaction_id": "a917be59-f35a-478f-a5d9-19bf467972ad",
        "amount": 2199,
        "status": "paid",
        "order": "abc123",
        "completed": 1458748422,
        "signature": "8022cb71924dba2e24f849fdc83596e80a3966465f6b3f1702326afa31229b11",
    }
    return payload


@pytest.fixture  # type: ignore
def kass_payload_valid() -> kass.KassRequestPaymentDict:
    payload: kass.KassRequestPaymentDict = {
        "amount": 2199,
        "description": "Kass bolur",
        "image_url": "https://photos.kassapi.is/kass/kass-bolur.jpg",
        "order": "ABC123",
        "recipient": "7728440",
        "terminal": 1,
        "expires_in": 90,
        "notify_url": "https://example.com/callbacks/kass",
    }
    return payload


@pytest.fixture  # type: ignore
def kass_payload_invalid_recipient() -> kass.KassRequestPaymentDict:
    payload: kass.KassRequestPaymentDict = {
        "amount": 2199,
        "description": "Kass bolur",
        "image_url": "https://photos.kassapi.is/kass/kass-bolur.jpg",
        "order": "ABC123",
        "recipient": "7798217",
        "terminal": 1,
        "expires_in": 90,
        "notify_url": "https://example.com/callbacks/kass",
    }
    return payload


@pytest.fixture  # type: ignore
def kass_instance(get_kass_token_test: str, get_kass_url: str) -> kass.KassBilling:
    kass_token = get_kass_token_test
    kass_url = get_kass_url
    instance = kass.KassBilling(kass_token, kass_url)
    return instance


@pytest.fixture  # type: ignore
def kass_instance_with_token_from_api_docs(
    get_kass_token_from_api_docs: str, get_kass_url: str
) -> kass.KassBilling:
    kass_token = get_kass_token_from_api_docs
    kass_url = get_kass_url
    instance = kass.KassBilling(kass_token, kass_url)
    return instance


@pytest.fixture  # type: ignore
def kass_instance_with_token(
    kass_instance: kass.KassBilling, kass_payload_valid: kass.KassRequestPaymentDict
) -> kass.KassBilling:
    _ = kass_instance.create_payment_token(kass_payload_valid)
    return kass_instance

