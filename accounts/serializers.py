from rest_framework import serializers
from .models import User, Role

ROLE_PRIORITY = {
    Role.SUPER_ADMIN: 100,
    Role.OPERATIONS_MANAGER: 90,
    Role.MENU_MANAGER: 70,
    Role.ACCOUNT_MANAGER: 70,
    Role.RESTAURANT_MANAGER: 70,
    Role.FINANCE: 70,
    Role.COMPANY_OWNER: 60,
    Role.DEPARTMENT_ADMIN: 50,
    Role.EMPLOYEE: 10,
}


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "phone_number",
            "full_name",
            "role",
            "organization",
            "department",
        ]
        read_only_fields = ["organization", "department"]  # از ورودی گرفته نشه

    def validate_role(self, value):
        request = self.context.get("request")
        current = request.user

        # Can't upscaled own privileges
        if self.instance and self.instance.pk == current.pk:
            raise serializers.ValidationError("You cannot change your own role.")

        current_priority = ROLE_PRIORITY.get(current.role, 0)
        value_priority = ROLE_PRIORITY.get(value, 999)

        # Only lower privileges
        if value_priority >= current_priority:
            raise serializers.ValidationError(
                "Cannot assign a role equal or higher than yours."
            )

        return value

    def validate_department(self, value):
        request = self.context["request"]
        user = request.user
        if user.role == Role.COMPANY_OWNER and value is not None:
            if value.organization_id != user.organization_id:
                raise serializers.ValidationError(
                    "Department does not belong to your organization."
                )
        return value


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "phone_number",
            "full_name",
            "role",
            "organization",
            "department",
        ]
        read_only_fields = ["phone_number", "role", "organization", "department"]
