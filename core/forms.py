from django import forms
from .models import Contact


class ContactForm(forms.ModelForm):
    """Form for user contact submissions."""

    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
        widget = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Message Subject'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Your message here...',
                'rows': 5
            }),
        }
