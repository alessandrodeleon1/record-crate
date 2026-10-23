from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User as DjangoUser
from recordcrate.models import User


class CustomUserCreationForm(UserCreationForm):
    city = forms.CharField(required=False, label="City")
    address = forms.CharField(required=False, label="Address")

    class Meta(UserCreationForm.Meta):
        model = DjangoUser
        fields = UserCreationForm.Meta.fields + ("email",)

    def save(self, commit=True):
        # Save the Django auth user first
        auth_user = super().save(commit=commit)
        if commit:
            # User model created and linked to Django user
            User.objects.create(
                account=auth_user,
                city=self.cleaned_data.get("city"),
                address=self.cleaned_data.get("address")
            )
        return auth_user
