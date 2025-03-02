from rest_framework import authentication, exceptions
from .models import AccessToken
from django.utils import timezone

class CustomTokenAuthentication(authentication.BaseAuthentication):
    keyword = 'Bearer'

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).split()
        if not auth_header or auth_header[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth_header) == 1:
            msg = "Invalid token header. No credentials provided."
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth_header) > 2:
            msg = "Invalid token header. Token string should not contain spaces."
            raise exceptions.AuthenticationFailed(msg)

        try:
            token_key = auth_header[1].decode()
        except UnicodeError:
            msg = "Invalid token header. Token string should not contain invalid characters."
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = AccessToken.objects.get(token=token_key, is_revoked=False)
        except AccessToken.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid or expired token.")

        if token.expires_at < timezone.now():
            raise exceptions.AuthenticationFailed("Token has expired.")

        return (token.user, token)