from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')


class CustomUserLoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput)


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('bio', 'avatar', 'username', 'title')

    def clean(self):
        cleaned_data = super().clean()

        if not self.cleaned_data['avatar']:
            cleaned_data['avatar'] = self.instance.avatar
        if not self.cleaned_data['bio']:
            cleaned_data['bio'] = self.instance.bio
        if not self.cleaned_data['username']:
            cleaned_data['username'] = self.instance.username
        if not self.cleaned_data['title']:
            cleaned_data['title'] = self.instance.title

        return cleaned_data
