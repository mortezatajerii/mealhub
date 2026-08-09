from datetime import date

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from accounts.permissions import IsAdminRole

from .models import Reservation
from .serializers import ReservationSerializer
from .services import create_weekly_reservations


def _is_past_cutoff():
    # Thursday=3, Friday=4 → after Wednesday cutoff
    return date.today().weekday() in (3, 4)


class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "patch", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Reservation.objects.select_related("daily_menu", "food_item", "user")
        return Reservation.objects.filter(user=user).select_related(
            "daily_menu", "food_item"
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_finalized:
            raise PermissionDenied("رزرو نهایی شده و قابل تغییر نیست.")
        if _is_past_cutoff() and not request.user.is_staff:
            raise PermissionDenied("مهلت تغییر رزرو تا چهارشنبه است.")
        if instance.user != request.user and not request.user.is_staff:
            raise PermissionDenied()
        return super().partial_update(request, *args, **kwargs)

    @action(detail=False, methods=["post"], permission_classes=[IsAdminRole])
    def generate_week(self, request):
        created = create_weekly_reservations()
        return Response({"created": created})
