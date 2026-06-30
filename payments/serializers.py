from rest_framework import serializers

from .models import Transaction
from .services import PAYMENT_PACKS


class PaymentCreateSerializer(serializers.Serializer):
    pack = serializers.ChoiceField(choices=[(key, value["name"]) for key, value in PAYMENT_PACKS.items()])


class PaymentConfirmSerializer(serializers.Serializer):
    transaction_id = serializers.UUIDField()
    token = serializers.CharField(max_length=120)


class TransactionSerializer(serializers.ModelSerializer):
    amount_soles = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            "id",
            "pack",
            "amount",
            "amount_soles",
            "discs_purchased",
            "status",
            "payment_reference",
            "provider",
            "created_at",
            "paid_at",
        ]

    def get_amount_soles(self, obj):
        return obj.amount / 100