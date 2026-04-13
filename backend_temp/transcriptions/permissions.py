from django.conf import settings

from billing.models import Subscription


def user_has_active_subscription(user) -> bool:
    return Subscription.objects.filter(
        user=user,
        status=Subscription.Status.ACTIVE,
        ends_at__gt=Subscription.now(),
    ).exists()


def can_user_transcribe(user) -> tuple[bool, str]:
    access_kind = get_transcription_access_kind(user)
    if access_kind == "subscription":
        return True, "Suscripcion activa."

    if access_kind == "paid_credit":
        return True, f"Tienes {user.profile.paid_transcription_credits} credito(s) de pago disponible(s)."

    used = user.profile.free_transcriptions_used
    if used < settings.FREE_TRANSCRIPTIONS_PER_USER:
        remaining = settings.FREE_TRANSCRIPTIONS_PER_USER - used
        return True, f"Tienes {remaining} intento(s) gratis disponible(s)."

    return False, "Ya agotaste tus 2 intentos gratis, no tienes suscripcion activa y tampoco creditos de pago."


def consume_transcription_access(user) -> str:
    access_kind = get_transcription_access_kind(user)
    if access_kind == "subscription":
        return "subscription"

    profile = user.profile
    if access_kind == "paid_credit":
        profile.paid_transcription_credits -= 1
        profile.save(update_fields=["paid_transcription_credits"])
        return "paid_credit"

    profile.free_transcriptions_used += 1
    profile.save(update_fields=["free_transcriptions_used"])
    return "free"


def get_transcription_access_kind(user) -> str | None:
    if user_has_active_subscription(user):
        return "subscription"

    if user.profile.paid_transcription_credits > 0:
        return "paid_credit"

    used = user.profile.free_transcriptions_used
    if used < settings.FREE_TRANSCRIPTIONS_PER_USER:
        return "free"

    return None
