# Django Imports
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Local Imports
from alerts.models import (Alert, Earthquake, Flood, Fire, Tornado)

class CreateAlertAPIView(APIView):
    """
    API view to create an alert.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Create an alert.
        """
        alert_type = request.data.get('alert_type')
        if alert_type == 'earthquake':
            magnitude = request.data.get('magnitude')
            depth = request.data.get('depth')
            alert = Earthquake.objects.create(
                magnitude=magnitude, depth=depth)
        elif alert_type == 'flood':
            severity = request.data.get('severity')
            water_level = request.data.get('water_level')
            is_flash_flood = request.data.get('is_flash_flood')
            alert = Flood.objects.create(
                severity=severity, water_level=water_level, is_flash_flood=is_flash_flood)
        elif alert_type == 'tornado':
            category = request.data.get('category')
            damage_description = request.data.get('damage_description')
            alert = Tornado.objects.create(
                category=category, damage_description=damage_description)
        elif alert_type == 'fire':
            alert = Fire.objects.create()
        else:
            return Response({'error': 'Invalid alert type'}, status=status.HTTP_400_BAD_REQUEST)
        Alert.objects.create(alert=alert, user=request.user)
        return Response({'message': 'Alert created successfully'}, status=status.HTTP_201_CREATED)
    
    

 