from django.urls import path

from .views import (
    ConfirmPaymentView,
    InitiatePaymentView,
    MyPaymentsView,
    PaymentDetailView,
)

urlpatterns = [
    path("", InitiatePaymentView.as_view(), name="initiate-payment"),
    path("me", MyPaymentsView.as_view(), name="my-payments"),
    path("<int:payment_id>/confirm", ConfirmPaymentView.as_view(), name="confirm-payment"),
    path("<int:payment_id>", PaymentDetailView.as_view(), name="payment-detail"),
]
