from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import CustomUser
from allauth.account.forms import SignupForm # type: ignore

class UserRegistrationForm(SignupForm):
    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control'
        })
    )

    role = forms.ChoiceField(
        choices=CustomUser.UserRoleChoices.choices,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg rounded-3 border-2'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholders = {
            'username': 'Username',
            'email': 'Email',
            'password1': 'Password',
            'password2': 'Confirm Password',
        }

        for field_name, field in self.fields.items():
            field.help_text = ''

            if field_name not in ['role', 'profile_image']:
                field.widget.attrs.update({
                    'placeholder': placeholders.get(field_name, ''),
                    'class': 'form-control form-control-lg rounded-3 border-2'
                })

            if field_name == 'username':
                field.widget.attrs['autofocus'] = True

    def save(self, request):
        user = super().save(request)

        user.profile_image = self.cleaned_data.get('profile_image')

        role = self.cleaned_data.get('role')
        user.role = role if role else CustomUser.UserRoleChoices.CUSTOMER

        user.save()
        return user
# class UserRegistrationForm(UserCreationForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self._form_attributes()

#     # password1 = forms.CharField(
#     #     widget=forms.PasswordInput(attrs={'class': 'Password'}))
#     # password2 = forms.CharField(
#     #     widget=forms.PasswordInput(attrs={'class': 'Password'}))

#     class Meta:
#         model = CustomUser
#         fields = [
#             'username', 'email', 'password1', 'password2', 'profile_image', 'role'
#         ]

#     def _form_attributes(self):
#         placeholders = {
#             'username': 'Username',
#             'password1': 'Password',
#             'password2': 'Password Confirmation',
#             'email': 'Email',
#         }
#         for field_name, field in self.fields.items():
#             field.widget.attrs.update(
#                 {'placeholder': placeholders.get(
#                     field_name, ''
#                 )}
#             )
#             field.help_text = ''
#             if field_name == 'profile_image':
#                 field.widget.attrs.update({
#                     'class': 'form-control'
#                 })
#             if field_name == 'username':
#                 field.widget.attrs['autofocus'] = True
#         print(self.fields.keys())


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