from django.contrib import admin
from .models import AccessToken

# Register your models here.
@admin.register(AccessToken)
class AccessTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_name', 'created_at', 'expires_at', 'is_revoked')
    search_fields = ('user', 'device_name')
    list_filter = ('created_at', 'expires_at', 'is_revoked')
