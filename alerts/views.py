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

# Local Imports
from .serializers import AlertGeoSerializer
from .models import Alert

logger = logging.getLogger(__name__)

# View to return all active alerts in GeoJSON format
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
        alerts = Alert.objects.all().order_by('-created_at')
        paginator = Paginator(alerts, 4)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context


class ManageAlertsView(LoginRequiredMixin, TemplateView):
    template_name = 'alerts/manage_alerts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        alerts = Alert.objects.all().order_by('-created_at')
        paginator = Paginator(alerts, 4)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context


class CreateAlertView(LoginRequiredMixin, APIView):
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
                effect_radius=data.get('effect_radius'),
                hazard_type=data.get('hazard_type', 'storm'),
                reported_by=current_user,
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
                "effect_radius": alert.effect_radius,
                "hazard_type": alert.hazard_type,
                "reported_by": (
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

# View to return paginated alerts data in JSON format
class AlertsPaginatedView(APIView):

    def get(self, request, *args, **kwargs):
        # Grab the optional search term from the query string
        search_query = request.GET.get('q', '')

        if search_query:
            alerts = Alert.objects.filter(
                Q(description__icontains=search_query) |
                Q(hazard_type__icontains=search_query) |
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
                "hazard_type": alert.hazard_type,
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


# def resources_view(request):
#     return render(request, 'alerts/resources.html')


# def guide_example_view(request):
#     return render(request, 'alerts/guide_example.html')


# def about_view(request):
#     return render(request, 'alerts/about.html')
