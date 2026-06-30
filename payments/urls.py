from django.urls import path

from . import views

urlpatterns = [
    path("", views.payment_store, name="payment_store"),
]