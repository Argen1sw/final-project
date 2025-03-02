# Python Imports
from datetime import datetime, timedelta

# Django Imports
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views import View
from django.views.generic import TemplateView
from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.utils import timezone


# Local Imports
from .models import AccessToken

# What is next?
# 6. Add pagination to the list of tokens.
# 7. Add a search bar to search for tokens.


class ListTokensView(LoginRequiredMixin, TemplateView):
    """
    View to list and manage access tokens (devices) for the current user.

    - Admin and ambassador users see tokens for all users.
    - Normal users see only their own tokens.
    - All users can generate a new token.
    """
    template_name = 'api_tokens/device_manager.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # If the user is an admin or ambassador, show all tokens; otherwise, show only their tokens.
        if not user.is_admin() and not user.is_ambassador():
            context['access_tokens'] = AccessToken.objects.filter(
                user=user).order_by('-created_at')
        else:
            context['access_tokens'] = AccessToken.objects.all().order_by(
                '-created_at')
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to generate a new token.

        * Requires a device name to generate a token.
        * Expires in 30 days by default if not provided.
        * Expires_at can be set up to 2 years from the current date.
        """
        device_name = request.POST.get('device_name')
        if not device_name:
            messages.error(
                request, "Device name is required to generate a token.", extra_tags='token')
            return redirect(request.path)

        expires_at_input = request.POST.get('expires_at')
        if expires_at_input:
            try:
                expires_at = datetime.strptime(
                    expires_at_input, "%Y-%m-%dT%H:%M")
                expires_at = timezone.make_aware(
                    expires_at, timezone.get_current_timezone())

                # Ensure the expiration date is not more than 2 years from now
                if expires_at > timezone.now() + timedelta(days=730):
                    messages.error(
                        request, "Expiration time cannot exceed 2 years.", extra_tags='token')
                    return redirect("device_manager")

                # Ensure the expiration date is not in the past
                if expires_at < timezone.now():
                    messages.error(
                        request, "Expiration time cannot be in the past.", extra_tags='token')
                    return redirect("device_manager")

            except ValueError:
                messages.error(
                    request, "Invalid expiration time.", extra_tags='token')
                return redirect("device_manager")

        # Create a new token for the current user.
        token = AccessToken.objects.create(
            user=request.user, device_name=device_name, expires_at=expires_at if expires_at_input else None)
        messages.success(
            request, f"New token generated for device '{device_name}': {token.token}", extra_tags='token')
        return redirect(request.path)


class RevokeTokenView(LoginRequiredMixin, View):
    """
    API view to revoke an access token.

    - Normal users can only revoke their own tokens.
    - Admin or ambassador users can revoke any token.
    """

    def post(self, request, token_id):
        token = get_object_or_404(AccessToken, id=token_id)
        user = request.user

        # Check if the token belongs to the requesting user, or if the user has elevated permissions.
        if not user.is_admin() and not user.is_ambassador():
            if token.user != user:
                return Response(
                    {"error": "You do not have permission to revoke this token."},
                    status=status.HTTP_403_FORBIDDEN
                )

        if token.is_revoked:
            token.is_revoked = False
            messages.success(
                request, "Token unrevoked successfully.", extra_tags='token')
        else:
            token.is_revoked = True
            messages.success(
                request, "Token revoked successfully.", extra_tags='token')

        token.save()
        return (redirect('device_manager'))


class DeleteTokenView(LoginRequiredMixin, View):
    """
    API view to delete an access token.

    - Normal users can only delete their own tokens.
    - Admin or ambassador users can delete any token.
    """

    def post(self, request, token_id):
        token = get_object_or_404(AccessToken, id=token_id)
        user = request.user

        # Check if the token belongs to the requesting user, or if the user has elevated permissions.
        if not user.is_admin() and not user.is_ambassador():
            if token.user != user:
                return Response(
                    {"error": "You do not have permission to delete this token."},
                    status=status.HTTP_403_FORBIDDEN
                )

        token.delete()
        messages.success(
            request, "Token deleted successfully.", extra_tags='token')
        return (redirect('device_manager'))
