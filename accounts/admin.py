from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import AdminUserAddForm, AdminUserChangeForm
from .models import CustomUser, LoginCode


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = AdminUserAddForm
    form = AdminUserChangeForm
    add_form_template = None  # the stock template talks about usernames and passwords

    list_display = ("email", "first_name", "last_name", "user_type", "is_staff", "is_active", "last_login")
    list_filter = ("user_type", "is_staff", "is_superuser", "is_active")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    readonly_fields = ("last_login", "date_joined")

    fieldsets = (
        (None, {"fields": ("email",)}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "user_type",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "first_name", "last_name", "user_type", "is_staff", "is_superuser"),
            },
        ),
    )


@admin.register(LoginCode)
class LoginCodeAdmin(admin.ModelAdmin):
    list_display = ("email", "created", "expires_at", "used_at", "attempts", "requested_ip")
    list_filter = ("created",)
    search_fields = ("email",)
    readonly_fields = ("email", "created", "expires_at", "used_at", "attempts", "requested_ip")
    exclude = ("code_hash",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
