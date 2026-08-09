from django.contrib import admin

from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "organization",
        "daily_menu",
        "food_item",
        "is_finalized",
        "created_at",
    )

    list_filter = (
        "is_finalized",
        "organization",
        "daily_menu__date",
    )

    search_fields = (
        "user__phone_number",
        "user__first_name",
        "user__last_name",
        "organization__name",
        "food_item__name",
    )

    autocomplete_fields = (
        "user",
        "daily_menu",
        "food_item",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    date_hierarchy = "created_at"

    ordering = ("-created_at",)
