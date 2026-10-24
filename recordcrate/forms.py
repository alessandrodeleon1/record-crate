from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User as DjangoUser
from recordcrate.models import AuthUser, Release


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
            AuthUser.objects.get_or_create(
                account=auth_user,
                city=self.cleaned_data.get("city"),
                address=self.cleaned_data.get("address"),
            )
        return auth_user

class ReleaseCreationForm(forms.ModelForm):
    # enter data for all fields except release_id

    # title = forms.CharField(required=True, label="Title")
    # genre = forms.CharField(required=False, label="Genre")
    # year = forms.GetIntegerField(required=False, label="Year")
    # media_format = forms.GetIntegerField(required=False, label="Genre")
    # artist = forms.GetCharField(required=False, label="Artist")
    # label = forms.GetCharField(required=False, label="Label")

    class Meta:
        model = Release
        exclude = ['release_id']

        labels ={
            'title': "Title",
            'genre': "Genre",
            'year': "Year",
            'artist': "Artist",
            'label': "Label",
        }
