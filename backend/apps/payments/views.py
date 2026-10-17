"""
Payment endpoints.

Mounted at `/api/v1/payments/`.

    POST   /                       Initiate a payment for a course OR content
    POST   /{payment_id}/confirm   Simulated checkout: complete (or fail with
                                   {"simulate": "failure"}) a pending payment.
                                   Only enabled when PAYMENT_PROVIDER=simulation.
    GET    /me                     Current user's payment history
    GET    /{payment_id}           Detail (own payments only)
"""
from __future__ import annotations

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.content.models import Content
from apps.courses.models import Course

from . import services
from .serializers import PaymentCreateSerializer, PaymentResponseSerializer


class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        currency = data.get("currency", "XOF")

        # --- Course payment ---------------------------------------------------
        if data.get("course_id"):
            course = Course.objects.filter(pk=data["course_id"]).first()
            if not course:
                return Response(
                    {"detail": "Cours introuvable."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if course.is_free:
                return Response(
                    {"detail": "Ce cours est gratuit, aucun paiement nécessaire."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if services.has_completed_payment(request.user.id, course.id):
                return Response(
                    {"detail": "Vous avez déjà payé pour ce cours."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # The amount always comes from the catalogue, never from the client.
            payment = services.create_payment(
                user_id=request.user.id,
                course_id=course.id,
                amount=course.price or 0,
                currency=currency,
                payment_method=data.get("payment_method"),
            )
            return Response(
                PaymentResponseSerializer(payment).data,
                status=status.HTTP_201_CREATED,
            )

        # --- Content payment --------------------------------------------------
        content = Content.objects.filter(pk=data["content_id"]).first()
        if not content:
            return Response(
                {"detail": "Contenu introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not content.is_premium:
            return Response(
                {"detail": "Ce contenu est gratuit, aucun paiement nécessaire."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if services.has_completed_content_payment(request.user.id, content.id):
            return Response(
                {"detail": "Vous avez déjà payé pour ce contenu."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = services.create_payment(
            user_id=request.user.id,
            content_id=content.id,
            amount=content.price or 0,
            currency=currency,
            payment_method=data.get("payment_method"),
        )
        return Response(
            PaymentResponseSerializer(payment).data,
            status=status.HTTP_201_CREATED,
        )


class ConfirmPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, payment_id: int):
        # Self-confirmation only exists in simulation mode; a real provider
        # confirms payments through its webhook instead.
        if settings.PAYMENT_PROVIDER != "simulation":
            return Response(
                {"detail": "La confirmation manuelle des paiements est désactivée."},
                status=status.HTTP_403_FORBIDDEN,
            )
        outcome = request.data.get("simulate", "success")
        if outcome == "failure":
            payment = services.fail_payment(payment_id, request.user.id)
        else:
            payment = services.confirm_payment(payment_id, request.user.id)
        if not payment:
            return Response(
                {"detail": "Paiement introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(PaymentResponseSerializer(payment).data)


class MyPaymentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        skip = int(request.query_params.get("skip", 0))
        limit = int(request.query_params.get("limit", 50))
        payments = services.get_user_payments(request.user.id, skip, limit)
        return Response(PaymentResponseSerializer(payments, many=True).data)


class PaymentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, payment_id: int):
        payment = services.get_payment_by_id(payment_id)
        if not payment or payment.user_id != request.user.id:
            return Response(
                {"detail": "Paiement introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(PaymentResponseSerializer(payment).data)
