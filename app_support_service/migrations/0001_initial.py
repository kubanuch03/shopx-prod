# Generated by Django 5.0.3 on 2024-03-27 05:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SupportService",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("phone_number", models.CharField(max_length=15)),
                ("instagram_link", models.URLField()),
                ("whatsapp_link", models.URLField()),
                ("facebook_link", models.URLField()),
                ("telegram_token", models.CharField(max_length=50)),
                ("telegram_chat_id", models.CharField(max_length=15)),
                (
                    "admin",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]