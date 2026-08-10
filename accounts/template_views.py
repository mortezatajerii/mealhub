# mealhub/accounts/template_views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import TemplateView
from django.contrib import messages

from .forms import LoginForm, RegisterForm, ProfileForm, UserUpdateForm
from .models import Profile


class LoginTemplateView(View):

    template_name = "accounts/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("accounts:dashboard")

        form = LoginForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if not form.cleaned_data.get("remember_me"):
                request.session.set_expiry(0)

            messages.success(
                request,
                f"خوش آمدید، {user.get_full_name() or user.phone_number}",
            )

            next_url = request.GET.get("next") or request.POST.get("next")

            if next_url:
                return redirect(next_url)

            return redirect("accounts:dashboard")

        return render(request, self.template_name, {"form": form})


class RegisterTemplateView(View):

    template_name = "accounts/register.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("accounts:dashboard")

        form = RegisterForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "حساب کاربری شما با موفقیت ایجاد شد.")
            return redirect("accounts:dashboard")

        return render(request, self.template_name, {"form": form})


class DashboardTemplateView(LoginRequiredMixin, TemplateView):

    template_name = "accounts/dashboard.html"
    login_url = "/accounts/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wallet = getattr(self.request.user, "wallet", None)
        context["wallet"] = wallet
        context["transactions"] = wallet.transactions.all()[:10] if wallet else []
        user = self.request.user

        try:
            profile = user.profile
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=user)

        context["user"] = user
        context["profile"] = profile

        context["organization"] = user.organization
        context["department"] = user.department
        context["role_display"] = user.get_role_display()

        return context


# class ProfileUpdateView(LoginRequiredMixin, View):
#     template_name = "accounts/profile_edit.html"
#     login_url = "/accounts/login/"

#     def get(self, request):
#         user = request.user

#         profile, created = Profile.objects.get_or_create(user=user)

#         user_form = UserUpdateForm(instance=user)
#         profile_form = ProfileForm(instance=profile)

#         return render(
#             request,
#             self.template_name,
#             {"user_form": user_form, "profile_form": profile_form},
#         )

#     def post(self, request):
#         user = request.user
#         profile = user.profile

#         user_form = UserUpdateForm(request.POST, instance=user)
#         profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

#         if user_form.is_valid() and profile_form.is_valid():
#             user_form.save()
#             profile_form.save()
#             messages.success(request, "اطلاعات پروفایل شما با موفقیت به‌روزرسانی شد.")
#             return redirect("accounts:dashboard")

#         return render(
#             request,
#             self.template_name,
#             {"user_form": user_form, "profile_form": profile_form},
#         )


class LogoutTemplateView(View):
    def post(self, request):
        logout(request)
        messages.info(request, "شما با موفقیت از سیستم خارج شدید.")
        return redirect("accounts:login")
