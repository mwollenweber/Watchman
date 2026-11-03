from django import forms

from .models import CustomUser, LoginCode, normalize_email


class EmailForm(forms.Form):
    email = forms.EmailField(
        label="Email address",
        max_length=254,
        widget=forms.EmailInput(
            attrs={"autofocus": True, "autocomplete": "email", "placeholder": "you@example.com"}
        ),
    )

    def clean_email(self):
        return normalize_email(self.cleaned_data["email"])


class CodeForm(forms.Form):
    code = forms.CharField(
        label="Login code",
        min_length=LoginCode.CODE_LENGTH,
        max_length=LoginCode.CODE_LENGTH,
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "autocomplete": "one-time-code",
                "inputmode": "numeric",
                "pattern": "[0-9]*",
                "placeholder": "0" * LoginCode.CODE_LENGTH,
            }
        ),
    )

    def clean_code(self):
        code = self.cleaned_data["code"].strip().replace(" ", "")
        if not code.isdigit():
            raise forms.ValidationError("The code is numbers only.")
        return code


class AdminUserAddForm(forms.ModelForm):
    """Create a user from the admin. No password: they sign in with an emailed code."""

    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name", "user_type", "is_staff", "is_superuser")

    def clean_email(self):
        return normalize_email(self.cleaned_data["email"])

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_unusable_password()
        if commit:
            user.save()
            self.save_m2m()
        return user


class AdminUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = (
            "email",
            "first_name",
            "last_name",
            "user_type",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )

    def clean_email(self):
        return normalize_email(self.cleaned_data["email"])
