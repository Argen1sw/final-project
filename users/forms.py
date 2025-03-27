# Library/Frameworks Imporst
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

# Local Imports
from .models import User

# Register should include a mechanism that allows user to register
# with their google account.


class RegisterForm(UserCreationForm):
    """
    View class that handles user registration.

    * UserCreationForm: A form that creates a user, with no privileges, 
        from the given username and password.
    * Fields: username, email, password1, password2
    """
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Password',
                'class': 'bg-gray-700 text-white border border-gray-600 p-2 rounded w-full'
            }
        ),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Confirm Password',
                'class': 'bg-gray-700 text-white border border-gray-600 p-2 rounded w-full'
            }
        ),
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Username',
                'class': 'bg-gray-700 text-white border border-gray-600 p-2 rounded w-full'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email',
                'class': 'bg-gray-700 text-white border border-gray-600 p-2 rounded w-full'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Query to extract all the users email
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

# This will need to be implemented in the future to be able to accept google login and
# email as a form of validation too
class LoginForm(AuthenticationForm):
    """
    Form class that handles user login.
    
    * AuthenticationForm: A form for logging a user in.
    * Fields: username, password
    """
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'bg-gray-700 text-white border border-gray-600 p-2 rounded w-full',
        'placeholder': 'Username',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'bg-gray-700 text-white border border-gray-600 p-2 rounded w-full',
        'placeholder': 'Password',
    }))

    class Meta:
        model = User
        fields = ['username', 'password']


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
    # Fields
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
        """
        Override constructor method that initializes the form.
        """
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        """
        Method that validates the current password.
        Check link below for more information:
        https://docs.djangoproject.com/en/5.1/ref/forms/validation/
        """
        current_password = self.cleaned_data.get('current_password')
        print(f" from current password {current_password}")
        print(self.user.check_password(current_password))
        if not self.user.check_password(current_password):
            raise forms.ValidationError("The current password is incorrect.")
        return current_password

    def clean_new_password(self):
        """
        Method that validates the new password.
        """
        new_password = self.cleaned_data.get('new_password')
        print(f" from New password {new_password}")
        if len(new_password) < 8:
            raise forms.ValidationError(
                "New password must be at least 8 characters long.")
        return new_password

    def clean_repeat_new_password(self):
        """
        Method that validates the repeat new password.
        """
        repeat_new_password = self.cleaned_data.get('repeat_new_password')
        new_password = self.cleaned_data.get('new_password')
        print(f" from repeat password {repeat_new_password}")

        if repeat_new_password != new_password:
            raise forms.ValidationError(
                "The new password and repeat password do not match.")
        return repeat_new_password

    def save(self):
        """
        Method that saves the new password for the user.
        """
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
