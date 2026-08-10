from django.db import transaction

from .models import Wallet, Transaction


class WalletError(Exception):
    """Base exception for wallet operations."""


class InsufficientBalanceError(WalletError):
    """Raised when available balance cannot cover the requested amount."""


class InvalidAmountError(WalletError):
    """Raised when amount is zero or negative."""


def _validate_amount(amount):
    if amount is None or amount <= 0:
        raise InvalidAmountError("Amount must be a positive value.")


def _locked_wallet(organization):
    """Fetch wallet with row-level lock. Must be called inside atomic block."""
    wallet, _ = Wallet.objects.select_for_update().get_or_create(
        organization=organization
    )
    return wallet


def deposit(*, organization, amount, performed_by=None, description=""):
    """Credit the wallet. Used by FINANCE / PLATFORM_MANAGER roles."""
    _validate_amount(amount)
    with transaction.atomic():
        wallet = _locked_wallet(organization)
        wallet.balance += amount
        wallet.save(update_fields=["balance", "updated_at"])
        return Transaction.objects.create(
            wallet=wallet,
            transaction_type=Transaction.Type.CREDIT,
            status=Transaction.Status.COMPLETED,
            amount=amount,
            performed_by=performed_by,
            description=description,
        )


def reserve_balance(*, organization, amount, reservation):
    """Hold funds for a reservation. Called from reservations/services.py."""
    _validate_amount(amount)
    with transaction.atomic():
        wallet = _locked_wallet(organization)
        if wallet.available_balance < amount:
            raise InsufficientBalanceError(
                f"Available balance {wallet.available_balance} < {amount}"
            )
        wallet.reserved_balance += amount
        wallet.save(update_fields=["reserved_balance", "updated_at"])
        return Transaction.objects.create(
            wallet=wallet,
            transaction_type=Transaction.Type.RESERVE,
            status=Transaction.Status.COMPLETED,
            amount=amount,
            reference_id=f"reservation_{reservation.pk}",
        )


def release_balance(*, organization, amount, reservation):
    """Release held funds when a reservation is cancelled."""
    _validate_amount(amount)
    with transaction.atomic():
        wallet = _locked_wallet(organization)
        if wallet.reserved_balance < amount:
            raise WalletError("Release amount exceeds reserved balance.")
        wallet.reserved_balance -= amount
        wallet.save(update_fields=["reserved_balance", "updated_at"])
        return Transaction.objects.create(
            wallet=wallet,
            transaction_type=Transaction.Type.RELEASE,
            status=Transaction.Status.COMPLETED,
            amount=amount,
            reference_id=f"reservation_{reservation.pk}",
        )


def settle_reservation(*, organization, amount, reservation):
    """Convert a hold into a real debit when the meal is served/finalized."""
    _validate_amount(amount)
    with transaction.atomic():
        wallet = _locked_wallet(organization)
        if wallet.reserved_balance < amount:
            raise WalletError("Settle amount exceeds reserved balance.")
        wallet.reserved_balance -= amount
        wallet.balance -= amount
        wallet.save(update_fields=["balance", "reserved_balance", "updated_at"])
        return Transaction.objects.create(
            wallet=wallet,
            transaction_type=Transaction.Type.DEBIT,
            status=Transaction.Status.COMPLETED,
            amount=amount,
            reference_id=f"reservation_{reservation.pk}",
        )
