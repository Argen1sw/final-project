# Standard library imports
from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Local Imports
from .views import (RevokeTokenView, ListTokensView, DeleteTokenView)
from .api import (CreateAlertAPIView, ListAlertsAPIView)

description = """
## Welcome to the EnviroAlert API!

A bearer token is required to access the API. You can generate a token by logging in to the EnviroAlert web app and navigating to the device manager.

**Example code of API usage with an ESP8266:**
```cpp
// Include the required libraries
// API endpoint and token
const char* apiUrl = "https://enviroAlerts/api/list_alerts/";
const char* bearerToken = "YOUR_TOKEN_HERE";

// Add Authorization header with Bearer token
https.addHeader("Authorization", String("Bearer ") + bearerToken);

// Send GET request to the API
int httpResponseCode = https.GET();
if (httpResponseCode > 0) {
    // Success code in here
} else {
    // Error code in here
}
```

**Alert Types Supported:**
- **earthquake**: hazard_data: {magnitude:number, depth:number, epicenter_description:string}.
- **flood**: hazard_data: {severity:low||moderate||major, water_level:number(meters), is_flash_flood:boolean}.
- **tornado**: hazard_data: {category:EF0-5, damage_description:string}.
- **fire**: hazard_data: {fire_intensity:low||moderate||high, is_contained:boolean, cause:string}.

**Example Body to create an Alert:**

```json
{
  "lat": 38.877537,
  "lng": -77.056191,
  "description": "Something happened in DC",
  "hazard_type": "fire",
  "effect_radius": 5000,
  "source_url": "https://www.django-rest-framework.org/api-guide/generic-views/",
  "hazard_data": {
        "fire_intensity":"low",
        "is_contained":"False",
        "cause":"Lightning"
  }
}
```

For any inquiries, please contact us at [argen1swong@gmail.com](mailto:argen1swong@gmail.com)
any other admin or ambassador.

---

"""


# Define only the API endpoints you want to document.
api_urlpatterns = [
    path('api/list_alerts/', ListAlertsAPIView.as_view(), name='list_alerts'),
    path('api/create_alert/', CreateAlertAPIView.as_view(), name='create_alert_api'),
]

schema_view = get_schema_view(
    openapi.Info(
        title="EnviroAlert API",
        default_version='v1',
        description=description,
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=api_urlpatterns,
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
    path('api/list_alerts/', ListAlertsAPIView.as_view(), name='list_alerts'),
    path('api/create_alert/', CreateAlertAPIView.as_view(), name='create_alert_api'),
]
