import requests
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import BillingOrderSerializer, BillingStatusSerializer
from .models import BillingOrder
from .services import create_checkout_order_for_kind, process_mercadopago_webhook


class BillingStatusView(APIView):
    def get(self, request):
        serializer = BillingStatusSerializer.from_user(request.user)
        return Response(serializer.data)


class BillingCheckoutView(APIView):
    def post(self, request):
        requested_kind = request.data.get("kind", BillingOrder.Kind.MONTHLY)
        if requested_kind not in BillingOrder.Kind.values:
            return Response({"detail": "Tipo de pago invalido."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = create_checkout_order_for_kind(request.user, requested_kind)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException:
            return Response(
                {"detail": "No fue posible conectar con Mercado Pago desde este entorno. Revisa proxy, firewall o conexion de red."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(BillingOrderSerializer(order).data, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name="dispatch")
class MercadoPagoWebhookView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        process_mercadopago_webhook(request)
        return Response({"received": True}, status=status.HTTP_200_OK)
