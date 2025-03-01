# Standard Library Imports
import logging

# Django Imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.gis.geos import Point
from geopy.geocoders import Nominatim
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from rest_framework import generics
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.forms.models import model_to_dict

# Local Imports
from .serializers import AlertGeoSerializer
from .models import (Alert, Earthquake, Flood, Tornado, Fire) 

# Simple mapping of hazard types to model names
# This is a temporary solution and should be replaced with a more robust solution
# in the future.
HAZARD_MODEL_MAPPING = {
    'earthquake': Earthquake,
    'flood': Flood,
    'tornado': Tornado,
    'fire': Fire,
}

class HomeView(TemplateView):
    """
    View class for the home page.

    * Displays the home page with the latest alerts.
    * Paginates the alerts for the list of alerst element.
    """
    template_name = "alerts/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        alerts = Alert.objects.all().order_by('-created_at')
        paginator = Paginator(alerts, 4)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        # Inject hazard type information on each alert
        for alert in page_obj:
            alert.hazard_type = alert.content_type.model if alert.content_type else None
            alert.hazard_details_dict = model_to_dict(alert.hazard_details) if alert.hazard_details else None
            del alert.hazard_details_dict['id']
            for key in alert.hazard_details_dict:
                if alert.hazard_details_dict[key] is None:
                    alert.hazard_details_dict[key] = "N/A"
        context['page_obj'] = page_obj
        return context


class ManageAlertsView(LoginRequiredMixin, TemplateView):
    """
    View class for the manage alerts page.

    * Displays the manage alerts page with all alerts.
    * Paginates the alerts for the list of alerts element.
    """
    template_name = 'alerts/manage_alerts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        alerts = Alert.objects.all().order_by('-created_at')
        paginator = Paginator(alerts, 4)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        # Inject hazard type information on each alert
        for alert in page_obj:
            alert.hazard_type = alert.content_type.model if alert.content_type else None
            alert.hazard_details_dict = model_to_dict(alert.hazard_details) if alert.hazard_details else None
            del alert.hazard_details_dict['id']
            for key in alert.hazard_details_dict:
                if alert.hazard_details_dict[key] is None:
                    alert.hazard_details_dict[key] = "Not Provided"
        context['page_obj'] = page_obj
        return context
    

class AlertGeoJsonListView(generics.ListAPIView):
    """
    Returns all active alerts in GeoJSON format along with the hazard type and details.

    * Alerts are filtered by the `is_active` field.
    """
    queryset = Alert.objects.filter(is_active=True)
    serializer_class = AlertGeoSerializer


