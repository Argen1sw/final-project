# Python Imports

# Django Imports
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from rest_framework.views import APIView
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponseForbidden

# Local Imports
from .forms import RegisterForm, LoginForm
from .models import User


# - Add messages display to the login page and registration page

class UserRegisterView(CreateView):
    """
    View class that handles new user registration.

    * If the user register succesfully, redirect to the home page.
    """

    form_class = RegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        user = form.save()
        user.user_type = 1  # Default to "normal user"
        user.save()

        # Authenticate and log the user in
        user = authenticate(
            username=user.username,
            password=form.cleaned_data.get("password1")
        )
        if user is not None:
            login(self.request, user)
            messages.success(
                self.request,
                f"Registration successful. Welcome, {user.username}!"
            )
            return redirect("home")
        else:
            messages.error(
                self.request,
                "There was a problem logging you in automatically. Please log in manually."
            )
            return redirect("login")


class CustomLoginView(LoginView):
    """
    View class that handles user login.

    * If the user is already logged in, redirect to the home page.
    * If the user is not logged in, display the login form.
    """
    form_class = LoginForm
    template_name = "users/login.html"

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        return super().form_valid(form)


class ManageUsersView(LoginRequiredMixin, TemplateView):
    """ 
    View class that handles user management. 

    * Only admin and ambassador users can access this view.
    * Admin users can manage all users.
    * Ambassador users can only manage normal users.        
    """
    template_name = "users/manage_users.html"

    def dispatch(self, request, *args, **kwargs):
        """
        Check if the user is an admin or ambassador.
        """
        if not request.user.is_admin() and not request.user.is_ambassador():
            messages.error(
                request,
                "You do not have permission to access this page."
            )
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Add all users to the context.
        """
        context = super().get_context_data(**kwargs)
        users = User.objects.all().order_by("-date_joined")
        paginator = Paginator(users, 2)
        page_number = self.request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)
        context["page_obj"] = page_obj
        return context


class ManageUsersPaginatedView(LoginRequiredMixin, APIView):
    """
    View class that handles user management.

    * Only admin and ambassador users can access this view.
    * Admin users can manage all users.
    * Ambassador users can only manage normal users.
    * This view returns a JSON response for pagination purposes.
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Check if the user is an admin or ambassador.
        """
        if not request.user.is_admin() and not request.user.is_ambassador():
            messages.error(
                request,
                "You do not have permission to access this page."
            )
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Get all users if not search Q provided and paginate the users.

        * The user can search for a user by username or email.
        """
        user_type = request.user.user_type

        search_query = request.GET.get("q", "")
        if search_query:
            users = User.objects.filter(
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query)
            ).order_by("-date_joined")
        else:
            users = User.objects.all().order_by("-date_joined")

        # Paginate the users
        paginator = Paginator(users, 2)
        page_number = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        user_data = []
        for user in page_obj:
            user_data.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "date_joined": user.date_joined,
                "user_type": user.get_user_type_display(),
                "bio": user.bio,
                "alerts_created": user.alerts_created,
                "alerts_verified": user.alerts_verified,
                "is_verified": user.is_verified,
                "is_suspended": user.is_suspended
            })
        return Response({
            "user_type": user_type,
            "users": user_data,
            "page": page_obj.number,
            "num_pages": paginator.num_pages,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous()
        }, status=status.HTTP_200_OK)


class suspendUnsuspendUser(LoginRequiredMixin, APIView):
    """
    suspend or unsuspend a user based on the user_id.

    * Only admin and ambassador users can access this view.
    * Admin users can manage all users.
    * Ambassador users can only manage normal users.
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Check if the user is an admin or ambassador.
        """
        if not request.user.is_admin() and not request.user.is_ambassador():
            messages.error(
                request,
                "You do not have permission to use this view."
            )
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *arg, **args):
        """
        get the user_id from the request and suspend or unsuspend the user.
        """
        user_id = args.get("user_id")
        print(user_id)
        user = get_object_or_404(User, id=user_id)

        if request.user.is_admin():
            pass
        elif request.user.is_ambassador():
            if not user.is_normal_user():
                return HttpResponseForbidden("You are not allowed to suspend this user. Contact an admin.")
        else:
            return HttpResponseForbidden("You are not allowed to perform this action.")

        if user.is_suspended:
            user.is_suspended = False
            user.save()
            messages.success(
                request, f"User {user.username} has been unsuspended.")
        else:
            user.is_suspended = True
            user.save()
            messages.info(request, f"User {user.username} has been suspended.")
        return redirect("manage_users")


class userProfileView(LoginRequiredMixin, TemplateView):
    template_name = "users/user_profile.html"
    # model = User
    
# class editUserProfileView(LoginRequiredMixin, TemplateView):
#     template_name = "users/edit_user_profile.html"
#     # model = User
    

    