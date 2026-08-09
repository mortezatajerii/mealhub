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
    search_fields = ("items__name", "date")
    autocomplete_fields = ("food_items",)
    date_hierarchy = "date"
