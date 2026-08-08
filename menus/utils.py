from datetime import timedelta
from django.utils import timezone

# Python weekday(): Monday=0 ... Saturday=5
SATURDAY = 5
EDIT_CUTOFF_OFFSET = 4


def days_into_week(date):
    return (date.weekday() - SATURDAY) % 7


def get_week_start(date):
    return date - timedelta(days=days_into_week(date))


def get_next_week_range(today=None):
    # ? Shanbeh to Jome
    today = today or timezone.localdate()
    start = get_week_start(today) + timedelta(days=7)
    return start, start + timedelta(days=6)


def is_menu_editable(menu_date, today=None):
    if menu_date is None:
        return False
    today = today or timezone.localdate()
    start, end = get_next_week_range(today)
    return start <= menu_date <= end and days_into_week(today) <= EDIT_CUTOFF_OFFSET
