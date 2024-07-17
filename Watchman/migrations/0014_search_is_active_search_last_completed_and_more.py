# Generated by Django 4.2.10 on 2024-07-17 03:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Watchman", "0013_alter_zonelist_last_completed_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="search",
            name="is_active",
            field=models.BooleanField(blank=True, db_index=True, default=True),
        ),
        migrations.AddField(
            model_name="search",
            name="last_completed",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(
                    2023, 7, 18, 3, 5, 47, 921358, tzinfo=datetime.timezone.utc
                ),
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="search",
            name="criteria",
            field=models.CharField(default="test", max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="search",
            name="last_ran",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(
                    2023, 7, 18, 3, 5, 47, 921337, tzinfo=datetime.timezone.utc
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
                    2023, 7, 18, 3, 5, 47, 921324, tzinfo=datetime.timezone.utc
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
                    2023, 7, 18, 3, 5, 47, 920698, tzinfo=datetime.timezone.utc
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
                    2023, 7, 18, 3, 5, 47, 920711, tzinfo=datetime.timezone.utc
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
                    2023, 7, 18, 3, 5, 47, 920721, tzinfo=datetime.timezone.utc
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
                    2023, 7, 18, 3, 5, 47, 920234, tzinfo=datetime.timezone.utc
                ),
                null=True,
            ),
        ),
    ]
