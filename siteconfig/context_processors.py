from .models import SiteSettings, MenuItem


def site_settings(request):
    return {"site_settings": SiteSettings.objects.first()}


def site_menu(request):
    return {
        "desktop_menu_items": MenuItem.objects.filter(
            is_active=True,
            show_in_desktop=True,
        ).order_by("order"),
        "mobile_menu_items": MenuItem.objects.filter(
            is_active=True,
            show_in_mobile=True,
        ).order_by("order"),
    }
