from django.conf import settings
from rest_framework import serializers

from .models import BillingOrder, Subscription


class BillingOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingOrder
        fields = (
            "id",
            "kind",
            "external_reference",
            "provider",
            "provider_reference",
            "provider_payment_id",
            "description",
            "amount",
            "currency",
            "status",
            "checkout_url",
            "sandbox_checkout_url",
            "created_at",
            "approved_at",
        )


class BillingStatusSerializer(serializers.Serializer):
    provider = serializers.CharField()
    public_key = serializers.CharField(allow_blank=True)
    annual_plan_price = serializers.CharField()
    annual_plan_price_usd = serializers.CharField()
    pay_per_use_price = serializers.CharField()
    pay_per_use_price_usd = serializers.CharField()
    currency = serializers.CharField()
    plan_duration_days = serializers.IntegerField()
    has_active_subscription = serializers.BooleanField()
    paid_transcription_credits = serializers.IntegerField()
    active_subscription_end = serializers.DateTimeField(allow_null=True)
    latest_order = BillingOrderSerializer(allow_null=True)

    @classmethod
    def from_user(cls, user):
        active_subscription = Subscription.objects.filter(
            user=user,
            status=Subscription.Status.ACTIVE,
            ends_at__gt=Subscription.now(),
        ).order_by("-ends_at").first()
        latest_order = BillingOrder.objects.filter(user=user).order_by("-created_at").first()
        return cls(
            {
                "provider": settings.PAYMENT_PROVIDER,
                "public_key": settings.MERCADOPAGO_PUBLIC_KEY,
                "annual_plan_price": settings.PAID_PLAN_PRICE,
                "annual_plan_price_usd": settings.PAID_PLAN_PRICE_USD,
                "pay_per_use_price": settings.PER_USE_PRICE,
                "pay_per_use_price_usd": settings.PER_USE_PRICE_USD,
                "currency": settings.BILLING_CURRENCY,
                "plan_duration_days": settings.PAID_PLAN_DURATION_DAYS,
                "has_active_subscription": bool(active_subscription),
                "paid_transcription_credits": user.profile.paid_transcription_credits,
                "active_subscription_end": active_subscription.ends_at if active_subscription else None,
                "latest_order": latest_order,
            }
        )
