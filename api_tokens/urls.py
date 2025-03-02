# Standard library imports
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated

# Local Imports
from .views import (RevokeTokenView, ListTokensView, DeleteTokenView)
from .api import CreateAlertAPIView

# Define only the API endpoints you want to document.
api_urlpatterns = [
    path('create_alert/', CreateAlertAPIView.as_view(), name='create_alert'),
]

schema_view = get_schema_view(
    openapi.Info(
        title="EnviroAlert API",
        default_version='v1',
        # description=description,
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=api_urlpatterns,  # Include API URLs
)

urlpatterns = [

    path('device_manager/', ListTokensView.as_view(), name='device_manager'),
    path('token_revoke/<int:token_id>/',
         RevokeTokenView.as_view(), name='token_revoke'),
    path('token_delete/<int:token_id>/',
         DeleteTokenView.as_view(), name='token_delete'),

    path(
        'api/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    path(
        'api/redoc/',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),
]
