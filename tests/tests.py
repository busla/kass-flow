import pytest
from kass_flow import kass


def test_kass_instance(kass_instance: kass.KassBilling) -> None:
    assert kass_instance.kass_token == "kass_test_auth_token"
    return None


def test_kass_token_not_empty(
    kass_instance: kass.KassBilling, kass_payload_valid: kass.KassRequestPaymentDict
) -> None:
    token = kass_instance.create_payment_token(kass_payload_valid)
    assert token != ""
    return None


def test_kass_has_token_property(
    kass_instance: kass.KassBilling, kass_payload_valid: kass.KassRequestPaymentDict
) -> None:
    token = kass_instance.create_payment_token(kass_payload_valid)
    assert token == kass_instance.token
    return None


def test_kass_response_success(
    kass_instance: kass.KassBilling, kass_payload_valid: kass.KassRequestPaymentDict
) -> None:
    result, is_success = kass_instance.dispatch(kass_payload_valid)
    assert is_success is True
    assert not result["received"]["error"]
    assert result["received"]["success"] is True
    return None


def test_kass_response_error(
    kass_instance: kass.KassBilling,
    kass_payload_invalid_recipient: kass.KassRequestPaymentDict,
) -> None:
    result, is_success = kass_instance.dispatch(kass_payload_invalid_recipient)
    print(result)
    assert is_success is False
    assert result["received"]["error"]
    assert result["received"]["success"] is False
    return None


@pytest.mark.skip(
    reason="We need an actual callback from KASS to test this"
)  # type: ignore
def test_kass_signature(
    kass_instance_with_token_from_api_docs: kass.KassBilling,
    kass_callback_response: kass.KassCallbackPaymentDict,
) -> None:
    # instance = kass.KassBilling(get_kass_token_from_api_docs,)
    instance = kass_instance_with_token_from_api_docs
    is_valid = instance.is_signature_valid(kass_callback_response, instance.token)
    assert is_valid is True
