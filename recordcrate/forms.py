from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User as DjangoUser
from recordcrate.models import AuthUser, Release, Item


class CustomUserCreationForm(UserCreationForm):
    city = forms.CharField(required=False, label="City")
    address = forms.CharField(required=False, label="Address")

    class Meta(UserCreationForm.Meta):
        model = DjangoUser
        fields = UserCreationForm.Meta.fields + ("email",)

    def save(self, commit=True):
        # Save the Django auth user first
        return super().save(commit=commit)

class ReleaseCreationForm(forms.ModelForm):
    class Meta :
        model = Release
        exclude = ['release_id']

        labels = {
            'title': "Title",
            'genre': "Genre",
            'year': "Year",
            'artist': "Artist",
            'label': "Label",
        }
class SellItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["price", "condition"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["condition"].required = True
