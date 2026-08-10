from django.db import models
from django.conf import settings

from organizations.models import Organization
from menus.models import DailyMenu, FoodItem


class Reservation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reservations"
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.PROTECT, related_name="reservations"
    )
    daily_menu = models.ForeignKey(
        DailyMenu, on_delete=models.PROTECT, related_name="reservations"
    )
    food_item = models.ForeignKey(
        FoodItem, on_delete=models.PROTECT, related_name="reservations"
    )
    price_snapshot = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    is_finalized = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "daily_menu")
