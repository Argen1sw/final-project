# Django Import
from django.urls import path
from django.contrib.auth.views import LogoutView

# Local Import
from .views import (CustomLoginView, UserRegisterView, ManageUsersView,
                    ManageUsersPaginatedView, SuspendUnsuspendUser,
                    UserProfileView)

urlpatterns = [

    # Register User page path endpoint
    path('register/', UserRegisterView.as_view(), name='register'),

    # Login User page path endpoint
    path('login/', CustomLoginView.as_view(), name='login'),

    # Logout User path endpoint
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),

    # Manage Users page path endpoint
    path('manage_users/', ManageUsersView.as_view(), name='manage_users'),

    # Paginated Manage Users path endpoint (for AJAX)
    path('paginated_manage_users/', ManageUsersPaginatedView.as_view(),
        name='paginated_manager_users'),

    # Suspend/Unsuspend User path endpoint
    path('suspend_unsuspend_user/<int:user_id>/',
        SuspendUnsuspendUser.as_view(), name='suspend_unsuspend_user'),

    # User Profile path endpoint
    path('profile/', UserProfileView.as_view(), name='profile')
        
]
