from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

# Register should include a mechanism that allows user to register
# with their google account.
class RegisterForm(UserCreationForm):
    """
    """
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Query to extract all the users email
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email
    
# This will need to be extended to be able to accept google login and
# email as a form of validation too
class LoginForm(AuthenticationForm):
    pass