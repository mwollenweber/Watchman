# Generated by Django 4.2.10 on 2024-07-14 20:20

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("Watchman", "0004_search_interval"),
    ]

    operations = [
        migrations.AddField(
            model_name="search",
            name="database",
            field=models.CharField(
                db_index=True, default=django.utils.timezone.now, max_length=255
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="search",
            name="tolerance",
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name="search",
            name="interval",
            field=models.IntegerField(
                blank=True, db_index=True, default=1440, null=True
            ),
        ),
        migrations.AlterField(
            model_name="search",
            name="last_ran",
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.CreateModel(
            name="WhoisRecord",
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
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "domain",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Watchman.domain",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="WebPage",
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
                ("page", models.CharField(blank=True, db_index=True, null=True)),
                ("tdstamp", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "md5",
                    models.CharField(
                        blank=True, db_index=True, max_length=32, null=True
                    ),
                ),
                (
                    "size",
                    models.IntegerField(
                        blank=True, db_index=True, default=0, null=True
                    ),
                ),
                (
                    "status_code",
                    models.IntegerField(
                        blank=True, db_index=True, default=0, null=True
                    ),
                ),
                (
                    "ip",
                    models.GenericIPAddressField(blank=True, db_index=True, null=True),
                ),
                (
                    "domain",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Watchman.domain",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PingRecord",
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
                ("tdstamp", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "fqdn",
                    models.CharField(
                        blank=True, db_index=True, max_length=255, null=True
                    ),
                ),
                (
                    "ip",
                    models.GenericIPAddressField(blank=True, db_index=True, null=True),
                ),
                ("alive", models.BooleanField(db_index=True, default=False)),
                (
                    "domain",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Watchman.domain",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MXRecord",
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
                ("tdstamp", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "record",
                    models.CharField(
                        blank=True, db_index=True, max_length=255, null=True
                    ),
                ),
                (
                    "ip",
                    models.GenericIPAddressField(blank=True, db_index=True, null=True),
                ),
                (
                    "domain",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Watchman.domain",
                    ),
                ),
            ],
        ),
    ]
