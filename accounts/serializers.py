from rest_framework import serializers
from django.core.validators import RegexValidator
from .models import User

Role = User.Role

ROLE_PRIORITY = {
    Role.SUPER_ADMIN: 100,
    Role.PLATFORM_MANAGER: 90,
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


class RegisterSerializer(serializers.Serializer):

    phone_number = serializers.CharField(
        max_length=11,
        validators=[
            RegexValidator(regex=r"^09\d{9}$", message="شماره موبایل معتبر نیست.")
        ],
    )
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=30, required=False, default="")
    last_name = serializers.CharField(max_length=30, required=False, default="")

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("این شماره موبایل قبلاً ثبت شده است.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "رمزهای عبور مطابقت ندارند."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(
            phone_number=validated_data["phone_number"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user
