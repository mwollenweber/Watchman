# Generated by Django 4.2.10 on 2024-07-13 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Watchman", "0003_rename_clients_client_rename_domains_domain_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="search",
            name="interval",
            field=models.IntegerField(blank=True, default=1440, null=True),
        ),
    ]
