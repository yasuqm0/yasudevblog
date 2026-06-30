from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "pack",
        "amount",
        "discs_purchased",
        "status",
        "provider",
        "payment_reference",
        "created_at",
        "paid_at",
    )
    list_filter = ("status", "provider", "pack", "created_at")
    search_fields = ("id", "user__username", "user__email", "payment_reference")
    readonly_fields = ("id", "created_at", "updated_at", "paid_at")