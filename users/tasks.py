# Library Frameworks import
from celery import shared_task
from django.db.models import Count

# Local Imports
from .models import User


@shared_task
def check_user_achievements():
    """
    Check each user's stats and update user type based on their number of upvotes
    and created alerts.

    mark users as "ambassador" if they have at least 500 upvotes and 20 alerts.
    """
    UPVOTE_THRESHOLD = 500
    ALERTS_THRESHOLD = 20
    updated_users = []

    for user in User.objects.all():
        if user.alerts_upvoted >= UPVOTE_THRESHOLD and user.alerts_created >= ALERTS_THRESHOLD:
            user.user_type = 2
            user.save()
            updated_users.append(user.pk)

    return f"Updated user type for users: {updated_users}"
