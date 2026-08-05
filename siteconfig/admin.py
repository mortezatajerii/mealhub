from django.contrib import admin
from .models import SiteSettings, MenuItem

# Register your models here.


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("SEO", {"fields": ("site_title", "meta_description")}),
        ("Branding", {"fields": ("favicon", "logo_header", "logo_footer")}),
        ("Footer", {"fields": ("footer_copyright",)}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "order", "show_in_desktop", "show_in_mobile")
    list_editable = ("is_active", "order", "show_in_desktop", "show_in_mobile")
    list_filter = ("is_active", "show_in_desktop", "show_in_mobile")
    search_fields = ("title", "url")
