from rest_framework.viewsets import ModelViewSet
from .models import Alert
from .forms import AlertForm
from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.gis.geos import Point
from rest_framework_gis.pagination import GeoJsonPagination
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from geopy.geocoders import Nominatim
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from django.urls import reverse_lazy
from rest_framework import generics
from .serializers import AlertGeoSerializer
from django.http import JsonResponse

import logging
logger = logging.getLogger(__name__)


class AlertGeoJsonListView(generics.ListAPIView):
    """
    Returns all active alerts in GeoJSON format.
    """
    queryset = Alert.objects.filter(is_active=True)
    serializer_class = AlertGeoSerializer


class HomeView(TemplateView):
    template_name = "alerts/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


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
            address = location.raw.get('address', {}) if location else {}
        except Exception as e:
            return Response({"error": f"Geocoding failed: {str(e)}"}, status=400)

        # Automatically set `reported_by` to the logged-in user
        current_user = request.user if request.user.is_authenticated else None
        
        # Create alert
        try:
            alert = Alert.objects.create(
                description=data.get('description', ''),
                location=Point(float(data['lng']), float(data['lat'])),
                hazard_type=data.get('hazard_type', 'storm'), # Fallback Storm
                reported_by=current_user, # or None 
                source_url=data.get('source_url', None),    
                country=address.get('country', ''),
                city=address.get('city', address.get('town', '')),
                county=address.get('county', '')
            )
            
            # Build response
            return Response({
                "id": alert.id,
                "description": alert.description,
                "location": {
                    "type": "Point",
                    "coordinates": [alert.location.x, alert.location.y]
                },
                "hazard_type": alert.hazard_type,

                "reported_by":(
                    str(alert.reported_by)
                    if alert.reported_by else None
                ),
                
                "source_url": alert.source_url,
                "country": alert.country,
                "city": alert.city,
                "county": alert.county,
                "created_at": alert.created_at
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"error": f"Error creating Alert: {str(e)}"}, status=400)


class AlertsView(TemplateView):
    template_name = 'alerts/alerts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AlertForm()
        return context




def resources_view(request):
    return render(request, 'alerts/resources.html')

def guide_example_view(request):
    return render(request, 'alerts/guide_example.html')

def about_view(request):
    return render(request, 'alerts/about.html')

def login_view(request):
    return render(request, 'alerts/login.html')