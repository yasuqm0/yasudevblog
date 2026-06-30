import requests
from django.conf import settings
from django.db import transaction as db_transaction
from django.utils import timezone

from accounts.models import Profile
from .models import Transaction


PAYMENT_PACKS = {
    "mini": {
        "name": "Pack Mini",
        "amount": 100,
        "discs": 10,
    },
    "medio": {
        "name": "Pack Medio",
        "amount": 500,
        "discs": 60,
    },
    "grande": {
        "name": "Pack Grande",
        "amount": 1000,
        "discs": 150,
    },
    "legendario": {
        "name": "Pack Legendario",
        "amount": 2000,
        "discs": 300,
    },
}


def complete_transaction(transaction_id, payment_reference=""):
    with db_transaction.atomic():
        transaction = Transaction.objects.select_for_update().select_related("user").get(id=transaction_id)

        if transaction.status == Transaction.STATUS_COMPLETED:
            return transaction

        transaction.status = Transaction.STATUS_COMPLETED
        transaction.payment_reference = payment_reference or transaction.payment_reference
        transaction.paid_at = timezone.now()
        transaction.save(update_fields=["status", "payment_reference", "paid_at", "updated_at"])

        profile, _ = Profile.objects.select_for_update().get_or_create(user=transaction.user)
        profile.discs += transaction.discs_purchased
        profile.save(update_fields=["discs"])

        return transaction


def fail_transaction(transaction, payment_reference=""):
    transaction.status = Transaction.STATUS_FAILED
    transaction.payment_reference = payment_reference or transaction.payment_reference
    transaction.save(update_fields=["status", "payment_reference", "updated_at"])
    return transaction


def create_culqi_charge(transaction, token):
    if not settings.CULQI_PRIVATE_KEY:
        raise ValueError("CULQI_PRIVATE_KEY no está configurada.")

    payload = {
        "amount": transaction.amount,
        "currency_code": "PEN",
        "email": transaction.user.email or f"{transaction.user.username}@yasudevblog.lat",
        "source_id": token,
        "description": f"Compra de {transaction.discs_purchased} discos en yasudevblog.lat",
        "metadata": {
            "transaction_id": str(transaction.id),
            "user_id": transaction.user.id,
            "pack": transaction.pack,
        },
    }

    response = requests.post(
        "https://api.culqi.com/v2/charges",
        json=payload,
        headers={
            "Authorization": f"Bearer {settings.CULQI_PRIVATE_KEY}",
            "Content-Type": "application/json",
        },
        timeout=20,
    )

    data = response.json()

    if response.status_code not in [200, 201]:
        error_message = data.get("merchant_message") or data.get("user_message") or str(data)
        raise ValueError(error_message)

    return data