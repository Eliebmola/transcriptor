from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Subscription",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("active", "Active"), ("expired", "Expired"), ("pending", "Pending")], default="pending", max_length=20)),
                ("started_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("ends_at", models.DateTimeField()),
                ("price_paid_usd", models.DecimalField(decimal_places=2, default=8, max_digits=6)),
                ("payment_reference", models.CharField(blank=True, max_length=255)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="subscriptions", to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
