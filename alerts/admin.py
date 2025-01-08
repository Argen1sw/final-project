from django.contrib import admin
from .models import Alert

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'location', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at',)
