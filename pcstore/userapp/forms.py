from django import forms
from django.contrib.auth import get_user_model
from .models import Address  # Make sure to import your Address model

User = get_user_model()

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'mobile','username']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'peronalinfofirstnameinput', 'placeholder': 'first_name'}),
            'last_name': forms.TextInput(attrs={'class': 'peronalinfolastnameinput', 'placeholder': 'last_name'}),
            'email': forms.TextInput(attrs={'class': 'personalinfoemailinput', 'placeholder': 'email'}),
            'mobile': forms.NumberInput(attrs={'class': 'personalinfomobileinput', 'placeholder': 'mobile'}),
            'username': forms.TextInput(attrs={'class': 'personalinfomobileinput', 'placeholder': 'username'}),
        }

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['flat_house', 'area_street', 'landmark', 'pincode', 'town_city', 'state', 'fullname', 'mobile']
        widgets = {
            'flat_house': forms.TextInput(attrs={'class': 'address-input', 'placeholder': 'Flat/House No.'}),
            'area_street': forms.TextInput(attrs={'class': 'address-input', 'placeholder': 'Area/Street'}),
            'landmark': forms.TextInput(attrs={'class': 'address-input', 'placeholder': 'Landmark (Optional)'}),
            'pincode': forms.TextInput(attrs={'class': 'address-input', 'placeholder': 'Pincode'}),
            'town_city': forms.TextInput(attrs={'class': 'address-input', 'placeholder': 'Town/City'}),
            'state': forms.TextInput(attrs={'class': 'address-input', 'placeholder': 'State'}),
            'fullname': forms.TextInput(attrs={'class': 'address-input', 'placeholder': 'Full Name'}),
            'mobile': forms.TextInput(attrs={'class': 'address-input', 'placeholder': 'Mobile Number'}),
        }