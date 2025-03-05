from django.contrib import admin
from .models import User

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # Fields to display in the admin list view
    list_display = ('username', 'email', 'user_type', 'is_verified', 'is_suspended', 'date_joined')
    list_filter = ('user_type', 'is_verified', 'is_suspended')
    search_fields = ('username', 'email')
    ordering = ('date_joined',)

    # Customize the form used when viewing/editing a user
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('email', 'bio')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
        ('User Type and Status', {'fields': ('user_type', 'is_verified', 'is_suspended')}),
        ('Other Information', {'fields': ('alerts_created', 'alerts_upvoted')}),
    )

    # Fields for the user creation form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type'),
        }),
    )