

from django import forms
from datetime import time
from .models import AdminAppointmentApproval, AdminProfile
from users.models import CustomUser

class AdminAppointmentApprovalForm(forms.ModelForm):
    approved_time_slot = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'min': '08:00',
            'max': '22:00',
            'class': 'form-control',
        }),
        input_formats=['%H:%M', '%H:%M:%S'],
        help_text="Select time between 08:00 and 22:00",
        required=False,
    )
    cancellation_reason = forms.ChoiceField(
        choices=AdminAppointmentApproval.CANCELLED_REASON.choices,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        error_messages={'required': 'Please select a cancellation reason.'},
    )

    class Meta:
        model = AdminAppointmentApproval
        fields = ['approved_time_slot', 'status', 'cancellation_reason']
        widgets = {
            # 'assigned_staff': forms.HiddenInput(),
            'status': forms.Select(),
        }

    def clean_approved_time_slot(self):
        approved_time_slot = self.cleaned_data.get('approved_time_slot')

        if approved_time_slot and (approved_time_slot < time(8, 0) or approved_time_slot > time(22, 0)):
            raise forms.ValidationError(
                "Please select a time between 08:00 and 22:00."
            )
        return approved_time_slot

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control mb-2'
            })

        if user:
            if user.role == CustomUser.UserRoleChoices.ADMIN:
                admin_reasons = [
                    ('admin_cancelled', 'Admin Cancelled'),
                    ('no_show', 'Client did not show up')
                ]
                self.fields['cancellation_reason'].choices = admin_reasons
            else:
                customer_reasons = [
                    ('customer_request', 'Customer Request'),
                    ('busy_schedule', 'Busy Schedule'),
                    ('found_another', 'Found Another Service Provider'),
                    ('other', 'Other Reason')
                ]
                self.fields['cancellation_reason'].choices = customer_reasons

class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = AdminProfile
        fields = [
            'full_name', 'phone_number', 'employee_number',  'admin_profile_image'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._update_attributes()

    def _update_attributes(self):
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control mb-2'
            })
