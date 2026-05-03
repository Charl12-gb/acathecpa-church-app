"""Public contact form endpoint: forwards the message to CONTACT_EMAIL."""
from __future__ import annotations

import logging

from django.conf import settings
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services

logger = logging.getLogger(__name__)


class ContactMessageSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120)
    email = serializers.EmailField()
    subject = serializers.CharField(max_length=200)
    message = serializers.CharField(max_length=5000)


class ContactView(APIView):
    """`POST /api/v1/contact` — public contact form."""
    permission_classes = [AllowAny]
    authentication_classes: list = []

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        recipient = getattr(settings, "CONTACT_EMAIL", None) or settings.DEFAULT_FROM_EMAIL
        body = (
            f"Nouveau message via le formulaire de contact ({settings.PROJECT_NAME}).\n\n"
            f"Nom    : {data['name']}\n"
            f"Email  : {data['email']}\n"
            f"Sujet  : {data['subject']}\n\n"
            f"Message :\n{data['message']}\n"
        )
        try:
            services.send_email(
                subject=f"[Contact] {data['subject']}",
                recipient=recipient,
                body=body,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Contact email failed: %s", exc)
            return Response(
                {"detail": "Impossible d'envoyer le message pour le moment."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {"message": "Votre message a bien été envoyé. Nous vous répondrons rapidement."},
            status=status.HTTP_201_CREATED,
        )
