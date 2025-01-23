from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from .forms import RegisterForm, LoginForm


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.user_type = 1  # Default to "normal user"
            user.save()
            # Automatically log in the user after registration
            login(request, user)
            return redirect('home')  # Redirect to a homepage or dashboard
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'users/login.html'

    def form_valid(self, form):
        """Customize the response after a successful login, if needed."""
        return super().form_valid(form)