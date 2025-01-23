from django.contrib import admin
from .models import Alert

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('hazard_type', 'description', 'reported_by', 'created_at')
    search_fields = ('description',)
    list_filter = ('created_at',)
