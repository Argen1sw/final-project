from django.urls import path, include
from .views import (ManageAlertsView, CreateAlertView,
                    HomeView, AlertGeoJsonListView, AlertsPaginatedView)


urlpatterns = [
    
    # Home page path endpoint
    path('', HomeView.as_view(), name='home'),

    # Manage Alerts page Path endpoint 
    path('manage_alerts/', ManageAlertsView.as_view(), name='manage_alerts'),

    # Path endpoint for creating alerts (Used for the form in the map)
    path('create_alerts/', CreateAlertView.as_view(), name='create_alert'),

    # Path endpoint for the  all Alerts in GeoJSON format (Used for the map)
    path('geojson/', AlertGeoJsonListView.as_view(), name='alerts-geojson'),

    # Path endpoint for paginated alerts (Used for AJAX)
    path('paginated_alerts/', AlertsPaginatedView.as_view(), name='paginated_alert'),

]
