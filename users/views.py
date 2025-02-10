# Description: This file contains the views for the users app.

# Python Imports

# Django Imports
from django.shortcuts import redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

# Local Imports
from .forms import RegisterForm, LoginForm
from .models import User

# TODO:
# - Add email verification
# - Add password reset
# - Add Google login
# - Add messages display to the login page and registration page


# View class that handles new user registration
class UserRegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save()
        user.user_type = 1  # Default to "normal user"
        user.save()
        
        # Authenticate and log the user in
        user = authenticate(
            username=user.username, 
            password=form.cleaned_data.get('password1')
        )
        if user is not None:
            login(self.request, user)
            messages.success(
                self.request, 
                f'Registration successful. Welcome, {user.username}!'
            )
            return redirect('home') 
        else:
            messages.error(
                self.request, 
                'There was a problem logging you in automatically. Please log in manually.'
            )
            return redirect('login') 

# View class that handles user login
class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'users/login.html'

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        return super().form_valid(form)

# View class that handles user management
# Only admin and ambassador users can access this view
class ManageUsersView(LoginRequiredMixin, TemplateView):
    template_name = 'users/manage_users.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_admin() and not request.user.is_ambassador():
            messages.error(
                request, 
                'You do not have permission to access this page.'
            )
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all()
        return context




from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseForbidden

@login_required
def suspend_user(request, user_id):
    # Retrieve the target user
    target_user = get_object_or_404(User, id=user_id)

    # Check permissions
    if request.user.is_admin():
        # Admin can manage any user
        pass
    elif request.user.is_ambassador():
        # Ambassadors can only manage normal users
        if not target_user.is_normal_user():
            return HttpResponseForbidden("You are not allowed to suspend this user.")
    else:
        return HttpResponseForbidden("You are not allowed to perform this action.")

    # Mark the user as suspended
    if not target_user.is_suspended:
        target_user.is_suspended = True
        target_user.save()
        messages.success(request, f"User {target_user.username} has been suspended.")
    else:
        messages.info(request, f"User {target_user.username} is already suspended.")

    # Redirect back to the manage users page (update the URL name as needed)
    return redirect('manage_users')

@login_required
def unsuspend_user(request, user_id):
    # Retrieve the target user
    target_user = get_object_or_404(User, id=user_id)

    # Check permissions
    if request.user.is_admin():
        # Admin can manage any user
        pass
    elif request.user.is_ambassador():
        # Ambassadors can only manage normal users
        if not target_user.is_normal_user():
            return HttpResponseForbidden("You are not allowed to unsuspend this user.")
    else:
        return HttpResponseForbidden("You are not allowed to perform this action.")

    # Mark the user as not suspended
    if target_user.is_suspended:
        target_user.is_suspended = False
        target_user.save()
        messages.success(request, f"User {target_user.username} has been unsuspended.")
    else:
        messages.info(request, f"User {target_user.username} is not suspended.")

    # Redirect back to the manage users page (update the URL name as needed)
    return redirect('manage_users')