from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from accounts.permissions import HasPermission, Perm, get_user_scope, Scope
from organizations.models import Organization
from .models import Wallet, Transaction
from .serializers import (
    WalletSerializer,
    TransactionSerializer,
    DepositSerializer,
)
from .services import deposit


class WalletViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing wallets.
    - Platform roles see all wallets
    - Organization users see only their own wallet
    """

    serializer_class = WalletSerializer
    permission_classes = [HasPermission]
    permission_map = {
        "list": Perm.WALLET_CREDIT,
        "retrieve": Perm.WALLET_CREDIT,
        "deposit": Perm.WALLET_CREDIT,
    }

    def get_queryset(self):
        user = self.request.user
        scope = get_user_scope(user)

        if scope == Scope.PLATFORM:
            return Wallet.objects.select_related("organization").all()

        # Organization users see only their wallet
        if user.organization_id:
            return Wallet.objects.filter(
                organization_id=user.organization_id
            ).select_related("organization")

        return Wallet.objects.none()

    @action(detail=False, methods=["post"])
    def deposit(self, request):
        """
        Deposit funds into an organization's wallet.
        Only FINANCE and PLATFORM_MANAGER can use this.
        """
        serializer = DepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        organization = get_object_or_404(
            Organization, pk=serializer.validated_data["organization"]
        )
        amount = serializer.validated_data["amount"]
        description = serializer.validated_data.get("description", "")

        transaction = deposit(
            organization=organization,
            amount=amount,
            performed_by=request.user,
            description=description,
        )

        return Response(
            TransactionSerializer(transaction).data,
            status=status.HTTP_201_CREATED,
        )


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing transactions.
    - Platform roles see all transactions
    - Organization users see only their organization's transactions
    """

    serializer_class = TransactionSerializer
    permission_classes = [HasPermission]
    permission_map = {
        "list": Perm.WALLET_CREDIT,
        "retrieve": Perm.WALLET_CREDIT,
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        scope = get_user_scope(user)

        if scope == Scope.PLATFORM:
            return queryset.all()
        if scope == Scope.ORGANIZATION and user.organization_id:
            return queryset.filter(wallet__organization_id=user.organization_id)
        return queryset.none()
