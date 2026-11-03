# Switch accounts to email-only identity with one-time login codes.
#
# Existing users keep their account. Any user without an email address (or
# sharing one with an earlier user) gets "<old username>@placeholder.invalid"
# so the unique constraint holds. Fix those addresses in the admin before
# those users need to sign in, since codes go to the stored address.

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

import accounts.models


def fill_missing_emails(apps, schema_editor):
    CustomUser = apps.get_model("accounts", "CustomUser")
    seen = set()
    for user in CustomUser.objects.order_by("pk"):
        email = (user.email or "").strip().lower()
        if not email or email in seen:
            base = f"{user.username}@placeholder.invalid"
            email, n = base, 1
            while email in seen:
                n += 1
                email = f"{user.username}+{n}@placeholder.invalid"
        seen.add(email)
        if email != user.email:
            user.email = email
            user.save(update_fields=["email"])


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(fill_missing_emails, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="customuser",
            name="email",
            field=models.EmailField(max_length=254, unique=True, verbose_name="email address"),
        ),
        migrations.RemoveField(
            model_name="customuser",
            name="username",
        ),
        migrations.AlterField(
            model_name="customuser",
            name="user_type",
            field=models.CharField(
                choices=[("client", "client"), ("clientAdmin", "clientAdmin"), ("admin", "admin")],
                default="client",
                max_length=20,
            ),
        ),
        migrations.AlterModelManagers(
            name="customuser",
            managers=[
                ("objects", accounts.models.CustomUserManager()),
            ],
        ),
        migrations.CreateModel(
            name="LoginCode",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("email", models.EmailField(db_index=True, max_length=254)),
                ("code_hash", models.CharField(max_length=64)),
                ("created", models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ("expires_at", models.DateTimeField()),
                ("used_at", models.DateTimeField(blank=True, null=True)),
                ("attempts", models.PositiveSmallIntegerField(default=0)),
                ("requested_ip", models.GenericIPAddressField(blank=True, null=True)),
            ],
            options={
                "ordering": ["-created"],
            },
        ),
    ]
