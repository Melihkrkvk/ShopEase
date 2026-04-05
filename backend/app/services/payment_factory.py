import logging
import uuid
from abc import ABC, abstractmethod

from app.core.config import settings

logger = logging.getLogger(__name__)


class PaymentResult:
    """
    Represents the outcome of a payment processing attempt.

    Attributes:
        success (bool): Whether the payment succeeded.
        transaction_id (str): Unique identifier for this transaction.
        message (str): Human-readable status message.
    """

    def __init__(self, success: bool, transaction_id: str, message: str) -> None:
        """
        Initialize a PaymentResult.

        Args:
            success (bool): Whether the payment succeeded.
            transaction_id (str): Unique identifier for this transaction.
            message (str): Human-readable status message.
        """
        self.success = success
        self.transaction_id = transaction_id
        self.message = message

    def __bool__(self) -> bool:
        """Allow using PaymentResult directly in boolean context."""
        return self.success


class PaymentProvider(ABC):
    """
    Abstract base class for all payment providers.

    Defines the interface that every payment method must implement.
    """

    @abstractmethod
    def process(self, amount: float) -> PaymentResult:
        """
        Process a payment for the given amount.

        Args:
            amount (float): The total amount to charge.

        Returns:
            PaymentResult: The result of the payment attempt.

        Raises:
            ValueError: If the amount is not positive.
        """
        ...

    def _validate_amount(self, amount: float) -> None:
        """
        Validate that the payment amount is positive.

        Args:
            amount (float): The amount to validate.

        Raises:
            ValueError: If amount is zero or negative.
        """
        if amount <= 0:
            raise ValueError(f"Payment amount must be positive, got {amount}")


class CreditCardPayment(PaymentProvider):
    """
    Payment provider that simulates credit card transactions.

    Generates a transaction ID and logs the charge attempt.
    Rejects amounts above the configured credit card limit.
    """

    @property
    def _MAX_AMOUNT(self) -> float:
        """Return the configured credit card transaction limit."""
        return settings.credit_card_max_amount

    def process(self, amount: float) -> PaymentResult:
        """
        Process a credit card payment.

        Args:
            amount (float): The total amount to charge in USD.

        Returns:
            PaymentResult: Success with transaction ID, or failure if limit exceeded.

        Raises:
            ValueError: If amount is not positive.
        """
        self._validate_amount(amount)
        transaction_id = f"CC-{uuid.uuid4().hex[:12].upper()}"

        if amount > self._MAX_AMOUNT:
            logger.warning(
                "Credit card charge rejected — amount $%.2f exceeds limit $%.2f | txn=%s",
                amount, self._MAX_AMOUNT, transaction_id,
            )
            return PaymentResult(
                success=False,
                transaction_id=transaction_id,
                message=f"Charge of ${amount:.2f} exceeds single-transaction limit of ${self._MAX_AMOUNT:.2f}",
            )

        logger.info(
            "Credit card charge approved — $%.2f | txn=%s",
            amount, transaction_id,
        )
        return PaymentResult(
            success=True,
            transaction_id=transaction_id,
            message=f"Credit card charge of ${amount:.2f} approved",
        )


class PayPalPayment(PaymentProvider):
    """
    Payment provider that simulates PayPal transactions.

    Generates a transaction ID and logs the payment attempt.
    Rejects amounts above the configured PayPal account limit.
    """

    @property
    def _MAX_AMOUNT(self) -> float:
        """Return the configured PayPal transaction limit."""
        return settings.paypal_max_amount

    def process(self, amount: float) -> PaymentResult:
        """
        Process a PayPal payment.

        Args:
            amount (float): The total amount to charge in USD.

        Returns:
            PaymentResult: Success with transaction ID, or failure if limit exceeded.

        Raises:
            ValueError: If amount is not positive.
        """
        self._validate_amount(amount)
        transaction_id = f"PP-{uuid.uuid4().hex[:12].upper()}"

        if amount > self._MAX_AMOUNT:
            logger.warning(
                "PayPal payment rejected — amount $%.2f exceeds limit $%.2f | txn=%s",
                amount, self._MAX_AMOUNT, transaction_id,
            )
            return PaymentResult(
                success=False,
                transaction_id=transaction_id,
                message=f"PayPal payment of ${amount:.2f} exceeds account limit of ${self._MAX_AMOUNT:.2f}",
            )

        logger.info(
            "PayPal payment approved — $%.2f | txn=%s",
            amount, transaction_id,
        )
        return PaymentResult(
            success=True,
            transaction_id=transaction_id,
            message=f"PayPal payment of ${amount:.2f} approved",
        )


class PaymentFactory:
    """
    Factory for creating PaymentProvider instances.

    Uses the Factory Method pattern to return the correct provider subclass
    based on a string key.

    Attributes:
        _providers (dict): Maps payment method keys to provider classes.
    """

    def __init__(self) -> None:
        """Initialize the factory with all registered payment providers."""
        self._providers: dict[str, type[PaymentProvider]] = {
            "credit_card": CreditCardPayment,
            "paypal": PayPalPayment,
        }

    def create(self, method: str) -> PaymentProvider:
        """
        Instantiate and return the PaymentProvider for the given method key.

        Args:
            method (str): The payment method key (e.g. 'credit_card', 'paypal').

        Returns:
            PaymentProvider: An instance of the corresponding payment provider.

        Raises:
            ValueError: If the method key is not registered.
        """
        if method not in self._providers:
            raise ValueError(f"Unknown payment method: '{method}'")
        return self._providers[method]()

    def get_available_payment_methods(self) -> list[str]:
        """Return all registered payment method keys."""
        return list(self._providers.keys())
