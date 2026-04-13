from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
import hashlib
import hmac
from typing import Any

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
import requests

from .models import BillingOrder, BillingWebhookEvent, Subscription


MERCADOPAGO_API_BASE = "https://api.mercadopago.com"


@dataclass(slots=True)
class CheckoutSession:
    checkout_url: str
    sandbox_checkout_url: str
    provider_reference: str
    raw_response: dict[str, Any]


def get_billing_amount() -> Decimal:
    return Decimal(str(settings.PAID_PLAN_PRICE))


def get_per_use_amount() -> Decimal:
    return Decimal(str(settings.PER_USE_PRICE))


def build_frontend_return_url(status: str) -> str:
    return f"{settings.FRONTEND_BASE_URL}/plan?payment_status={status}"


def build_payment_methods_config() -> dict[str, Any]:
    excluded_types = [
        {"id": payment_type.strip()}
        for payment_type in settings.MERCADOPAGO_EXCLUDED_PAYMENT_TYPES.split(",")
        if payment_type.strip()
    ]
    excluded_methods = [
        {"id": method.strip()}
        for method in settings.MERCADOPAGO_EXCLUDED_PAYMENT_METHODS.split(",")
        if method.strip()
    ]
    config: dict[str, Any] = {
        "installments": settings.MERCADOPAGO_INSTALLMENTS,
    }
    if excluded_types:
        config["excluded_payment_types"] = excluded_types
    if excluded_methods:
        config["excluded_payment_methods"] = excluded_methods
    return config


