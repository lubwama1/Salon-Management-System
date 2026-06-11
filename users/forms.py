from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import CustomUser

class UserRegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._form_attributes()

    # password1 = forms.CharField(
    #     widget=forms.PasswordInput(attrs={'class': 'Password'}))
    # password2 = forms.CharField(
    #     widget=forms.PasswordInput(attrs={'class': 'Password'}))

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password1', 'password2', 'profile_image', 'role'
        ]

    def _form_attributes(self):
        placeholders = {
            'username': 'Username',
            'password1': 'Password',
            'password2': 'Password Confirmation',
            'email': 'Email',
        }
        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {'placeholder': placeholders.get(
                    field_name, ''
                )}
            )
            field.help_text = ''
            if field_name == 'profile_image':
                field.widget.attrs.update({
                    'class': 'form-control'
                })
            if field_name == 'username':
                field.widget.attrs['autofocus'] = True
        print(self.fields.keys())


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'username': 'username',
            'password': 'password'
        }
        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    'placeholder': placeholders.get(
                        field_name, ''
                    )
                }
            )