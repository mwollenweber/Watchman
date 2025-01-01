# Generated by Django 4.2.16 on 2024-11-09 00:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Watchman", "0013_alter_search_last_completed_alter_search_last_ran_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="search",
            name="last_completed",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(
                    2023, 11, 10, 0, 55, 32, 955591, tzinfo=datetime.timezone.utc
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
                    2023, 11, 10, 0, 55, 32, 955573, tzinfo=datetime.timezone.utc
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
                    2023, 11, 10, 0, 55, 32, 955561, tzinfo=datetime.timezone.utc
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
                    2023, 11, 10, 0, 55, 32, 957981, tzinfo=datetime.timezone.utc
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
                    2023, 11, 10, 0, 55, 32, 957993, tzinfo=datetime.timezone.utc
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
                    2023, 11, 10, 0, 55, 32, 957960, tzinfo=datetime.timezone.utc
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
                    2023, 11, 10, 0, 55, 32, 957946, tzinfo=datetime.timezone.utc
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
                    2023, 11, 10, 0, 55, 32, 955071, tzinfo=datetime.timezone.utc
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
                    2023, 11, 10, 0, 55, 32, 955083, tzinfo=datetime.timezone.utc
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
                    2023, 11, 10, 0, 55, 32, 955098, tzinfo=datetime.timezone.utc
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
                    2023, 11, 10, 0, 55, 32, 954456, tzinfo=datetime.timezone.utc
                ),
                null=True,
            ),
        ),
    ]
