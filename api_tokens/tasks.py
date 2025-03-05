# Library Imports
from celery import shared_task
from django.utils import timezone

# Local Imports
from .models import AccessToken

@shared_task
def revoke_expired_tokens():
    """
    Revoke tokens that have expired.
    
    * This task is run periodically to revoke tokens that have expired.
    """
    print("Revoking expired tokens...")
    expired_tokens = AccessToken.objects.filter(is_revoked=False, expires_at__lte=timezone.now())
    updated_count = expired_tokens.update(is_revoked=True)
    return f"Revoked {updated_count} tokens."

