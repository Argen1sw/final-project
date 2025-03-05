# Python Imports
import secrets

# Django Imports
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class AccessToken(models.Model):
    """
    Access token model to store information about access tokens.

    * Token is generated automatically if not provided.
    * Expiration time is set to 30 days if not provided.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='access_tokens',
        on_delete=models.CASCADE,
        help_text="User associated with the token"
    )
    device_name = models.CharField(
        max_length=100, help_text="Identifier for the device")
    token = models.CharField(max_length=64, unique=True,
                             editable=False, help_text="Access token")
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Creation time of the token")
    expires_at = models.DateTimeField(help_text="Expiration time of the token")
    is_revoked = models.BooleanField(
        default=False, help_text="Revocation status")

    def save(self, *args, **kwargs):
        # Generate token if not already set
        if not self.token:
            self.token = secrets.token_hex(32)  # 64 characters
        # Set a default expiration if not provided
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=30)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.device_name} token"