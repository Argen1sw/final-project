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

class UserProfileForm(forms.ModelForm):
    """
    Form class that handles user profile updates.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3})
        }
        
class PasswordUpdateForm(forms.Form):
    """
    Form class that handles user password updates.
    """
    
    current_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(),
        required=True
    )
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(),
        required=True
    )
    repeat_new_password = forms.CharField(
        label="Repeat Password",
        widget=forms.PasswordInput(),
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = kwargs.get('user')

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError("The current password is incorrect.")
        return current_password

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        if len(new_password) < 8:
            raise forms.ValidationError("New password must be at least 8 characters long.")
        return new_password

    def clean_repeat_new_password(self):
        repeat_new_password = self.cleaned_data.get('repeat_new_password')
        new_password = self.cleaned_data.get('new_password')

        if repeat_new_password != new_password:
            raise forms.ValidationError("The new password and repeat password do not match.")
        return repeat_new_password

    def save(self):
        # Set the new password for the user
        new_password = self.cleaned_data.get('new_password')
        self.user.set_password(new_password)
        self.user.save()
    
    
class EmailUpdateForm(forms.ModelForm):
    """
    Form class that handles user email updates.
    """
    class Meta:
        model = User
        fields = ['email']
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Query to extract all the users email
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email
    
