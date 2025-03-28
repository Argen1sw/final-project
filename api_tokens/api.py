# Django Imports
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, mixins
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.throttling import ScopedRateThrottle

# Local Imports
from alerts.models import Alert
from .serializers import ListAlertSerializer, CreateAlertSerializer

class ListAlertsAPIView(generics.ListAPIView):
    """
    API view to list all alerts.

    * Accepts GET requests.
    * Returns a list of all alerts in JSON format.
    """
    queryset = Alert.objects.all()
    serializer_class = ListAlertSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CreateAlertAPIView(generics.GenericAPIView,
                         mixins.CreateModelMixin):
    """
    API view to create an alert.

    * Request limit is 10 per day per user token.
    
    **Supported alert types and its fields:**
      - **earthquake**: hazard_data: {magnitude:number, depth:number, epicenter_description:string}.
      - **flood**: hazard_data: {severity:low||moderate||major, water_level:number(meters), is_flash_flood:boolean}.
      - **tornado**: hazard_data: {category:EF0 up to EF5, damage_description:string}.
      - **fire**: hazard_data: {fire_intensity:low||moderate||high, is_contained:boolean, cause:string}.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CreateAlertSerializer
    throttle_classes = [ScopedRateThrottle] # Throttle to limit the number of requests for this endpoint
    throttle_scope = 'create_alert' # Scope for the throttle class
    
    @swagger_auto_schema(
        responses={201: openapi.Response("Alert created successfully"), 400: "Bad Request"}
    )

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)