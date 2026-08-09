from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    search_fields = ["phone_number", "first_name", "last_name", "email"]
    ordering = ["phone_number"]