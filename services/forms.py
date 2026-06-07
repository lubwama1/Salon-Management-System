
from django import forms

from .models import ServiceCategory, Service


class ServiceCategoryForm(forms.ModelForm):
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'style': 'resize: none;',
            'placeholder': 'Enter description...'
        })

    )

    name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Enter Category Name'
    }))
    class Meta:
        model = ServiceCategory
        fields = [
            'name', 'description'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._update_attributes()

    def _update_attributes(self):
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control mb-2'
            })


class ServiceForm(forms.ModelForm):
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'style': 'resize: none;',
        })
    )
    price = forms.DecimalField(widget=forms.NumberInput(attrs={
        'step': '0.01',
        'min': '0'
    }))

    class Meta:
        model = Service
        fields = [
            'service_category', 'name', 'description', 'price'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._update_attributes()

    def _update_attributes(self):
        placeholders = {
            'name': 'Service name',
            'description': 'Enter description...',
            'price': 'Enter price',

        }
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control mb-2',
                'placeholder': placeholders.get(field_name, field.label)
            })
