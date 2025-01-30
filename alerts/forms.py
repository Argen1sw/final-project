from django import forms
from .models import Alert

class AlertForm(forms.ModelForm):
    class Meta:
        model = Alert
        fields = ['description', 'hazard_type', 'source_url']
        widgets = {
            'description': forms.Textarea(attrs={
                'placeholder': 'Brief description (What is happening, etc.)',
                'rows': 3,
            }),
            'hazard_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'source_url': forms.URLInput(attrs={
                'placeholder': 'Is there any URL reporting this hazard: e.g http://example.com'
            }),
        }
