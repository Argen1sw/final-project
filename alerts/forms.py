# Python Imports
from datetime import timedelta

# Libraries/Frameworks Imports
from django import forms
from django.utils import timezone

# Local Imports
from .models import Alert, Earthquake, Flood, Tornado, Fire

# Create a registry to map hazard models to their form classes.
HAZARD_FORM_REGISTRY = {}


def register_hazard_form(model_class):
    """Decorator to register a hazard ModelForm for a hazard model."""
    def wrapper(form_class):
        HAZARD_FORM_REGISTRY[model_class] = form_class
        return form_class
    return wrapper


@register_hazard_form(Earthquake)
class EarthquakeForm(forms.ModelForm):
    class Meta:
        model = Earthquake
        fields = ['magnitude', 'depth', 'epicenter_description']


@register_hazard_form(Flood)
class FloodForm(forms.ModelForm):
    class Meta:
        model = Flood
        fields = ['severity', 'water_level', 'is_flash_flood']


@register_hazard_form(Tornado)
class TornadoForm(forms.ModelForm):
    class Meta:
        model = Tornado
        fields = ['category', 'damage_description']


@register_hazard_form(Fire)
class FireForm(forms.ModelForm):
    class Meta:
        model = Fire
        fields = ['fire_intensity', 'is_contained', 'cause']


class AlertForm(forms.ModelForm):
    """
    AlertForm dynamically injects the hazard detail fields based on the associated hazard instance.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hazard_form = None

        hazard = self.instance.hazard_details if self.instance else None

        if hazard:
            hazard_form_class = HAZARD_FORM_REGISTRY.get(type(hazard))

            if hazard_form_class:
                # Instantiate the hazard form for the existing hazard instance
                self.hazard_form = hazard_form_class(instance=hazard)
                # Add the hazard form fields to this alert form
                for field_name, field in self.hazard_form.fields.items():
                    self.fields[field_name] = field
                    self.initial[field_name] = getattr(
                        hazard, field_name, None)

    class Meta:
        model = Alert

        fields = ['description', 'effect_radius', 'soft_deletion_time',
                  'country', 'city', 'county', 'source_url']

        labels = {
            'description': 'Alert Description',
            'effect_radius': 'Impact Radius (meters)',
            'soft_deletion_time': 'Expiration Time',
        }
        
        help_texts = {
            'effect_radius': 'Enter the effect radius (in meters, max 100000)',
            'soft_deletion_time': 'Select a time no more than 10 days from now',
            'country': 'Enter the country.',
            'city': 'Enter the city',
            'county': 'Enter the county',
            'source_url': 'Enter the source URL for the alert',
        }
        
        error_messages = {
            'effect_radius': {
                'max_value': "The effect radius must be less than or equal to 100000 meters.",
            },
        }
        
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, }),
            'effect_radius': forms.NumberInput(attrs={'min': 0, 'max': 100000}),
            'soft_deletion_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'country': forms.TextInput(attrs={'placeholder': 'Country'}),
            'city': forms.TextInput(attrs={'placeholder': 'City'}),
            'county': forms.TextInput(attrs={'placeholder': 'County'}),
            'source_url': forms.URLInput(attrs={'placeholder': 'Source URL'}),
        }

    def clean_soft_deletion_time(self):
        soft_deletion_time = self.cleaned_data.get('soft_deletion_time')
        if soft_deletion_time:
            now = timezone.now()
            # Allow a maximum of 10 days from now (or from the updated time)
            max_allowed_date = now + timedelta(days=10)
            if soft_deletion_time > max_allowed_date:
                raise forms.ValidationError(
                    "The soft deletion time cannot be more than 10 days from now."
                )
        return soft_deletion_time
    
    def save(self, commit=True):
        alert = super().save(commit=False)
        hazard = alert.hazard_details

        if hazard and self.hazard_form:
            # Update hazard details using the cleaned data from the alert form.
            for field_name in self.hazard_form.fields:
                setattr(hazard, field_name, self.cleaned_data.get(field_name))
            hazard.save()

        if commit:
            alert.save()
        return alert
