
from django import forms
from .models import Contact, TeamMember


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['full_name', 'email', 'message']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your Message Here', 'rows': 5, 'style': 'resize:none;'}),
        }


class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = [
            'name', 'role', 'email', 'bio', 'years_of_experience', 'instagram', 'twitter', 'tiktok', 'github', 'is_active', 'image'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your Full Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Your Email'}),
            'bio': forms.Textarea(attrs={'placeholder': 'Your bio Here', 'rows': 5, 'style': 'resize:none;'}),
            'years_of_experience': forms.DateInput(attrs={'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control mb-2'
            })
