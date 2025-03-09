# Standard library imports
from django.urls import path

# Local Imports
from .views import (ManageAlertsView, CreateAlertView,
                    HomeView, AlertGeoJsonListView, AlertsPaginatedView,
                    AlertVoteView, AlertDetailsAndEditView, AlertDeleteView,
                    ArchiveAlertView)


urlpatterns = [

    # Home page path endpoint
    path('', HomeView.as_view(), name='home'),

    # Manage Alerts page Path endpoint
    path('manage_alerts/', ManageAlertsView.as_view(), name='manage_alerts'),

    # Path endpoint for creating alerts (Used for the form in the map)
    path('create_alerts/', CreateAlertView.as_view(), name='create_alert'),

    # Path endpoint for the  all Alerts in GeoJSON format (Used for the map)
    path('geojson/', AlertGeoJsonListView.as_view(), name='alerts-geojson'),

    # Path endpoint for paginated alerts (Used for AJAX request)
    path('paginated_alerts/', AlertsPaginatedView.as_view(), name='paginated_alert'),

    # Path endpoint for alert details
    path('alert/<int:pk>/', AlertDetailsAndEditView.as_view(), name='alert_details'),

    # Path endpoint for editing alerts
    path('alert/<int:pk>/edit/',
         AlertDetailsAndEditView.as_view(), name='edit_alert'),

    #   # Path endpoint for voting alerts
    path('alert/<int:pk>/vote', AlertVoteView.as_view(), name='vote_alert'),

    # Path endpoint for deleting alerts
    path('alert/<int:pk>/delete/', AlertDeleteView.as_view(), name='delete_alert'),

    # Path endpoint for archiving alerts
    path('alert/<int:pk>/archive/',
         ArchiveAlertView.as_view(), name='archive_alert'),
]
