# Library Imports
from celery import shared_task
from django.utils.timezone import now

# Local Imports
from .models import Alert


@shared_task
def deactivate_expired_alerts():
    """
    Deactivate alerts that have expired.

    * This task is run periodically to deactivate alerts that have expired.
    """
    print("Deactivating expired alerts...")
    expired_alerts = Alert.objects.filter(
        is_active=True, soft_deletion_time__lte=now())
    updated_count = expired_alerts.update(is_active=False)
    return f"Deactivated {updated_count} alerts."
