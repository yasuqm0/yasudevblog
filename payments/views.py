from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Transaction
from .serializers import PaymentConfirmSerializer, PaymentCreateSerializer, TransactionSerializer
from .services import PAYMENT_PACKS, complete_transaction, create_culqi_charge, fail_transaction


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def payment_packs(request):
    return Response(PAYMENT_PACKS)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_payment(request):
    serializer = PaymentCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    pack_key = serializer.validated_data["pack"]
    pack = PAYMENT_PACKS[pack_key]

    transaction = Transaction.objects.create(
        user=request.user,
        pack=pack_key,
        amount=pack["amount"],
        discs_purchased=pack["discs"],
        status=Transaction.STATUS_PENDING,
    )

    return Response(
        {
            "transaction": TransactionSerializer(transaction).data,
            "culqi": {
                "public_key": settings.CULQI_PUBLIC_KEY,
                "settings": {
                    "title": "YasuDevBlog - Discos",
                    "currency": "PEN",
                    "amount": transaction.amount,
                },
                "client": {
                    "email": request.user.email,
                },
            },
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def confirm_payment(request):
    serializer = PaymentConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    transaction = Transaction.objects.get(
        id=serializer.validated_data["transaction_id"],
        user=request.user,
    )

    if transaction.status != Transaction.STATUS_PENDING:
        return Response(TransactionSerializer(transaction).data)

    try:
        charge = create_culqi_charge(transaction, serializer.validated_data["token"])
        payment_reference = charge.get("data", {}).get("id") or charge.get("id", "")
        transaction = complete_transaction(transaction.id, payment_reference=payment_reference)
    except Exception as error:
        fail_transaction(transaction, payment_reference=str(error)[:120])
        return Response(
            {"detail": "El pago fue rechazado.", "error": str(error)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(TransactionSerializer(transaction).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def simulate_payment(request):
    if not settings.PAYMENTS_SIMULATION_ENABLED:
        return Response(
            {"detail": "La simulación de pagos está desactivada."},
            status=status.HTTP_403_FORBIDDEN,
        )

    transaction_id = request.data.get("transaction_id")

    transaction = Transaction.objects.get(
        id=transaction_id,
        user=request.user,
        status=Transaction.STATUS_PENDING,
    )

    transaction = complete_transaction(transaction.id, payment_reference=f"simulated-{transaction.id}")

    return Response(TransactionSerializer(transaction).data)


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def culqi_webhook(request):
    expected_secret = getattr(settings, "CULQI_WEBHOOK_SECRET", "")

    if expected_secret:
        received_secret = request.GET.get("secret") or request.headers.get("X-Webhook-Secret", "")
        if received_secret != expected_secret:
            return Response({"detail": "Webhook no autorizado."}, status=status.HTTP_403_FORBIDDEN)

    payload = request.data
    data = payload.get("data", {})
    charge = data.get("object", data) if isinstance(data, dict) else {}

    metadata = charge.get("metadata", {}) if isinstance(charge, dict) else {}
    transaction_id = metadata.get("transaction_id")

    if not transaction_id:
        return Response({"detail": "Webhook recibido sin transaction_id."}, status=status.HTTP_200_OK)

    payment_reference = charge.get("id", "")

    try:
        transaction = complete_transaction(transaction_id, payment_reference=payment_reference)
    except Transaction.DoesNotExist:
        return Response({"detail": "Transacción no encontrada."}, status=status.HTTP_200_OK)

    return Response(TransactionSerializer(transaction).data)

@login_required
def payment_store(request):
    return render(
        request,
        "payments/store.html",
        {
            "payment_packs": PAYMENT_PACKS,
            "culqi_public_key": settings.CULQI_PUBLIC_KEY,
            "simulation_enabled": settings.PAYMENTS_SIMULATION_ENABLED,
        },
    )