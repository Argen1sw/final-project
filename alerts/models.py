# Python Imports

# Django Imports
from django.contrib.gis.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now
from django.core.validators import MaxValueValidator
from datetime import timedelta

# Local Imports
from users.models import User


class Alert(models.Model):
    """
    Alert model to store information about alerts.

    * Soft delete mechanism: Instead of permanently deleting the record,
    mark it as inactive.
    * If the effect radius is not set, it will be set based on the hazard type.
    * If the deletion time is not set, it will be calculated based on the hazard type.
    * If the hazard type is changed, the deletion time will be recalculated.
    """
    description = models.TextField(null=True, blank=True,
        help_text="A brief description of the alert.")
    location = models.PointField(
        geography=True, help_text="2D geographic location of the alert.")
    effect_radius = models.PositiveIntegerField(
        validators=[MaxValueValidator(100000)],
        help_text="Radius of effect in meters - max: 100 km."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    soft_deletion_time = models.DateTimeField(
        help_text="Calculated time when this alert expires and gets archive.")

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

    # Archive Alert Field
    is_active = models.BooleanField(
        default=True, help_text="Soft-delete flag. If False, the alert is considered Archived.")

    # ContentType Fields for Hazard-Specific Models
    content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    hazard_details = GenericForeignKey('content_type', 'object_id')

    def save(self, *args, **kwargs):
        """
        Override the save method to set default values for the alert.
        
        * If the effect radius is not set, it will be set based on the hazard type.
        * If the deletion time is not set, it will be calculated based on the hazard type.
        """
        hazard_name = self.content_type.model if self.content_type else None

        # Define default values based on the hazard model type
        default_effect_radius = {
            'earthquake': 50000,
            'flood': 10000,
            'tornado': 5000,
            'fire': 5000,
            'storm': 50000
        }

        base_times = {
            'earthquake': timedelta(days=2),
            'flood': timedelta(days=10),
            'tornado': timedelta(days=3),
            'fire': timedelta(days=7),
            'storm': timedelta(days=5),
        }

        if hazard_name:
            if not self.effect_radius:
                self.effect_radius = default_effect_radius.get(
                    hazard_name, 10000)

            if not self.soft_deletion_time or self._state.adding:
                self.soft_deletion_time = now() + base_times.get(hazard_name, timedelta(days=1))
        else:
            # fallback if no hazard is associated yet (We don't want this to happen)
            if not self.effect_radius:
                self.effect_radius = 10000
            if not self.soft_deletion_time or self._state.adding:
                self.soft_deletion_time = now() + timedelta(days=1)

        super().save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        """
        Override the delete method to handle the associated hazard instance.
        """
        # Delete the associated hazard instance if it exists.
        if self.content_type and self.object_id:
            try:
                hazard_instance = self.content_type.get_object_for_this_type(pk=self.object_id)
                hazard_instance.delete()
            except self.content_type.model_class().DoesNotExist:
                pass
        return super().delete(*args, **kwargs)
    
    def __str__(self):
        hazard_str = self.content_type.model if self.content_type else "Unknown"
        return f"{hazard_str} - {self.description[:50]}"


class Earthquake(models.Model):
    """
    Model to store information about earthquakes.

    * Fields are all optional.
    """
    magnitude = models.DecimalField(
        max_digits=4, decimal_places=2, blank=True, null=True, help_text="Magnitude of the earthquake.")
    depth = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True, help_text="Depth of the earthquake in kilometers.")
    epicenter_description = models.CharField(
        max_length=255, blank=True, null=True, help_text="Description of the epicenter.")

    def __str__(self):
        return f"Earthquake (Magnitude: {self.magnitude}, Depth: {self.depth} km)"


class Flood(models.Model):
    """
    Model to store information about floods.

    * Fields are all optional.
    """

    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('major', 'Major'),
    ]

    severity = models.CharField(
        max_length=20, choices=SEVERITY_CHOICES, blank=True, null=True,
        help_text="Severity of the flood."
    )
    water_level = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True, help_text="Water level in meters.")
    is_flash_flood = models.BooleanField(
        default=False, help_text="Indicates if it is a flash flood.")

    def __str__(self):
        return f"Flood (Severity: {self.severity}, Water Level: {self.water_level} m)"


class Tornado(models.Model):
    """
    Model to store information about tornadoes.

    * Fields are all optional.
    """
    CATEGORY_CHOICES = [
        ('EF0', 'EF0'),
        ('EF1', 'EF1'),
        ('EF2', 'EF2'),
        ('EF3', 'EF3'),
        ('EF4', 'EF4'),
        ('EF5', 'EF5'),
    ]
    category = models.CharField(
        max_length=3, choices=CATEGORY_CHOICES, blank=True, null=True,
        help_text="Category of the tornado."
    )

    damage_description = models.TextField(
        blank=True, null=True, help_text="Description of the damage caused.")

    def __str__(self):
        return f"Tornado (Category: {self.category})"


class Fire(models.Model):
    """
    Model to store information about fires.

    * Fields are all optional.    
    """
    FIRE_INTENSITY_CHOICES = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
    ]

    fire_intensity = models.CharField(
        max_length=20, choices=FIRE_INTENSITY_CHOICES, blank=True, null=True,
        help_text="Intensity of the fire."
    )
    is_contained = models.BooleanField(
        default=False, help_text="Indicates if the fire is contained.")
    cause = models.CharField(max_length=255, blank=True,
                             null=True, help_text="Possible cause of the fire.")

    def __str__(self):
        return f"Fire (Intensity: {self.fire_intensity}, Contained: {self.is_contained})"

class AlertUserVote(models.Model):
    """
    Model to store user votes on alerts.
    """
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vote = models.BooleanField(
        help_text="True: Upvote, False: Downvote.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'alert')

    def __str__(self):
        return f"{self.user.username} - {self.alert.id} - {self.vote}"