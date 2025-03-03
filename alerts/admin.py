from django.contrib import admin
from .models import (Alert, Earthquake, Flood, Tornado, Fire)

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('content_type', 'description', 'reported_by', 'created_at')
    search_fields = ('description',)
    list_filter = ('created_at',)
    
    def delete_model(self, request, obj):
        if obj.hazard_details:
            obj.hazard_details.delete()
        super().delete_model(request, obj)
    
@admin.register(Earthquake)
class EarthquakeAdmin(admin.ModelAdmin):
    list_display = ('magnitude', 'depth')
    search_fields = ('magnitude', 'depth')
    list_filter = ('magnitude',)

@admin.register(Flood)
class FloodAdmin(admin.ModelAdmin):
    list_display = ('severity', 'water_level', 'is_flash_flood')
    search_fields = ('severity', 'water_level')
    list_filter = ('severity',)
    
@admin.register(Tornado)
class TornadoAdmin(admin.ModelAdmin):
    list_display = ('category', 'damage_description')
    search_fields = ('category', 'damage_description')
    list_filter = ('category',)
    
@admin.register(Fire)
class FireAdmin(admin.ModelAdmin):
    list_display = ('fire_intensity', 'is_contained', 'cause')
    search_fields = ('cause',)
    list_filter = ('cause',)