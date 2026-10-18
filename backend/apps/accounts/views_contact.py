"""Public contact form endpoint: forwards the message to CONTACT_EMAIL."""
from __future__ import annotations

import logging

from django.conf import settings
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .models import ContactMessage

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
        # Saved first, so the message is never lost even if the email fails.
        saved = ContactMessage.objects.create(
            name=data["name"], email=data["email"], subject=data["subject"], message=data["message"],
        )
        saved.email_sent = services.send_email(
            subject=f"[Contact] {data['subject']}",
            recipient=recipient,
            body=body,
            reply_to=data["email"],
        )
        saved.save(update_fields=["email_sent"])
        if not saved.email_sent:
            logger.error("Contact email failed for message %s (kept in database)", saved.id)

        return Response(
            {"message": "Votre message a bien été reçu. Nous vous répondrons rapidement."},
            status=status.HTTP_201_CREATED,
        )
