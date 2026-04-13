from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from billing.models import Subscription


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs["username"], password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Credenciales invalidas.")
        attrs["user"] = user
        return attrs


class MeSerializer(serializers.ModelSerializer):
    free_transcriptions_used = serializers.IntegerField(source="profile.free_transcriptions_used", read_only=True)
    paid_transcription_credits = serializers.IntegerField(source="profile.paid_transcription_credits", read_only=True)
    free_transcriptions_remaining = serializers.SerializerMethodField()
    has_active_subscription = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "free_transcriptions_used",
            "paid_transcription_credits",
            "free_transcriptions_remaining",
            "has_active_subscription",
        )

    def get_free_transcriptions_remaining(self, obj):
        limit = settings.FREE_TRANSCRIPTIONS_PER_USER
        return max(limit - obj.profile.free_transcriptions_used, 0)

    def get_has_active_subscription(self, obj):
        return Subscription.objects.filter(user=obj, status=Subscription.Status.ACTIVE, ends_at__gt=Subscription.now()).exists()
