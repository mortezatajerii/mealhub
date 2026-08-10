import datetime
from django.contrib.auth import get_user_model
from django.db import transaction
from menus.models import DailyMenu
from wallets.services import reserve_balance, InsufficientBalanceError
from .models import Reservation

User = get_user_model()


def create_weekly_reservations():
    today = datetime.date.today()
    days_until_saturday = (5 - today.weekday()) % 7 or 7
    week_start = today + datetime.timedelta(days=days_until_saturday)
    week_end = week_start + datetime.timedelta(days=5)

    menus = DailyMenu.objects.filter(
        date__range=(week_start, week_end)
    ).prefetch_related("items")

    users = list(
        User.objects.filter(is_active=True, organization__isnull=False).select_related(
            "organization"
        )
    )

    results = {"created": 0, "skipped": 0, "insufficient": 0}

    for menu in menus:
        default_item = menu.items.first()
        if default_item is None:
            continue

        for user in users:
            with transaction.atomic():
                reservation, created = Reservation.objects.get_or_create(
                    user=user,
                    daily_menu=menu,
                    defaults={
                        "organization": user.organization,
                        "food_item": default_item,
                        "price_snapshot": default_item.price,
                    },
                )
                if not created:
                    results["skipped"] += 1
                    continue

                try:
                    reserve_balance(
                        organization=user.organization,
                        amount=default_item.price,
                        reservation=reservation,
                    )
                    results["created"] += 1
                except InsufficientBalanceError:
                    reservation.delete()
                    results["insufficient"] += 1


    return results
