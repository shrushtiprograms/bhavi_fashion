from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Address


class CustomUserCreationForm(UserCreationForm):
    """
    Form for user registration
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone = forms.CharField(required=True, max_length=10)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.role = 'customer'  # Default role is customer
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """
    Form for user login
    """
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class AddressForm(forms.ModelForm):
    """
    Form for adding or updating user addresses
    """
    class Meta:
        model = Address
        fields = ('name', 'phone', 'address_line1', 'address_line2', 'city', 'state', 'pincode', 'is_default')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile
    """
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone', 'profile_image')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
           
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
