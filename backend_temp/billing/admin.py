from django.contrib import admin

from .models import BillingOrder, BillingWebhookEvent, Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "provider", "provider_payment_id", "started_at", "ends_at", "price_paid_usd")


@admin.register(BillingOrder)
class BillingOrderAdmin(admin.ModelAdmin):
    list_display = ("user", "provider", "amount", "currency", "status", "provider_reference", "created_at")
    search_fields = ("external_reference", "provider_reference", "provider_payment_id", "user__username", "user__email")


@admin.register(BillingWebhookEvent)
class BillingWebhookEventAdmin(admin.ModelAdmin):
    list_display = ("provider", "topic", "action", "external_event_id", "is_valid_signature", "processed", "created_at")
