from rest_framework import serializers
from .models import Wallet, Transaction


class WalletSerializer(serializers.ModelSerializer):
    available_balance = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )

    class Meta:
        model = Wallet
        fields = [
            "id",
            "organization",
            "organization_name",
            "balance",
            "reserved_balance",
            "available_balance",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["balance", "reserved_balance", "created_at", "updated_at"]


class TransactionSerializer(serializers.ModelSerializer):
    wallet_organization = serializers.CharField(
        source="wallet.organization.name", read_only=True
    )
    performed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            "id",
            "wallet",
            "wallet_organization",
            "transaction_type",
            "status",
            "amount",
            "reference_id",
            "performed_by",
            "performed_by_name",
            "description",
            "created_at",
        ]
        read_only_fields = [
            "status",
            "created_at",
        ]

    def get_performed_by_name(self, obj):
        if obj.performed_by:
            return (
                f"{obj.performed_by.first_name} {obj.performed_by.last_name}".strip()
                or obj.performed_by.phone_number
            )
        return None


class DepositSerializer(serializers.Serializer):
    organization = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    description = serializers.CharField(
        max_length=500, required=False, allow_blank=True
    )

    def validate_organization(self, value):
        from organizations.models import Organization

        if not Organization.objects.filter(pk=value).exists():
            raise serializers.ValidationError("سازمان مورد نظر یافت نشد.")
        return value
