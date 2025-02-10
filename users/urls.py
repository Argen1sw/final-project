

# Django Import
from django.urls import path
from django.contrib.auth.views import LogoutView

# Local Import
from .views import (CustomLoginView, UserRegisterView, ManageUsersView,
                    suspend_user, unsuspend_user)

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('manage_users/', ManageUsersView.as_view(), name='manage_users'),
    
    path('suspend_user/<int:user_id>/', suspend_user, name='suspend_user'),
    path('unsuspend_user/<int:user_id>/', unsuspend_user, name='unsuspend_user'),
]