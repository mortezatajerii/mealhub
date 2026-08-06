import re
import random
from django.conf import settings
from django.core.cache import cache
from django.utils.crypto import constant_time_compare
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Role
from .serializers import UserSerializer, MeSerializer
from .permissions import role_required
from .services import send_otp_sms, SMSError


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [
        role_required(
            Role.SUPER_ADMIN,
            Role.OPERATIONS_MANAGER,
            Role.COMPANY_OWNER,
            Role.DEPARTMENT_ADMIN,
        )
    ]

    def get_queryset(self):
        user = self.request.user
        if user.role in (Role.SUPER_ADMIN, Role.OPERATIONS_MANAGER):
            return User.objects.all()
        if user.role == Role.COMPANY_OWNER:
            return User.objects.filter(organization=user.organization)
        if user.role == Role.DEPARTMENT_ADMIN and user.department_id:
            return User.objects.filter(department=user.department)
        return User.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if user.role in (Role.SUPER_ADMIN, Role.OPERATIONS_MANAGER):
            # Platform admins choose org/department from input
            serializer.save()
        elif user.role == Role.COMPANY_OWNER:
            # Org is forced, department comes from input
            serializer.save(organization=user.organization)
        else:
            # DEPARTMENT_ADMIN: both forced
            serializer.save(
                organization=user.organization,
                department=user.department,
            )



class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(MeSerializer(request.user).data)

    def patch(self, request):
        serializer = MeSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class SendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get("phone_number")
        PHONE_RE = re.compile(r"^09\d{9}$")
        if not phone or not PHONE_RE.match(phone):
            return Response({"detail": "Valid phone_number required."}, status=400)

        if cache.get(f"otp:{phone}"):
            return Response(
                {"detail": "OTP already sent. Try again later."}, status=429
            )

        code = str(random.randint(100000, 999999))

        if not cache.add(f"otp:{phone}", code, timeout=settings.OTP_TTL_SECONDS):
            return Response(
                {"detail": "OTP already sent. Try again later."}, status=429
            )

        try:
            send_otp_sms(phone, code)
        except SMSError:
            cache.delete(f"otp:{phone}")
            return Response({"detail": "Failed to send OTP."}, status=502)

        return Response({"detail": "OTP sent."})


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get("phone_number")
        code = request.data.get("code")

        if not phone or not code:
            return Response({"detail": "phone_number and code required."}, status=400)

        # Brute force protection
        attempts_key = f"otp_attempts:{phone}"
        attempts = cache.get(attempts_key, 0)
        if attempts >= 5:
            return Response(
                {"detail": "Too many attempts. Request a new OTP."}, status=429
            )

        cached = cache.get(f"otp:{phone}")
        if not cached or not constant_time_compare(cached, str(code)):
            cache.set(attempts_key, attempts + 1, timeout=settings.OTP_TTL_SECONDS)
            return Response({"detail": "Invalid or expired OTP."}, status=400)

        cache.delete(f"otp:{phone}")
        cache.delete(attempts_key)
        user, created = User.objects.get_or_create(
            phone_number=phone,
            defaults={"role": Role.EMPLOYEE},
        )
        refresh = RefreshToken.for_user(user)
        return Response({"refresh": str(refresh), "access": str(refresh.access_token)})
