from .models import StaffProfile
from django import forms


class StaffForm(forms.ModelForm):
    class Meta:
        model = StaffProfile
        fields = [
            'full_name', 'phone_number', 'date_of_birth', 'role', 'employee_number', 'profile_image',
        ]
        widgets = {
            'phone_number': forms.NumberInput(attrs={'type': 'number', 'placeholder': 'Enter phone number'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._staff_form_attributes()

    def _staff_form_attributes(self):
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control mb-2'
            })
        if self.instance and self.instance.employee_number:
            self.fields['employee_number'].disabled = True
            self.fields['role'].disabled = True
