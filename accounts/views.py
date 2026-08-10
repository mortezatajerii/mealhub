# import re
# import random
# from django.conf import settings
# from django.core.cache import cache
from django.utils.crypto import constant_time_compare
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import authenticate

from .models import User
from .serializers import UserSerializer, MeSerializer, RegisterSerializer
from .permissions import HasPermission, Perm, Scope, get_user_scope

# from .services import send_otp_sms, SMSError

Role = User.Role


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [HasPermission]

    permission_map = {
        "list": Perm.EMPLOYEE_VIEW,
        "retrieve": Perm.EMPLOYEE_VIEW,
        "create": Perm.EMPLOYEE_CREATE,
        "update": Perm.EMPLOYEE_MANAGE,
        "partial_update": Perm.EMPLOYEE_MANAGE,
        "destroy": Perm.EMPLOYEE_MANAGE,
        "default": Perm.EMPLOYEE_VIEW,
    }

    def get_queryset(self):
        user = self.request.user
        scope = get_user_scope(user)

        if scope == Scope.PLATFORM:
            return User.objects.all()

        if scope == Scope.ORGANIZATION:
            return User.objects.filter(organization=user.organization)

        if scope == Scope.DEPARTMENT:
            return User.objects.filter(department=user.department)

        return User.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        scope = get_user_scope(user)

        if scope == Scope.PLATFORM:
            serializer.save()

        elif scope == Scope.ORGANIZATION:
            if not user.organization_id:
                raise PermissionDenied("سازمان شما مشخص نیست.")

            serializer.save(organization=user.organization)

        elif scope == Scope.DEPARTMENT:
            if not user.organization_id or not user.department_id:
                raise PermissionDenied("سازمان یا واحد شما مشخص نیست.")

            serializer.save(
                organization=user.organization,
                department=user.department,
            )

        else:
            raise PermissionDenied("اجازه ساخت کاربر را ندارید.")


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(MeSerializer(request.user).data)

    def patch(self, request):
        serializer = MeSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get("phone_number")
        password = request.data.get("password")

        if not phone or not password:
            return Response(
                {"detail": "شماره موبایل و رمز عبور الزامی است."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=phone, password=password)

        if user is None:
            return Response(
                {"detail": "اطلاعات ورود نادرست است."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"detail": "حساب کاربری شما غیرفعال است."},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": MeSerializer(
                    user
                ).data,  # ارسال اطلاعات کاربر در همان لاگین برای فرانت‌اند
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "توکن رفرش ارسال نشده است."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "با موفقیت خارج شدید."}, status=status.HTTP_205_RESET_CONTENT
            )
        except TokenError:
            return Response(
                {"detail": "توکن نامعتبر است یا قبلاً باطل شده است."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


# class SendOTPView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         phone = request.data.get("phone_number")
#         PHONE_RE = re.compile(r"^09\d{9}$")
#         if not phone or not PHONE_RE.match(phone):
#             return Response({"detail": "Valid phone_number required."}, status=400)

#         if cache.get(f"otp:{phone}"):
#             return Response(
#                 {"detail": "OTP already sent. Try again later."}, status=429
#             )

#         code = str(random.randint(100000, 999999))

#         if not cache.add(f"otp:{phone}", code, timeout=settings.OTP_TTL_SECONDS):
#             return Response(
#                 {"detail": "OTP already sent. Try again later."}, status=429
#             )

#         try:
#             send_otp_sms(phone, code)
#         except SMSError:
#             cache.delete(f"otp:{phone}")
#             return Response({"detail": "Failed to send OTP."}, status=502)

#         return Response({"detail": "OTP sent."})


# class VerifyOTPView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         phone = request.data.get("phone_number")
#         code = request.data.get("code")

#         if not phone or not code:
#             return Response({"detail": "phone_number and code required."}, status=400)

#         # Brute force protection
#         attempts_key = f"otp_attempts:{phone}"
#         attempts = cache.get(attempts_key, 0)
#         if attempts >= 5:
#             return Response(
#                 {"detail": "Too many attempts. Request a new OTP."}, status=429
#             )

#         cached = cache.get(f"otp:{phone}")
#         if not cached or not constant_time_compare(cached, str(code)):
#             cache.set(attempts_key, attempts + 1, timeout=settings.OTP_TTL_SECONDS)
#             return Response({"detail": "Invalid or expired OTP."}, status=400)

#         cache.delete(f"otp:{phone}")
#         cache.delete(attempts_key)
#         user, created = User.objects.get_or_create(
#             phone_number=phone,
#             defaults={"role": Role.EMPLOYEE},
#         )
#         refresh = RefreshToken.for_user(user)
#         return Response({"refresh": str(refresh), "access": str(refresh.access_token)})
