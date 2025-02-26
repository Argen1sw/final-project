# Django imports
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom User model inheriting from Django's AbstractUser.
    
    * User types:
        - 1: normal user
        - 2: ambassador
        - 3: admin
    * username is the primary unique identifier
    * email is required during user creation
    """
    USER_TYPE_CHOICES = (
        (1, 'normal user'),
        (2, 'ambassador'),
        (3, 'admin'),
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    user_type = models.PositiveSmallIntegerField(
        choices=USER_TYPE_CHOICES, default=1)
    email = models.EmailField(blank=False, null=False)
    bio = models.TextField(
        blank=True, help_text="A brief description about the user.")
    alerts_created = models.PositiveIntegerField(
        default=0, help_text="Number of alerts created by the user.")
    alerts_verified = models.PositiveIntegerField(
        default=0, help_text="Number of alerts verified by the user.")
    # notification_preferences = models.JSONField(default=dict, null=True, help_text="User preferences for notifications.")

    # Enhanced Security
    is_verified = models.BooleanField(
        default=False, help_text="Indicates if the user's email is verified.")
    is_suspended = models.BooleanField(
        default=False, help_text="Indicates if the user's account is suspended.")

    # Keep username as the primary unique identifier
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']  # Require email during user creation

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

    def is_normal_user(self):
        return self.user_type == 1

    def is_ambassador(self):
        return self.user_type == 2

    def is_admin(self):
        return self.user_type == 3
