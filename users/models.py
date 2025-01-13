from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    
    USER_TYPE_CHOICES = (
        (1, 'normal user'),
        (2, 'ambassador'),
        (3, 'admin'),
    )

    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES)
    
    # Override the email field
    email = models.EmailField(unique=True, blank=False, null=False)
    
    # Keep username as the primary unique identifier
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']  # Require email during user creation
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"