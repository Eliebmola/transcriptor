from django.urls import path

from .views import BillingCheckoutView, BillingStatusView, MercadoPagoWebhookView

urlpatterns = [
    path("status/", BillingStatusView.as_view(), name="billing-status"),
    path("checkout/", BillingCheckoutView.as_view(), name="billing-checkout"),
    path("webhooks/mercadopago/", MercadoPagoWebhookView.as_view(), name="mercadopago-webhook"),
]
