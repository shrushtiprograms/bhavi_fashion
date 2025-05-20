from django import forms
from django.core.validators import RegexValidator
from .models import BulkOrder

class BulkOrderForm(forms.ModelForm):
    contact = forms.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message='Phone number must be a 10-digit number.',
                code='invalid_phone'
            )
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter 10-digit phone number'})
    )

    class Meta:
        model = BulkOrder
        fields = [
            'business_name', 'contact_person', 'contact', 'email',
            'budget', 'delivery_timeline', 'shipping_address', 'notes'
        ]
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter business name'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter contact person'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter budget'}),
            'delivery_timeline': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g., 2 weeks'}),
            'shipping_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter shipping address'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Any additional notes'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        budget = cleaned_data.get('budget')
        if budget is not None and budget <= 0:
            self.add_error('budget', 'Budget must be greater than zero.')
        return cleaned_data