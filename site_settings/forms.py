
from django import forms
from .models import SiteSettings


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = ['site_name', 'site_email', 'site_logo',
                  'site_phonenumber', 'site_address', 'site_description']
        widgets = {
            'site_name': forms.TextInput(attrs={'class': 'form-control mb-2'}),
            'site_email': forms.EmailInput(attrs={'class': 'form-control mb-2'}),
            'site_logo': forms.FileInput(attrs={'class': 'form-control mb-2'}),
            'site_phonenumber': forms.NumberInput(attrs={'class': 'form-control mb-2'}),
            'site_address': forms.TextInput(attrs={'class': 'form-control mb-2'}),
            'site_description': forms.Textarea(attrs={'class': 'form-control mb-2', 'style': 'resize: none;', 'rows': 5}),
        }
