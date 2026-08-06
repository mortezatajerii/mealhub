# accounts/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("شماره موبایل الزامی است")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.SUPER_ADMIN)
        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        # platform rolls
        SUPER_ADMIN = "super_admin", "مدیر کل"
        PLATFORM_MANAGER = "platform_manager", "مدیر عملیات"
        MENU_MANAGER = "menu_manager", "مسئول منو"
        ACCOUNT_MANAGER = "account_manager", "پشتیبانی مشتریان"
        RESTAURANT_MANAGER = "restaurant_manager", "مسئول رستوران"
        FINANCE = "finance", "مسئول مالی"
        # customer rolls
        COMPANY_OWNER = "company_owner", "مدیر شرکت"
        DEPARTMENT_ADMIN = "department_admin", "مسئول واحد"
        EMPLOYEE = "employee", "کارمند"

    username = None
    phone_number = models.CharField("شماره موبایل", max_length=11, unique=True)
    role = models.CharField(
        "نقش", max_length=30, choices=Role.choices, default=Role.EMPLOYEE
    )

    # Only organization users not us
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="users",
        verbose_name="شرکت",
    )
    department = models.ForeignKey(
        "organizations.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
        verbose_name="واحد",
    )

    is_phone_verified = models.BooleanField("تأیید شماره موبایل", default=False)
    created_at = models.DateTimeField("تاریخ ثبت", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین تغییر", auto_now=True)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []
    objects = UserManager()

    PLATFORM_ROLES = {
        Role.SUPER_ADMIN,
        Role.PLATFORM_MANAGER,
        Role.MENU_MANAGER,
        Role.ACCOUNT_MANAGER,
        Role.RESTAURANT_MANAGER,
        Role.FINANCE,
    }

    @property
    def is_platform_user(self):
        return self.role in self.PLATFORM_ROLES

    def clean(self):
        super().clean()
        if not self.is_platform_user and self.organization_id is None:
            raise ValidationError("لطفاً شرکت این کاربر را مشخص کنید.")
        if self.is_platform_user and self.organization_id is not None:
            raise ValidationError("کاربر تیم پلتفرم نباید به شرکتی وصل باشد.")

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(
        "تصویر پروفایل", upload_to="avatars/", blank=True, null=True
    )
    national_code = models.CharField("کد ملی", max_length=10, blank=True)
    birth_date = models.DateField("تاریخ تولد", blank=True, null=True)
    address = models.TextField("آدرس", blank=True)

    def __str__(self):
        return f"پروفایل {self.user.phone_number}"


class OtpCode(models.Model):
    phone_number = models.CharField(max_length=11)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=["phone_number", "code"])]
