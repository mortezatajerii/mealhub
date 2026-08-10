from django.contrib import admin
from .models import Wallet, Transaction


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = [
        "organization",
        "balance",
        "reserved_balance",
        "available_balance",
        "created_at",
    ]
    list_filter = ["created_at"]
    search_fields = ["organization__name"]
    readonly_fields = ["created_at", "updated_at"]

    def available_balance(self, obj):
        return obj.available_balance

    available_balance.short_description = "موجودی قابل استفاده"


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "wallet",
        "transaction_type",
        "status",
        "amount",
        "reference_id",
        "created_at",
    ]
    list_filter = ["transaction_type", "status", "created_at"]
    search_fields = ["wallet__organization__name", "reference_id"]
    readonly_fields = ["created_at"]

    def has_add_permission(self, request):
        # Transactions should only be created through services
        return False

    def has_delete_permission(self, request, obj=None):
        # Never delete transactions
        return False
