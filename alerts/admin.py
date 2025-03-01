from django.contrib import admin
from .models import Alert, Earthquake

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('description', 'reported_by', 'created_at')
    search_fields = ('description',)
    list_filter = ('created_at',)
    
@admin.register(Earthquake)
class EarthquakeAdmin(admin.ModelAdmin):
    list_display = ('magnitude', 'depth')
    search_fields = ('magnitude', 'depth')
    list_filter = ('magnitude',)
