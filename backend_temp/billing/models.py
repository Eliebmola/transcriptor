from decimal import Decimal
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Subscription(models.Model):
    class Provider(models.TextChoices):
        MERCADOPAGO = "mercadopago", "Mercado Pago"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        PENDING = "pending", "Pending"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    started_at = models.DateTimeField(default=timezone.now)
    ends_at = models.DateTimeField()
    price_paid_usd = models.DecimalField(max_digits=6, decimal_places=2, default=8)
    payment_reference = models.CharField(max_length=255, blank=True)
    provider = models.CharField(max_length=30, choices=Provider.choices, default=Provider.MERCADOPAGO)
    provider_payment_id = models.CharField(max_length=120, blank=True)

    @staticmethod
    def now():
        return timezone.now()

    @property
    def is_active(self) -> bool:
        return self.status == self.Status.ACTIVE and self.ends_at > self.now()


class BillingOrder(models.Model):
    class Provider(models.TextChoices):
        MERCADOPAGO = "mercadopago", "Mercado Pago"

    class Kind(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        ANNUAL = "annual", "Annual"
        PAY_PER_USE = "pay_per_use", "Pay Per Use"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"
        ERROR = "error", "Error"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="billing_orders")
    provider = models.CharField(max_length=30, choices=Provider.choices, default=Provider.MERCADOPAGO)
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.MONTHLY)
    external_reference = models.CharField(max_length=64, unique=True, default="", editable=False)
    provider_reference = models.CharField(max_length=120, blank=True)
    provider_payment_id = models.CharField(max_length=120, blank=True)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=10, default="COP")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    checkout_url = models.URLField(blank=True)
    sandbox_checkout_url = models.URLField(blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    raw_provider_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.external_reference:
            self.external_reference = uuid.uuid4().hex
        super().save(*args, **kwargs)


class BillingWebhookEvent(models.Model):
    provider = models.CharField(max_length=30, default=BillingOrder.Provider.MERCADOPAGO)
    action = models.CharField(max_length=120, blank=True)
    topic = models.CharField(max_length=120, blank=True)
    external_event_id = models.CharField(max_length=120, blank=True)
    is_valid_signature = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
