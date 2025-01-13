from django.contrib.gis.db import models

# New modules
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth.models import User


class Alert(models.Model):
    
    description = models.TextField(help_text="A brief description of the alert.")
    location = models.PointField(geography=True, help_text="2D geographic location of the alert.")
    created_at = models.DateTimeField(auto_now_add=True)
    deletion_time = models.DateTimeField(null=True, blank=True, help_text="Calculated time when this alert expires.")

    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    county = models.CharField(max_length=100, blank=True, null=True)
    
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, help_text="User who created the alert.")
    
    source_url = models.URLField(blank=True, null=True, help_text="Source of information about the alert.")
    positive_votes = models.PositiveIntegerField(default=0, help_text="Number of positive votes.")
    negative_votes = models.PositiveIntegerField(default=0, help_text="Number of negative votes.")

    # Hazard type and specific details
    hazard_type = models.CharField(max_length=20, choices=[
        ('earthquake', 'Earthquake'),
        ('flood', 'Flood'),
        ('tornado', 'Tornado'),
        ('fire', 'Fire'),
        ('storm', 'Storm'),
    ], help_text="Type of hazard.")

    # ContentType Fields for Hazard-Specific Models
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    hazard_details = GenericForeignKey('content_type', 'object_id')

    
    def save(self, *args, **kwargs):
        if not self.deletion_time:
            base_times = {
                'earthquake': timedelta(days=2),
                'flood': timedelta(days=10),
                'tornado': timedelta(days=3),
                'fire': timedelta(days=7),
                'storm': timedelta(days=5),
            }
            self.deletion_time = now() + base_times.get(self.hazard_type, timedelta(days=1))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.hazard_type} - {self.description[:50]}"

# 
class Earthquake(models.Model):
    magnitude = models.DecimalField(max_digits=4, decimal_places=2, help_text="Magnitude of the earthquake.")
    depth = models.DecimalField(max_digits=5, decimal_places=2, help_text="Depth of the earthquake in kilometers.")
    epicenter_description = models.CharField(max_length=255, blank=True, null=True, help_text="Description of the epicenter.")

    def __str__(self):
        return f"Earthquake (Magnitude: {self.magnitude}, Depth: {self.depth} km)"
    
# 
class Flood(models.Model):
    water_level = models.DecimalField(max_digits=5, decimal_places=2, help_text="Water level in meters.")
    affected_area = models.DecimalField(max_digits=10, decimal_places=2, help_text="Affected area in square kilometers.")
    is_flash_flood = models.BooleanField(default=False, help_text="Indicates if it is a flash flood.")

    def __str__(self):
        return f"Flood (Water Level: {self.water_level}m, Flash Flood: {self.is_flash_flood})"
    

class Tornado(models.Model):
    wind_speed = models.DecimalField(max_digits=5, decimal_places=2, help_text="Wind speed in km/h.")
    damage_description = models.TextField(blank=True, null=True, help_text="Description of the damage caused.")

    def __str__(self):
        return f"Tornado (Wind Speed: {self.wind_speed} km/h)"
    
    
class Fire(models.Model):
    affected_area = models.DecimalField(max_digits=10, decimal_places=2, help_text="Affected area in square kilometers.")
    is_contained = models.BooleanField(default=False, help_text="Indicates if the fire is contained.")
    cause = models.CharField(max_length=255, blank=True, null=True, help_text="Possible cause of the fire.")

    def __str__(self):
        return f"Fire (Affected Area: {self.affected_area} sq km, Contained: {self.is_contained})"
    

class Storm(models.Model):
    wind_speed = models.DecimalField(max_digits=5, decimal_places=2, help_text="Wind speed in km/h.")
    rainfall = models.DecimalField(max_digits=5, decimal_places=2, help_text="Rainfall in mm.")
    storm_category = models.IntegerField(blank=True, null=True, help_text="Category of the storm.")

    def __str__(self):
        return f"Storm (Category: {self.storm_category}, Wind Speed: {self.wind_speed} km/h)"