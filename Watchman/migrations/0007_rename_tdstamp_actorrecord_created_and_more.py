# Generated by Django 4.2.10 on 2024-07-15 20:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        (
            "Watchman",
            "0006_actorrecord_alter_match_options_alter_search_options_and_more",
        ),
    ]

    operations = [
        migrations.RenameField(
            model_name="actorrecord",
            old_name="tdstamp",
            new_name="created",
        ),
        migrations.RenameField(
            model_name="mxrecord",
            old_name="tdstamp",
            new_name="created",
        ),
        migrations.RenameField(
            model_name="pingrecord",
            old_name="tdstamp",
            new_name="created",
        ),
        migrations.RenameField(
            model_name="webpage",
            old_name="tdstamp",
            new_name="created",
        ),
        migrations.AddField(
            model_name="zonelist",
            name="last_completed",
            field=models.DateTimeField(default=None),
        ),
        migrations.CreateModel(
            name="MatchHit",
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
                ("hit", models.CharField(db_index=True, max_length=255)),
                (
                    "is_new",
                    models.BooleanField(blank=True, db_index=True, default=True),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "match",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="Watchman.match"
                    ),
                ),
            ],
        ),
    ]
