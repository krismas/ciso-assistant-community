# Generated by Django 5.0.4 on 2024-06-21 22:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("global_settings", "0001_initial"),
        ("iam", "0003_alter_folder_updated_at_alter_role_updated_at_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="SSOSettings",
            fields=[
                (
                    "globalsettings_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="global_settings.globalsettings",
                    ),
                ),
                (
                    "is_enabled",
                    models.BooleanField(default=False, verbose_name="is enabled"),
                ),
                ("provider", models.CharField(max_length=30, verbose_name="provider")),
                (
                    "provider_id",
                    models.CharField(
                        blank=True, max_length=200, verbose_name="provider ID"
                    ),
                ),
                (
                    "provider_name",
                    models.CharField(max_length=200, verbose_name="name"),
                ),
                (
                    "client_id",
                    models.CharField(
                        default="0",
                        help_text="App ID, or consumer key",
                        max_length=191,
                        verbose_name="client id",
                    ),
                ),
                (
                    "secret",
                    models.CharField(
                        blank=True,
                        help_text="API secret, client secret, or consumer secret",
                        max_length=191,
                        verbose_name="secret key",
                    ),
                ),
                (
                    "key",
                    models.CharField(
                        blank=True, help_text="Key", max_length=191, verbose_name="key"
                    ),
                ),
                ("settings", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "managed": False,
            },
            bases=("global_settings.globalsettings",),
        ),
        migrations.AddField(
            model_name="user",
            name="is_sso",
            field=models.BooleanField(default=False),
        ),
    ]
