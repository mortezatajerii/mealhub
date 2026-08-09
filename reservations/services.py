import datetime
from django.contrib.auth import get_user_model
from menus.models import DailyMenu, FoodItem
from .models import Reservation

User = get_user_model()


def create_weekly_reservations():
    today = datetime.date.today()
    days_until_saturday = (5 - today.weekday()) % 7 or 7
    week_start = today + datetime.timedelta(days=days_until_saturday)
    week_end = week_start + datetime.timedelta(days=5)

    menus = DailyMenu.objects.filter(date__range=(week_start, week_end))
    default_item = FoodItem.objects.first()

    for menu in menus:
        for user in User.objects.filter(is_active=True):
            Reservation.objects.get_or_create(
                user=user,
                daily_menu=menu,
                defaults={
                    "organization": user.organization,
                    "food_item": default_item,
                },
            )
