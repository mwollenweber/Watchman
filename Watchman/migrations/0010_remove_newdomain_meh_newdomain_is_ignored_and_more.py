# Generated by Django 4.2.16 on 2024-10-27 04:37

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Watchman", "0009_alter_search_last_completed_alter_search_last_ran_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="newdomain",
            name="meh",
        ),
        migrations.AddField(
            model_name="newdomain",
            name="is_ignored",
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name="clientalert",
            name="alert_type",
            field=models.CharField(
                choices=[
                    ("slack", "slack"),
                    ("slackWebhook", "slackWebhook"),
                    ("email", "email"),
                    ("gmail", "gmail"),
                ],
                db_index=True,
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name="search",
            name="last_completed",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(
                    2023, 10, 28, 4, 37, 47, 974451, tzinfo=datetime.timezone.utc
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
                    2023, 10, 28, 4, 37, 47, 974433, tzinfo=datetime.timezone.utc
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
                    2023, 10, 28, 4, 37, 47, 974419, tzinfo=datetime.timezone.utc
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
                    2023, 10, 28, 4, 37, 47, 976871, tzinfo=datetime.timezone.utc
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
                    2023, 10, 28, 4, 37, 47, 976887, tzinfo=datetime.timezone.utc
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
                    2023, 10, 28, 4, 37, 47, 976852, tzinfo=datetime.timezone.utc
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
                    2023, 10, 28, 4, 37, 47, 976837, tzinfo=datetime.timezone.utc
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
                    2023, 10, 28, 4, 37, 47, 973860, tzinfo=datetime.timezone.utc
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
                    2023, 10, 28, 4, 37, 47, 973876, tzinfo=datetime.timezone.utc
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
                    2023, 10, 28, 4, 37, 47, 973909, tzinfo=datetime.timezone.utc
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
                    2023, 10, 28, 4, 37, 47, 973208, tzinfo=datetime.timezone.utc
                ),
                null=True,
            ),
        ),
    ]