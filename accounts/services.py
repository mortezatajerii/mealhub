import logging
import time
import uuid
import requests
from django.conf import settings

SMSIR_VERIFY_URL = "https://api.sms.ir/v1/send/verify"

logger = logging.getLogger(__name__)


class SMSError(Exception):
    pass


def mask_phone(phone: str) -> str:
    if len(phone) >= 5:
        return phone[:3] + "***" + phone[-2:]
    return phone


def send_otp_sms(phone_number: str, code: str) -> None:

    request_id = str(uuid.uuid4())
    start_time = time.time()
    masked_phone = mask_phone(phone_number)

    logger.info(
        "OTP send started",
        extra={
            "request_id": request_id,
            "phone": masked_phone,
            "template_id": settings.SMSIR_TEMPLATE_ID,
            "event": "otp_send_start",
        },
    )

    """Send OTP code via sms.ir verify (template-based) endpoint."""
    payload = {
        "mobile": phone_number,
        "templateId": settings.SMSIR_TEMPLATE_ID,
        "parameters": [
            {"name": "CODE", "value": code},
        ],
    }
    headers = {
        "x-api-key": settings.SMSIR_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    try:
        response = requests.post(
            SMSIR_VERIFY_URL, json=payload, headers=headers, timeout=10
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        duration_ms = (time.time() - start_time) * 1000
        # Failing log
        logger.error(
            "OTP send failed due to network/HTTP error",
            extra={
                "request_id": request_id,
                "phone": masked_phone,
                "error": str(exc),
                "duration_ms": duration_ms,
                "event": "otp_send_failure",
            },
        )
        raise SMSError(f"SMS provider error: {exc}") from exc

    duration_ms = (time.time() - start_time) * 1000

    try:
        data = response.json()
    except ValueError as exc:
        raise SMSError("Invalid response from SMS provider") from exc

    status = data.get("status")
    message = data.get("message")

    if status != 1:
        logger.error(
            "OTP send failed with non-success status",
            extra={
                "request_id": request_id,
                "phone": masked_phone,
                "status": status,
                "provider_message": message,
                "duration_ms": duration_ms,
                "event": "otp_send_failure",
            },
        )
        raise SMSError(f"SMS send failed: {message}")

    # Success log
    logger.info(
        "OTP send succeeded",
        extra={
            "request_id": request_id,
            "phone": masked_phone,
            "status": status,
            "duration_ms": duration_ms,
            "event": "otp_send_success",
        },
    )
