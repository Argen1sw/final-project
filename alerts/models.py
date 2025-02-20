
from django.contrib.gis.db import models

# New modules
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now
from datetime import timedelta
from users.models import User
from django.core.validators import MinValueValidator

#
class HazardType(models.TextChoices):
    EARTHQUAKE = 'earthquake', 'Earthquake'
    FLOOD = 'flood', 'Flood'
    TORNADO = 'tornado', 'Tornado'
    FIRE = 'fire', 'Fire'
    STORM = 'storm', 'Storm'

#
class Alert(models.Model):

    description = models.TextField(
        help_text="A brief description of the alert.")
    location = models.PointField(
        geography=True, help_text="2D geographic location of the alert.")
    effect_radius = models.PositiveIntegerField(
        help_text="Radius of effect in meters"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deletion_time = models.DateTimeField(
        null=True, blank=True, help_text="Calculated time when this alert expires.")

    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    county = models.CharField(max_length=100, blank=True, null=True)

    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                    null=True, blank=True, help_text="User who created the alert.")

    source_url = models.URLField(
        blank=True, null=True, help_text="Source of information about the alert.")
    positive_votes = models.PositiveIntegerField(
        default=0, help_text="Number of positive votes.")
    negative_votes = models.PositiveIntegerField(
        default=0, help_text="Number of negative votes.")
    
    hazard_type = models.CharField(
        max_length=20,
        choices=HazardType.choices,
        db_index=True,
        help_text="Type of hazard."
    )
    
    # Soft Delete Field
    is_active = models.BooleanField(
        default=True, help_text="Soft-delete flag. If False, the alert is considered deleted.")

    # ContentType Fields for Hazard-Specific Models
    content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    hazard_details = GenericForeignKey('content_type', 'object_id')


    def save(self, *args, **kwargs):
        """
         - Recalculate deletion_time if it's a new record, 
         or if hazard_type changed, or if deletion_time is not set.
        """
        if not self.effect_radius:
            self.effect_radius = {
                'earthquake': 50000,
                'flood': 10000,
                'tornado': 5000,
                'fire': 5000,
                'storm': 50000
            }.get(self.hazard_type)

        base_times = {
            'earthquake': timedelta(days=2),
            'flood': timedelta(days=10),
            'tornado': timedelta(days=3),
            'fire': timedelta(days=7),
            'storm': timedelta(days=5),
        }

        # Check if this is an existing record
        if self.pk:
            # Fetch the currently stored hazard_type from the database
            old_hazard_type = (
                Alert.objects
                .filter(pk=self.pk)
                .values_list('hazard_type', flat=True)
                .first()
            )
            hazard_type_changed = (old_hazard_type != self.hazard_type)
        else:
            hazard_type_changed = False

        # Decide if we need to recalculate deletion_time
        if not self.deletion_time or self._state.adding or hazard_type_changed:
            # Fallback of 1 day if hazard_type is somehow invalid/unknown
            self.deletion_time = now() + base_times.get(self.hazard_type, timedelta(days=1))

        super().save(*args, **kwargs)

    def soft_delete(self):
        """
        Instead of permanently deleting the record, mark it as inactive.
        """
        self.is_active = False
        self.save(update_fields=['is_active'])

    def __str__(self):
        return f"{self.hazard_type} - {self.description[:50]}"

#
class Earthquake(models.Model):
    magnitude = models.DecimalField(
        max_digits=4, decimal_places=2, help_text="Magnitude of the earthquake.")
    depth = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Depth of the earthquake in kilometers.")
    epicenter_description = models.CharField(
        max_length=255, blank=True, null=True, help_text="Description of the epicenter.")

    def __str__(self):
        return f"Earthquake (Magnitude: {self.magnitude}, Depth: {self.depth} km)"

#
class Flood(models.Model):
    water_level = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Water level in meters.")
    affected_area = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Affected area in square kilometers.")
    is_flash_flood = models.BooleanField(
        default=False, help_text="Indicates if it is a flash flood.")

    def __str__(self):
        return f"Flood (Water Level: {self.water_level}m, Flash Flood: {self.is_flash_flood})"

#
class Tornado(models.Model):
    wind_speed = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Wind speed in km/h.",
        validators=[MinValueValidator(0)],)
    damage_description = models.TextField(
        blank=True, null=True, help_text="Description of the damage caused.")

    def __str__(self):
        return f"Tornado (Wind Speed: {self.wind_speed} km/h)"

# 
class Fire(models.Model):
    affected_area = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Affected area in square kilometers.")
    is_contained = models.BooleanField(
        default=False, help_text="Indicates if the fire is contained.")
    cause = models.CharField(max_length=255, blank=True,
                             null=True, help_text="Possible cause of the fire.")

    def __str__(self):
        return f"Fire (Affected Area: {self.affected_area} sq km, Contained: {self.is_contained})"

# 
class Storm(models.Model):
    wind_speed = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Wind speed in km/h.")
    rainfall = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Rainfall in mm.")
    storm_category = models.IntegerField(
        blank=True, null=True, help_text="Category of the storm.")

    def __str__(self):
        return f"Storm (Category: {self.storm_category}, Wind Speed: {self.wind_speed} km/h)"