class CreateAlertView(LoginRequiredMixin, APIView):
    """
    API View class to create a new alert.

    * Only authenticated users can create alerts.
    * Alerts are created using the POST method.
    * Returns the alert data in JSON format for the AJAX request.
    """

    def post(self, request, *args, **kwargs):
        """
        Create a new alert.

        * Validates the input data.
        * Reverse geocodes the latitude and longitude.
        """
        data = request.data

        # Validate input data
        lat = data.get('lat')
        lng = data.get('lng')
        if lat is None or lng is None:
            return Response({"error": "Latitude and Longitude are required."}, status=400)

        # Reverse Geocoding
        try:
            geolocator = Nominatim(user_agent="enviroalerts")
            location = geolocator.reverse((lat, lng), language="en")
            address = location.raw.get('address', {}) if location else {}
        except Exception as e:
            return Response({"error": f"Geocoding failed: {str(e)}"}, status=400)

        # Automatically set `reported_by` to the logged-in user
        current_user = request.user if request.user.is_authenticated else None

        # Handles the Hazard type 
        hazard_model_name = data.get('hazard_type')
        hazard_data = data.get('hazard_data', {})
        content_type = None
        object_id = None
        
        # Preprocess hazard_data to ensure no empty strings are passed to the model
        hazard_data = {
            key: (value if not (isinstance(value, str) and value.strip() == "") else None)
            for key, value in hazard_data.items()
        }
        
        if hazard_model_name:
            model_class = HAZARD_MODEL_MAPPING.get(hazard_model_name.lower())
            if not model_class:
                return Response({"error": "Invalid hazard type."}, status=400)
            try:
                hazard_instance = model_class.objects.create(**hazard_data)
                content_type = ContentType.objects.get_for_model(model_class)
                object_id = hazard_instance.id
                
            except Exception as e:
                print("Error creating Hazard:", str(e))
                return Response({"error": f"Error creating Hazard: {str(e)}"}, status=400)
        
        # Create alert
        try:
            alert = Alert.objects.create(
                description=data.get('description', ''),
                location=Point(float(data['lng']), float(data['lat'])),
                effect_radius=data.get('effect_radius'),
                reported_by=current_user,
                source_url=data.get('source_url', None),
                country=address.get('country', ''),
                city=address.get('city', address.get('town', '')),
                county=address.get('county', ''),
                # Associated the hazard-specific model with the alert
                content_type=content_type,
                object_id=object_id
            )
            # Build response data to dynamically update the map and list of alerts
            response_data = {
                "id": alert.id,
                "description": alert.description,
                "location": {
                    "type": "Point",
                    "coordinates": [alert.location.x, alert.location.y]
                },
                "effect_radius": alert.effect_radius,
                
                # "hazard_type": alert.hazard_type,
                "hazard_type": hazard_model_name,
                "hazard_details": hazard_data,

                
                "reported_by": (
                    str(alert.reported_by)
                    if alert.reported_by else None
                ),

                "source_url": alert.source_url,
                "country": alert.country,
                "city": alert.city,
                "county": alert.county,
                "created_at": alert.created_at
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"Error creating Alert: {str(e)}"}, status=400)


class AlertsPaginatedView(APIView):
    """
    Paginated view for the alerts in the alert list element.

    * Returns the alerts in JSON format.
    * Supports search queries.
    * Paginates the alerts.
    """

    def get(self, request, *args, **kwargs):
        """
        Get all alerts if no search query is provided and paginate the alerts.

        * The user can search for an alert by description, hazard type, 
        country, city, or county.
        """
        # Grab the optional search term from the query string
        search_query = request.GET.get('q', '')

        if search_query:
            alerts = Alert.objects.filter(
                Q(description__icontains=search_query) |
                Q(content_type__model__icontains=search_query) |
                Q(country__icontains=search_query) |
                Q(city__icontains=search_query) |
                Q(county__icontains=search_query)
            ).order_by('-created_at')
        else:
            alerts = Alert.objects.all().order_by('-created_at')

        paginator = Paginator(alerts, 4)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        alerts_data = []
        for alert in page_obj:
            alerts_data.append({
                "id": alert.id,
                "description": alert.description,
                "location": {
                    "type": "Point",
                    "coordinates": [alert.location.x, alert.location.y]
                },
                "effect_radius": alert.effect_radius,
                "hazard_type": alert.content_type.model if alert.content_type else None,
                "hazard_details": model_to_dict(alert.hazard_details) if alert.hazard_details else None,
                "reported_by": str(alert.reported_by) if alert.reported_by else None,
                "source_url": alert.source_url,
                "country": alert.country,
                "city": alert.city,
                "county": alert.county,
                "created_at": alert.created_at.isoformat()
            })
        return Response({
            "alerts": alerts_data,
            "page": page_obj.number,
            "num_pages": paginator.num_pages,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous()
        }, status=status.HTTP_200_OK)



#--------------------------------------------------------
# ---------------------Old code--------------------------
#--------------------------------------------------------

# def resources_view(request):
#     return render(request, 'alerts/resources.html')


# def guide_example_view(request):
#     return render(request, 'alerts/guide_example.html')


# def about_view(request):
#     return render(request, 'alerts/about.html')
