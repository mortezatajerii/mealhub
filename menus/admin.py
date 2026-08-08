from django.contrib import admin
from .models import DailyMenu, FoodItem


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price")
    search_fields = ("name",)


@admin.register(DailyMenu)
class DailyMenuAdmin(admin.ModelAdmin):
    list_display = ("id", "date")
    list_filter = ("date",)
    autocomplete_fields = ("items",)
    date_hierarchy = "date"