def create_mercadopago_checkout(order: BillingOrder) -> CheckoutSession:
    if not settings.MERCADOPAGO_ACCESS_TOKEN:
        raise ValueError("Falta configurar MERCADOPAGO_ACCESS_TOKEN en el backend.")

    notification_url = f"{settings.BACKEND_PUBLIC_BASE_URL}{reverse('mercadopago-webhook')}"
    payload = {
        "items": [
            {
                "title": order.description,
                "quantity": 1,
                "currency_id": order.currency,
                "unit_price": float(order.amount),
            }
        ],
        "external_reference": order.external_reference,
        "payer": {
            "email": order.user.email or "",
        },
        "back_urls": {
            "success": build_frontend_return_url("success"),
            "failure": build_frontend_return_url("failure"),
            "pending": build_frontend_return_url("pending"),
        },
        "auto_return": "approved",
        "notification_url": notification_url,
        "payment_methods": build_payment_methods_config(),
    }
    response = requests.post(
        f"{MERCADOPAGO_API_BASE}/checkout/preferences",
        json=payload,
        headers={
            "Authorization": f"Bearer {settings.MERCADOPAGO_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return CheckoutSession(
        checkout_url=data.get("init_point", ""),
        sandbox_checkout_url=data.get("sandbox_init_point", ""),
        provider_reference=data.get("id", ""),
        raw_response=data,
    )


def create_checkout_order(user) -> BillingOrder:
    return create_checkout_order_for_kind(user, BillingOrder.Kind.MONTHLY)


def create_checkout_order_for_kind(user, kind: str) -> BillingOrder:
    if not settings.MERCADOPAGO_ACCESS_TOKEN:
        raise ValueError("Falta configurar MERCADOPAGO_ACCESS_TOKEN en el backend.")

    if kind == BillingOrder.Kind.PAY_PER_USE:
        description = "Transcriptor Pago por Uso"
        amount = get_per_use_amount()
    else:
        description = "Transcriptor Plan Mensual"
        amount = get_billing_amount()

    order = BillingOrder.objects.create(
        user=user,
        provider=BillingOrder.Provider.MERCADOPAGO,
        kind=kind,
        description=description,
        amount=amount,
        currency=settings.BILLING_CURRENCY,
    )
    try:
        checkout = create_mercadopago_checkout(order)
        order.provider_reference = checkout.provider_reference
        order.checkout_url = checkout.checkout_url
        order.sandbox_checkout_url = checkout.sandbox_checkout_url
        order.raw_provider_response = checkout.raw_response
        order.save(
            update_fields=[
                "provider_reference",
                "checkout_url",
                "sandbox_checkout_url",
                "raw_provider_response",
                "updated_at",
            ]
        )
        return order
    except Exception:
        order.delete()
        raise


def get_payment_details(payment_id: str) -> dict[str, Any]:
    response = requests.get(
        f"{MERCADOPAGO_API_BASE}/v1/payments/{payment_id}",
        headers={
            "Authorization": f"Bearer {settings.MERCADOPAGO_ACCESS_TOKEN}",
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def parse_signature_header(signature_header: str) -> tuple[str, str]:
    ts = ""
    signature_hash = ""
    for part in signature_header.split(","):
        key, _, value = part.partition("=")
        if key.strip() == "ts":
            ts = value.strip()
        elif key.strip() == "v1":
            signature_hash = value.strip()
    return ts, signature_hash


def is_valid_mercadopago_signature(request) -> bool:
    secret = settings.MERCADOPAGO_WEBHOOK_SECRET
    if not secret:
        return True

    signature_header = request.headers.get("x-signature", "")
    request_id = request.headers.get("x-request-id", "")
    if not signature_header or not request_id:
        return False

    data_id = request.GET.get("data.id", "")
    ts, received_hash = parse_signature_header(signature_header)
    manifest = f"id:{data_id.lower()};request-id:{request_id};ts:{ts};"
    expected = hmac.new(secret.encode(), msg=manifest.encode(), digestmod=hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, received_hash)


def activate_subscription_for_order(order: BillingOrder, payment_id: str) -> Subscription:
    now = timezone.now()
    current_active = Subscription.objects.filter(
        user=order.user,
        status=Subscription.Status.ACTIVE,
        ends_at__gt=now,
    ).order_by("-ends_at").first()
    starts_at = current_active.ends_at if current_active else now
    ends_at = starts_at + timedelta(days=settings.PAID_PLAN_DURATION_DAYS)

    subscription, created = Subscription.objects.get_or_create(
        provider=Subscription.Provider.MERCADOPAGO,
        provider_payment_id=payment_id,
        defaults={
            "user": order.user,
            "status": Subscription.Status.ACTIVE,
            "started_at": now,
            "ends_at": ends_at,
            "price_paid_usd": Decimal(str(settings.PAID_PLAN_PRICE_USD)),
            "payment_reference": order.external_reference,
        },
    )
    if not created:
        return subscription

    Subscription.objects.filter(
        user=order.user,
        status=Subscription.Status.ACTIVE,
    ).exclude(pk=subscription.pk).update(status=Subscription.Status.EXPIRED)
    return subscription


def grant_pay_per_use_credit(order: BillingOrder) -> None:
    profile = order.user.profile
    profile.paid_transcription_credits += 1
    profile.save(update_fields=["paid_transcription_credits"])


def process_mercadopago_webhook(request) -> BillingWebhookEvent:
    payload = request.data if isinstance(request.data, dict) else {}
    topic = payload.get("type") or request.GET.get("topic", "")
    action = payload.get("action", "")
    payment_id = str(payload.get("data", {}).get("id") or request.GET.get("data.id", "")).strip()
    is_valid = is_valid_mercadopago_signature(request)

    event = BillingWebhookEvent.objects.create(
        action=action,
        topic=topic,
        external_event_id=payment_id,
        is_valid_signature=is_valid,
        payload=payload,
    )

    if not payment_id or topic != "payment":
        event.processed = True
        event.save(update_fields=["processed"])
        return event

    if not is_valid:
        event.error_message = "Firma de webhook invalida."
        event.save(update_fields=["error_message"])
        return event

    payment = get_payment_details(payment_id)
    external_reference = payment.get("external_reference", "")
    order = BillingOrder.objects.filter(external_reference=external_reference).first()
    if order is None:
        event.error_message = "No se encontro la orden local para este pago."
        event.save(update_fields=["error_message"])
        return event

    payment_status = payment.get("status", "pending")
    mapped_status = {
        "approved": BillingOrder.Status.APPROVED,
        "rejected": BillingOrder.Status.REJECTED,
        "cancelled": BillingOrder.Status.CANCELLED,
    }.get(payment_status, BillingOrder.Status.PENDING)

    order.provider_payment_id = payment_id
    order.status = mapped_status
    order.raw_provider_response = payment
    if mapped_status == BillingOrder.Status.APPROVED:
        order.approved_at = timezone.now()
        if order.kind in {BillingOrder.Kind.MONTHLY, BillingOrder.Kind.ANNUAL}:
            activate_subscription_for_order(order, payment_id)
        elif order.kind == BillingOrder.Kind.PAY_PER_USE:
            grant_pay_per_use_credit(order)
    order.save(
        update_fields=[
            "provider_payment_id",
            "status",
            "raw_provider_response",
            "approved_at",
            "updated_at",
        ]
    )

    event.processed = True
    event.save(update_fields=["processed"])
    return event
