from django.urls import path, include
from .views import (map_view, CreateAlertView,
                    HomeView, resources_view, guide_example_view,
                    AlertGeoJsonListView)


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('map/', map_view, name='map'),
    path('resources/', resources_view, name='resources'),
    path('guide_example/', guide_example_view, name='guide'),
    path('create_alerts/', CreateAlertView.as_view(), name='create_alert'),
    path(
        'geojson/', AlertGeoJsonListView.as_view(), name='alerts-geojson'),
]
