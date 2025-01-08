from rest_framework.viewsets import ModelViewSet
from .models import Alert
from .serializers import AlertSerializer, CreateAlertSerializer
from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.gis.geos import Point
from rest_framework_gis.pagination import GeoJsonPagination
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from geopy.geocoders import Nominatim

import logging
logger = logging.getLogger(__name__)


class AlertViewSet(ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    pagination_class = GeoJsonPagination


def map_view(request):
    return render(request, 'alerts/map.html')

def home_view(request):
    return render(request, 'alerts/home.html')

def resources_view(request):
    return render(request, 'alerts/resources.html')

def guide_example_view(request):
    return render(request, 'alerts/guide_example.html')

def about_view(request):
    return render(request, 'alerts/about.html')

def login_view(request):
    return render(request, 'alerts/login.html')

class CreateAlertView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        
        # Validate input data
        lat = data.get('lat')
        lng = data.get('lng')

        if lat is None or lng is None:
            return Response({"error": "Latitude and Longitude are required."}, status=400)

        try:
            lat = float(lat)
            lng = float(lng)
        except ValueError:
            return Response({"error": "Latitude and Longitude must be valid numbers."}, status=400)

        # Reverse Geocoding
        try:
            geolocator = Nominatim(user_agent="enviroalerts")
            location = geolocator.reverse((lat, lng), language="en")
            address = location.raw.get('address', {})
        except Exception as e:
            return Response({"error": f"Geocoding failed: {str(e)}"}, status=400)

        # Create alert
        try:
            alert = Alert.objects.create(
                title=data['title'],
                description=data.get('description', ''),
                location=Point(float(data['lng']), float(data['lat'])),
                hazard_type=data.get('hazard_type', 'other'),
                severity=data.get('severity', None),
                reported_by=data.get('reported_by', None), 
                source_url=data.get('source_url', None),    
                country=address.get('country', ''),
                city=address.get('city', address.get('town', '')),
                county=address.get('county', '')
            )
            return Response({
                "id": alert.id,
                "title": alert.title,
                "description": alert.description,
                "location": {
                    "type": "Point",
                    "coordinates": [alert.location.x, alert.location.y]
                },
                "hazard_type": alert.hazard_type,
                "severity": alert.severity,
                "reported_by": alert.reported_by,
                "source_url": alert.source_url,
                "country": alert.country,
                "city": alert.city,
                "county": alert.county,
                "created_at": alert.created_at
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": f"Error creating Alert: {str(e)}"}, status=400)
