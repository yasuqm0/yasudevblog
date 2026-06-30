import uuid
from django.conf import settings
from django.db import models


class Transaction(models.Model):
    STATUS_PENDING = "pending"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pendiente"),
        (STATUS_COMPLETED, "Completado"),
        (STATUS_FAILED, "Fallido"),
    ]

    PACK_CHOICES = [
        ("mini", "Pack Mini"),
        ("medio", "Pack Medio"),
        ("grande", "Pack Grande"),
        ("legendario", "Pack Legendario"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payment_transactions")
    pack = models.CharField(max_length=20, choices=PACK_CHOICES)
    amount = models.PositiveIntegerField(help_text="Monto en centimos. Ejemplo: S/ 1.00 = 100")
    discs_purchased = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    payment_reference = models.CharField(max_length=120, blank=True)
    provider = models.CharField(max_length=30, default="culqi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.pack} - {self.status}"