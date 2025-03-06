# Libraries/Framworks Imports
from django import forms

# Local Imports
from .models import Alert


class AlertForm(forms.ModelForm):
    """
    Form class that handles alert creation and updates.
    """
    # This form should also create a hazard type field
    # So it will also extract the hazard type and its details from the alert in the view?
     
    class Meta:
        model = Alert
        
        fields = ['description', 'location', 'effect_radius',
                  'country', 'city', 'county', 'source_url']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'location': forms.HiddenInput(),
            'effect_radius': forms.NumberInput(attrs={'min': 0, 'max': 100000}),
            'country': forms.TextInput(attrs={'placeholder': 'Country'}),
            'city': forms.TextInput(attrs={'placeholder': 'City'}),
            'county': forms.TextInput(attrs={'placeholder': 'County'}),
            'source_url': forms.URLInput(attrs={'placeholder': 'Source URL'})
        }
