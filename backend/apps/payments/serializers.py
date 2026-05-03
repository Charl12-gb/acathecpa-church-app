from __future__ import annotations

from rest_framework import serializers

from .models import Payment, PaymentMethod


class PaymentResponseSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    course_id = serializers.IntegerField(read_only=True, allow_null=True)
    content_id = serializers.IntegerField(read_only=True, allow_null=True)
    course_title = serializers.CharField(source="course.title", read_only=True, allow_null=True)
    content_title = serializers.CharField(source="content.title", read_only=True, allow_null=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "user_id",
            "course_id",
            "course_title",
            "content_id",
            "content_title",
            "amount",
            "currency",
            "status",
            "payment_method",
            "transaction_ref",
            "created_at",
            "completed_at",
        ]
        read_only_fields = fields


class PaymentCreateSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(required=False, allow_null=True)
    content_id = serializers.IntegerField(required=False, allow_null=True)
    amount = serializers.FloatField(min_value=0)
    currency = serializers.CharField(max_length=10, default="XOF", required=False)
    payment_method = serializers.ChoiceField(
        choices=PaymentMethod.choices, required=False, allow_null=True
    )

    def validate(self, attrs):
        course_id = attrs.get("course_id")
        content_id = attrs.get("content_id")
        if bool(course_id) == bool(content_id):
            raise serializers.ValidationError(
                "Fournissez exactement un de course_id ou content_id."
            )
        return attrs
