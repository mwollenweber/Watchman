# Generated by Django 4.2.10 on 2024-07-27 03:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Watchman", "0023_rename_first_seen_domain_created_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="domain",
            name="exp_date",
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="webpage",
            name="fqdn",
            field=models.CharField(
                blank=True, db_index=True, max_length=255, null=True
            ),
        ),
        migrations.AlterField(
            model_name="pingrecord",
            name="alive",
            field=models.BooleanField(db_index=True, default=True),
        ),
        migrations.AlterField(
            model_name="search",
            name="last_completed",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(
                    2023, 7, 28, 3, 24, 36, 544231, tzinfo=datetime.timezone.utc
                ),
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="search",
            name="last_ran",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(
                    2023, 7, 28, 3, 24, 36, 544207, tzinfo=datetime.timezone.utc
                ),
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="search",
            name="last_updated",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(
                    2023, 7, 28, 3, 24, 36, 544189, tzinfo=datetime.timezone.utc
                ),
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="zonelist",
            name="last_completed",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(
                    2023, 7, 28, 3, 24, 36, 543272, tzinfo=datetime.timezone.utc
                ),
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="zonelist",
            name="last_diffed",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(
                    2023, 7, 28, 3, 24, 36, 543283, tzinfo=datetime.timezone.utc
                ),
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="zonelist",
            name="last_error",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(
                    2023, 7, 28, 3, 24, 36, 543292, tzinfo=datetime.timezone.utc
                ),
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="zonelist",
            name="last_updated",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(
                    2023, 7, 28, 3, 24, 36, 542954, tzinfo=datetime.timezone.utc
                ),
                null=True,
            ),
        ),
    ]
