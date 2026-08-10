# wallets/models.py
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Wallet(models.Model):
    organization = models.OneToOneField(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="wallet",
        verbose_name="سازمان",
    )
    balance = models.DecimalField(
        "موجودی",
        max_digits=12,
        decimal_places=0,
        default=0,
        validators=[MinValueValidator(Decimal("0"))],
    )
    reserved_balance = models.DecimalField(
        "موجودی رزرو شده",
        max_digits=12,
        decimal_places=0,
        default=0,
        validators=[MinValueValidator(Decimal("0"))],
    )
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("تاریخ بروزرسانی", auto_now=True)

    class Meta:
        verbose_name = "کیف پول"
        verbose_name_plural = "کیف پول‌ها"
        db_table = "wallets"

    def __str__(self):
        return f"{self.organization.name} - {self.balance:,} تومان"

    @property
    def available_balance(self):
        """موجودی قابل استفاده"""
        return self.balance - self.reserved_balance


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        CREDIT = "credit", "واریز"
        DEBIT = "debit", "برداشت"
        RESERVE = "reserve", "رزرو"
        RELEASE = "آزادسازی", "آزادسازی"

    class TransactionStatus(models.TextChoices):
        PENDING = "pending", "در انتظار"
        COMPLETED = "completed", "تکمیل شده"
        FAILED = "failed", "ناموفق"
        CANCELLED = "cancelled", "لغو شده"

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="کیف پول",
    )
    transaction_type = models.CharField(
        "نوع تراکنش", max_length=20, choices=TransactionType.choices
    )
    amount = models.DecimalField(
        "مبلغ",
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("0"))],
    )
    status = models.CharField(
        "وضعیت",
        max_length=20,
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING,
    )
    reference_id = models.CharField(
        "شناسه مرجع",
        max_length=100,
        blank=True,
        null=True,
        help_text="شناسه رزرواسیون یا سفارش مرتبط",
    )
    description = models.TextField("توضیحات", blank=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="wallet_transactions",
        verbose_name="ایجاد شده توسط",
    )
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("تاریخ بروزرسانی", auto_now=True)

    class Meta:
        verbose_name = "تراکنش"
        verbose_name_plural = "تراکنش‌ها"
        db_table = "wallet_transactions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["wallet", "-created_at"]),
            models.Index(fields=["reference_id"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount:,} تومان"
