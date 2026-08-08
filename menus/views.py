from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend

from accounts.permissions import HasPermission, Perm
from .models import DailyMenu, FoodItem
from .serializers import DailyMenuSerializer, FoodItemSerializer
from .utils import get_next_week_range, is_menu_editable


class FoodItemViewSet(viewsets.ModelViewSet):
    queryset = FoodItem.objects.all()
    serializer_class = FoodItemSerializer
    permission_classes = [HasPermission]
    filter_backends = [SearchFilter]
    search_fields = ["name"]
    permission_map = {
        "list": Perm.MENU_VIEW,
        "retrieve": Perm.MENU_VIEW,
        "create": Perm.MENU_MANAGE,
        "update": Perm.MENU_MANAGE,
        "partial_update": Perm.MENU_MANAGE,
        "destroy": Perm.MENU_MANAGE,
    }


class DailyMenuViewSet(viewsets.ModelViewSet):
    serializer_class = DailyMenuSerializer
    permission_classes = [HasPermission]
    filter_backends = []
    permission_map = {
        "list": Perm.MENU_VIEW,
        "retrieve": Perm.MENU_VIEW,
        "create": Perm.MENU_MANAGE,
        "update": Perm.MENU_MANAGE,
        "partial_update": Perm.MENU_MANAGE,
        "destroy": Perm.MENU_MANAGE,
    }

    def get_queryset(self):
        qs = DailyMenu.objects.prefetch_related("items").order_by("date")

        if self.request.user.has_perm_key(Perm.MENU_MANAGE):
            return qs

        start, end = get_next_week_range()
        return qs.filter(date__range=(start, end))

    def perform_destroy(self, instance):
        if not is_menu_editable(instance.date):
            raise ValidationError(
                "حذف منو فقط برای هفته آینده و تا پایان چهارشنبه مجاز است."
            )
        instance.delete()
