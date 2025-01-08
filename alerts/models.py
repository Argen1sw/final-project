from django.contrib.gis.db import models


# I will need to expand on this model:
# - Which info is important to display and the user needs to know?
# A few ideas:
#   Country name,
#   type of hazard (drop down list),
#
#
#   Each alert type will be set to a specific time to get cleared out
#   Automatically, For instance for earthquake the time would 2 days.
#   Floods 10 days and so on.

class Alert(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.PointField(geography=True)
    created_at = models.DateTimeField(auto_now_add=True)

    HAZARD_TYPES = [
        ('earthquake', 'Earthquake'),
        ('flood', 'Heavy Flood'),
        ('tornado', 'Tornado'),
        ('fire', 'Fire'),
        ('storm', 'Storm'),
    ]
    hazard_type = models.CharField(max_length=20, choices=HAZARD_TYPES,
                                   default='other')

    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    county = models.CharField(max_length=100, blank=True, null=True)
    severity = models.IntegerField(blank=True, null=True)
    reported_by = models.CharField(max_length=100, blank=True, null=True)
    source_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.hazard_type})"
