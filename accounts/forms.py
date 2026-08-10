from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from .models import User, Profile


class UserCreationForm(forms.ModelForm):
    """فرم ایجاد کاربر جدید توسط ادمین"""

    password1 = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "حداقل 8 کاراکتر"}
        ),
        min_length=8,
    )
    password2 = forms.CharField(
        label="تکرار رمز عبور",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "رمز عبور را دوباره وارد کنید",
                "autocomplete": "new-password",
            }
        ),
    )

    class Meta:
        model = User
        fields = (
            "phone_number",
            "first_name",
            "last_name",
            "role",
            "organization",
            "department",
        )
        widgets = {
            "phone_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "09123456789"}
            ),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-control"}),
            "organization": forms.Select(attrs={"class": "form-control"}),
            "department": forms.Select(attrs={"class": "form-control"}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("رمزهای عبور مطابقت ندارند.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """فرم ویرایش کاربر توسط ادمین"""

    password = ReadOnlyPasswordHashField(
        label="رمز عبور",
        help_text="برای تغییر رمز عبور از <a href='../password/'>این لینک</a> استفاده کنید.",
    )

    class Meta:
        model = User
        fields = (
            "phone_number",
            "password",
            "first_name",
            "last_name",
            "role",
            "organization",
            "department",
            "is_active",
            "is_staff",
            "is_phone_verified",
        )


class LoginForm(forms.Form):
    """فرم ورود به سیستم"""

    phone_number = forms.CharField(
        label="شماره موبایل",
        max_length=11,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "مثلاً 09123456789",
                "autocomplete": "tel",
                "inputmode": "numeric",
            }
        ),
        validators=[
            RegexValidator(
                regex=r"^09\d{9}$",
                message="شماره موبایل معتبر نیست. فرمت صحیح: 09123456789",
            )
        ],
    )
    password = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "رمز عبور خود را وارد کنید",
                "autocomplete": "new-password",
            }
        ),
    )
    remember_me = forms.BooleanField(
        label="مرا به خاطر بسپار",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        phone_number = cleaned_data.get("phone_number")
        password = cleaned_data.get("password")

        if phone_number and password:
            self.user_cache = authenticate(
                self.request, username=phone_number, password=password
            )
            if self.user_cache is None:
                raise ValidationError("شماره موبایل یا رمز عبور اشتباه است.")
            if not self.user_cache.is_active:
                raise ValidationError("این حساب کاربری غیرفعال است.")

        return cleaned_data

    def get_user(self):
        return self.user_cache


class RegisterForm(forms.Form):
    """فرم ثبت‌نام کاربر جدید"""

    phone_number = forms.CharField(
        label="شماره موبایل",
        max_length=11,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "09123456789",
                "autocomplete": "tel",
            }
        ),
        validators=[
            RegexValidator(
                regex=r"^09\d{9}$",
                message="شماره موبایل معتبر نیست. فرمت صحیح: 09123456789",
            )
        ],
    )
    first_name = forms.CharField(
        label="نام",
        max_length=30,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "نام",
                "autocomplete": "given-name",
            }
        ),
    )
    last_name = forms.CharField(
        label="نام خانوادگی",
        max_length=30,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "نام خانوادگی",
                "autocomplete": "family-name",
            }
        ),
    )
    password = forms.CharField(
        label="رمز عبور",
        min_length=8,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "حداقل 8 کاراکتر",
                "autocomplete": "new-password",
            }
        ),
    )
    password2 = forms.CharField(
        label="تأیید رمز عبور",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "تکرار رمز عبور",
                "autocomplete": "new-password",
            }
        ),
    )

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if User.objects.filter(phone_number=phone_number).exists():
            raise ValidationError("این شماره موبایل قبلاً ثبت شده است.")
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password2 and password != password2:
            raise ValidationError({"password2": "رمزهای عبور مطابقت ندارند."})

        return cleaned_data

    def save(self):
        user = User.objects.create_user(
            phone_number=self.cleaned_data["phone_number"],
            password=self.cleaned_data["password"],
            first_name=self.cleaned_data.get("first_name", ""),
            last_name=self.cleaned_data.get("last_name", ""),
        )
        return user


class ProfileForm(forms.ModelForm):
    """فرم ویرایش پروفایل کاربر"""

    class Meta:
        model = Profile
        fields = ("avatar", "national_code", "birth_date", "address")
        widgets = {
            "avatar": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "national_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "کد ملی 10 رقمی",
                    "maxlength": "10",
                }
            ),
            "birth_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "address": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "آدرس کامل"}
            ),
        }
        labels = {
            "avatar": "تصویر پروفایل",
            "national_code": "کد ملی",
            "birth_date": "تاریخ تولد",
            "address": "آدرس",
        }

    def clean_national_code(self):
        national_code = self.cleaned_data.get("national_code")
        if national_code and not national_code.isdigit():
            raise ValidationError("کد ملی باید فقط شامل اعداد باشد.")
        if national_code and len(national_code) != 10:
            raise ValidationError("کد ملی باید 10 رقم باشد.")
        return national_code


class UserUpdateForm(forms.ModelForm):
    """فرم ویرایش اطلاعات پایه کاربر"""

    class Meta:
        model = User
        fields = ("first_name", "last_name")
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "نام"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "نام خانوادگی"}
            ),
        }
        labels = {"first_name": "نام", "last_name": "نام خانوادگی"}
