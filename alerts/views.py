# Standard Library Imports
import logging

# Django Imports
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from rest_framework.views import APIView
from django.views import View
from rest_framework.response import Response
from rest_framework import status
from django.contrib.gis.geos import Point
from geopy.geocoders import Nominatim
from django.views.generic import (
    TemplateView, DetailView, DeleteView, UpdateView
)
from django.core.paginator import Paginator
from rest_framework import generics
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.forms.models import model_to_dict
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from django.urls import reverse


# Local Imports
from .serializers import AlertGeoSerializer
from .models import (Alert, Earthquake, Flood, Tornado, Fire, AlertUserVote)
from .forms import AlertForm

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
            alert.hazard_details_dict = model_to_dict(
                alert.hazard_details) if alert.hazard_details else None
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
        # filter alerts by the is_active field
        alerts = Alert.objects.filter(is_active=True).order_by('-created_at')
        paginator = Paginator(alerts, 4)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        # Inject hazard type information on each alert
        for alert in page_obj:
            alert.hazard_type = alert.content_type.model if alert.content_type else None
            alert.hazard_details_dict = model_to_dict(
                alert.hazard_details) if alert.hazard_details else None
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


class CreateAlertView(APIView):
    """
    API View class to create a new alert.

    * Only authenticated users can create alerts.
    * Alerts are created using the POST method.
    * Returns the alert data in JSON format for the AJAX request.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

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

        # Validate effect radius
        effect_radius = data.get('effect_radius')
        if effect_radius is not None and effect_radius > 100000 or effect_radius < 0:
            return Response({"error": "The radius of effect cannot exceed 100 km (100,000 meters)."}, status=400)

        # Reverse Geocoding
        try:
            geolocator = Nominatim(user_agent="enviroalerts")
            location = geolocator.reverse((lat, lng), language="en")
            address = location.raw.get('address', {}) if location else {}
        except Exception as e:
            return Response({"error": f"Geocoding failed: {str(e)}"}, status=400)

        # Automatically set `reported_by` to the logged-in user
        current_user = request.user if request.user.is_authenticated else None

        if current_user:
            current_user.alerts_created += 1
            current_user.save()
        else:
            return Response({"error": "You must be logged in to create an alert."}, status=400)

        # Handles the Hazard type
        hazard_model_name = data.get('hazard_type')
        hazard_data = data.get('hazard_data', {})
        content_type = None
        object_id = None

        # Preprocess hazard_data to ensure no empty strings are passed to the model
        hazard_data = {
            key: (value if not (isinstance(value, str)
                  and value.strip() == "") else None)
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
            # Filter alerts by the search query and is active field
            alerts = Alert.objects.filter(
                Q(description__icontains=search_query) |
                Q(content_type__model__icontains=search_query) |
                Q(country__icontains=search_query) |
                Q(city__icontains=search_query) |
                Q(county__icontains=search_query),
                is_active=True
            ).order_by('-created_at')
        else:
            alerts = Alert.objects.filter(
                is_active=True).order_by('-created_at')

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


class AlertDetailsAndEditView(LoginRequiredMixin, UpdateView):
    """
    Update view for displaying and editing an alert.

    * Displays the alert details, including hazard type and location.
    * Allows the user to edit the alert if they have permission.
    """
    model = Alert
    template_name = 'alerts/alert_details.html'
    context_object_name = 'alert'
    form_class = AlertForm

    def get_object(self, queryset=None):
        """
        Retrieves the alert object and ensures the user has permission to edit.
        """
        alert = get_object_or_404(Alert, pk=self.kwargs.get('pk'))

        # If the user does not have permission, return Forbidden response
        if not self.user_can_edit(alert):
            return HttpResponseForbidden("You do not have permission to edit this alert.")

        return alert

    def get_context_data(self, **kwargs):
        """
        Injects additional data into the template context, including hazard type and user vote.
        """
        context = super().get_context_data(**kwargs)
        alert = context['alert']

        # Add hazard type and details
        context = super().get_context_data(**kwargs)
        alert = context['alert']
        alert.hazard_type = alert.content_type.model if alert.content_type else None
        alert.hazard_details_dict = model_to_dict(
            alert.hazard_details) if alert.hazard_details else None
        del alert.hazard_details_dict['id']

        for key in alert.hazard_details_dict:
            if alert.hazard_details_dict[key] is None:
                alert.hazard_details_dict[key] = "N/A"

        # Insert the user's vote status
        if self.request.user.is_authenticated:
            user_vote = AlertUserVote.objects.filter(
                alert=alert, user=self.request.user).first()
            context['user_vote'] = user_vote.vote if user_vote else None

        return context

    def user_can_edit(self, alert):
        """
        Checks if the user has permission to edit the alert.
        """
        return (alert.reported_by == self.request.user or
                self.request.user.is_admin() or
                self.request.user.is_ambassador())

    def form_valid(self, form):
        """
        Handles form submission and ensures only authorized users can edit.
        """
        alert = form.save()

        if not self.user_can_edit(alert):
            return HttpResponseForbidden("You do not have permission to edit this alert.")

        alert.save()
        
        return super().form_valid(form)

    def get_success_url(self):
        """
        Redirects to the alert details page after successful editing.
        """
        return reverse('alert_details', kwargs={'pk': self.object.pk})


class AlertDeleteView(LoginRequiredMixin, DeleteView):
    pass


class AlertVoteView(LoginRequiredMixin, View):
    """
    View class for voting on an alert.

    * Handles the voting mechanism for an alert.
    * Supports upvoting and downvoting.
    """

    def post(self, request, pk):
        """
        Handle the POST request for voting on an alert.

        * Validates the vote type.
        * Updates the vote count for the alert.
        * Creates an instance of the vote model.
        """
        alert = get_object_or_404(Alert, pk=pk)

        # retrieve the user that owns the alert
        user = alert.reported_by

        vote_value = request.POST.get('vote')

        if vote_value not in ['1', '-1']:
            return HttpResponseBadRequest("Invalid vote type.")

        is_upvote = (vote_value == '1')

        #
        user_vote, created = AlertUserVote.objects.get_or_create(
            alert=alert,
            user=request.user,
            defaults={'vote': is_upvote}
        )

        # Update the vote count for the alert
        # Update the Alert's owner upvote count
        if not created:
            if user_vote.vote != is_upvote:
                # Change the vote if the user votes differently
                if is_upvote:
                    alert.negative_votes -= 1
                    alert.positive_votes += 1
                    # Remove the vote from the user's upvote count
                    user.alerts_upvoted += 1
                else:
                    alert.positive_votes -= 1
                    alert.negative_votes += 1
                    user.alerts_upvoted -= 1
                user_vote.vote = is_upvote
                user_vote.save()
            else:
                # delete the vote if the user votes the same way
                # Remove the vote from the user's upvote count
                if is_upvote:
                    print("Deleting upvote")
                    alert.positive_votes -= 1
                    user.alerts_upvoted -= 1
                else:
                    alert.negative_votes -= 1
                user_vote.delete()
                alert.save()
                user.save()
                return redirect('alert_details', pk=pk)
        else:
            if is_upvote:
                alert.positive_votes += 1
                user.alerts_upvoted += 1
            else:
                alert.negative_votes += 1
        user.save()
        alert.save()
        return redirect('alert_details', pk=pk)




# class AlertDetailsView(DetailView):
#     """
#     View class for the alert details page.

#     * Displays the details of a specific alert.
#     * Displays the hazard type and details.
#     * Displays the alert's location on a map.
#     """
#     model = Alert
#     template_name = 'alerts/alert_details.html'
#     context_object_name = 'alert'

#     def get_context_data(self, **kwargs):
#         """
#         Get the context data for the alert details page.

#         * Injects the hazard type and details into the context.
#         * 
#         """
#         context = super().get_context_data(**kwargs)
#         alert = context['alert']
#         alert.hazard_type = alert.content_type.model if alert.content_type else None
#         alert.hazard_details_dict = model_to_dict(
#             alert.hazard_details) if alert.hazard_details else None
#         del alert.hazard_details_dict['id']

#         for key in alert.hazard_details_dict:
#             if alert.hazard_details_dict[key] is None:
#                 alert.hazard_details_dict[key] = "N/A"

#         # Insert the user's vote status
#         if self.request.user.is_authenticated:
#             user_vote = AlertUserVote.objects.filter(
#                 alert=alert, user=self.request.user).first()
#             context['user_vote'] = user_vote.vote if user_vote else None

#         return context