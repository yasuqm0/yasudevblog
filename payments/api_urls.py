from django.urls import path

from . import views

urlpatterns = [
    path("packs/", views.payment_packs, name="payment-packs"),
    path("create/", views.create_payment, name="payment-create"),
    path("confirm/", views.confirm_payment, name="payment-confirm"),
    path("simulate/", views.simulate_payment, name="payment-simulate"),
]