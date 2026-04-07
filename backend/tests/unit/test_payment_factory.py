import pytest

from app.services.payment_factory import PaymentFactory


@pytest.fixture
def factory():
    return PaymentFactory()


def test_payment_factory_creates_credit_card_provider(factory):
    """PaymentFactory returns a CreditCardPayment for 'credit_card'."""
    from app.services.payment_factory import CreditCardPayment
    provider = factory.create("credit_card")
    assert isinstance(provider, CreditCardPayment)


def test_payment_factory_creates_paypal_provider(factory):
    """PaymentFactory returns a PayPalPayment for 'paypal'."""
    from app.services.payment_factory import PayPalPayment
    provider = factory.create("paypal")
    assert isinstance(provider, PayPalPayment)


def test_payment_factory_with_invalid_method_raises_value_error(factory):
    """PaymentFactory raises ValueError for an unknown payment method."""
    with pytest.raises(ValueError, match="Unknown payment method"):
        factory.create("bitcoin")


def test_credit_card_process_succeeds_for_valid_amount(factory):
    """CreditCardPayment.process returns a successful result for a valid amount."""
    provider = factory.create("credit_card")
    result = provider.process(amount=99.99)
    assert result.success is True
    assert result.transaction_id.startswith("CC-")
    assert "approved" in result.message


def test_paypal_process_succeeds_for_valid_amount(factory):
    """PayPalPayment.process returns a successful result for a valid amount."""
    provider = factory.create("paypal")
    result = provider.process(amount=49.99)
    assert result.success is True
    assert result.transaction_id.startswith("PP-")
    assert "approved" in result.message


def test_credit_card_process_fails_above_limit(factory):
    """CreditCardPayment.process returns failure when amount exceeds $10,000."""
    provider = factory.create("credit_card")
    result = provider.process(amount=10_001.0)
    assert result.success is False
    assert result.transaction_id.startswith("CC-")


def test_paypal_process_fails_above_limit(factory):
    """PayPalPayment.process returns failure when amount exceeds $5,000."""
    provider = factory.create("paypal")
    result = provider.process(amount=5_001.0)
    assert result.success is False
    assert result.transaction_id.startswith("PP-")


def test_payment_process_with_zero_amount_raises_value_error(factory):
    """process raises ValueError when amount is zero."""
    provider = factory.create("credit_card")
    with pytest.raises(ValueError, match="positive"):
        provider.process(amount=0)


def test_get_available_payment_methods_returns_all_keys(factory):
    """get_available_payment_methods lists all registered keys."""
    methods = factory.get_available_payment_methods()
    assert "credit_card" in methods
    assert "paypal" in methods
