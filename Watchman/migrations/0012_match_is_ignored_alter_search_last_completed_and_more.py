# Generated by Django 4.2.16 on 2024-11-07 03:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Watchman", "0011_alter_search_last_completed_alter_search_last_ran_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="match",
            name="is_ignored",
            field=models.BooleanField(blank=True, db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name="search",
            name="last_completed",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(
                    2023, 11, 8, 3, 55, 45, 130169, tzinfo=datetime.timezone.utc
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
                    2023, 11, 8, 3, 55, 45, 130149, tzinfo=datetime.timezone.utc
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
                    2023, 11, 8, 3, 55, 45, 130135, tzinfo=datetime.timezone.utc
                ),
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="watch",
            name="last_completed",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(
                    2023, 11, 8, 3, 55, 45, 133604, tzinfo=datetime.timezone.utc
                ),
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="watch",
            name="last_error",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(
                    2023, 11, 8, 3, 55, 45, 133617, tzinfo=datetime.timezone.utc
                ),
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="watch",
            name="last_ran",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(
                    2023, 11, 8, 3, 55, 45, 133582, tzinfo=datetime.timezone.utc
                ),
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="watch",
            name="last_updated",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(
                    2023, 11, 8, 3, 55, 45, 133561, tzinfo=datetime.timezone.utc
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
                    2023, 11, 8, 3, 55, 45, 129578, tzinfo=datetime.timezone.utc
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
                    2023, 11, 8, 3, 55, 45, 129591, tzinfo=datetime.timezone.utc
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
                    2023, 11, 8, 3, 55, 45, 129600, tzinfo=datetime.timezone.utc
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
                    2023, 11, 8, 3, 55, 45, 128941, tzinfo=datetime.timezone.utc
                ),
                null=True,
            ),
        ),
    ]