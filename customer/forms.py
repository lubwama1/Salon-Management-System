
# from random import choices

from django import forms
from .models import CustomerAppointment
from datetime import time
from users.models import CustomUser

class AppointmentForm(forms.ModelForm):
    time_slot = forms.TimeField(
        widget=forms.TimeInput(attrs={
                               'type': 'time',
                               'min': '08:00',
                               'max': '22:00',
                               'step': '60',  # Set step to 60 seconds (1 minute) for time selection
                               }),
        input_formats=['%H:%M'], help_text="Select time between 08:00 and 22:00"
    )

    class Meta:
        model = CustomerAppointment
        fields = [
            'full_name', 'email', 'phone_number', 'service', 'appointment_date', 'time_slot',
        ]
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'status': forms.Select(choices=CustomerAppointment.AppointmentStatusChoices),
        }

    def clean_time_slot(self):
        time_slot = self.cleaned_data['time_slot']
        if time_slot < time(8, 0) or time_slot > time(22, 0):
            raise forms.ValidationError(
                "Please select a time between 08:00 and 22:00.")
        return time_slot

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._update_attributes()

    def _update_attributes(self):
        placeholders = {
            'full_name': 'Enter your full name',
            'email': 'Enter your email address',
            'appointment_date': 'Select appointment date',
            'time_slot': 'Enter time (HH:MM)',
        }
        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {'class': 'form-control', 'placeholder': placeholders.get(field_name, field.label)})


class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'phone_number', 'date_of_birth', 'profile_image',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # user = kwargs.get('instance')
        self._profile_fields_attributes()
        # if user:
        #     try:
        #         admin_profile = AdminProfile.objects.get(user=user)
        #         self.fields['employee_number'].initial = admin_profile.employee_number
        #     except AdminProfile.DoesNotExist:
        #         pass
    def _profile_fields_attributes(self):
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'placeholder': f'Enter {field.label}',
                'class': 'form-control mb-2'
            })
            # field.label = ''
