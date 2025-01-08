from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from .views import (AlertViewSet, map_view, CreateAlertView,
                    home_view, resources_view, guide_example_view,
                    about_view, login_view)

router = DefaultRouter()
router.register(r'alerts', AlertViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('home/', home_view, name='home'),
    path('map/', map_view, name='map'),
    path('resources/', resources_view, name='resources'),
    path('guide_example/', guide_example_view, name='guide'),
    path('about/', about_view, name='about'),
    path('login/', login_view, name='login'),
    path('create_alerts/', CreateAlertView.as_view(), name='create_alert'),
]
