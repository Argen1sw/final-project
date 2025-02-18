from django.urls import path, include
from .views import (ManageAlertsView, CreateAlertView,
                    HomeView, AlertGeoJsonListView, AlertsPaginatedView)


urlpatterns = [
    path('', HomeView.as_view(), name='home'),

    # Endpoint that returns all the alerts in JSON format
    path('geojson/', AlertGeoJsonListView.as_view(), name='alerts-geojson'),


    # Alerts webpage endpoint
    path('manage_alerts/', ManageAlertsView.as_view(), name='manage_alerts'),
    path('create_alerts/', CreateAlertView.as_view(), name='create_alert'),
    path('paginated_alerts/', AlertsPaginatedView.as_view(), name='paginated_alert'),

    # path('resources/', resources_view, name='resources'),
    # path('guide_example/', guide_example_view, name='guide'),
]
