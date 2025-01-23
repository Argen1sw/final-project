from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationTest(TestCase):
    
    def test_registration_view_url_exists(self):
        """Test that the registration URL is accessible."""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_user_registration_success(self):
        """Test that a user can register successfully."""
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123',
        })

        # Check that the user was created
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'testuser@example.com')

        # Check default user_type
        self.assertEqual(user.user_type, 1)  # 1 corresponds to "normal user"

        # Check redirection after successful registration
        self.assertRedirects(response, reverse('home'))

    def test_registration_with_missing_fields(self):
        """Test registration fails if required fields are missing."""
        response = self.client.post(reverse('register'), {
            'username': '',
            'email': '',
            'password1': '',
            'password2': '',
        })

        # Ensure the user was not created
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 200)  # Stay on the form
        self.assertFormError(response, 'form', 'username', 'This field is required.')
        self.assertFormError(response, 'form', 'email', 'This field is required.')
        self.assertFormError(response, 'form', 'password1', 'This field is required.')

    def test_registration_with_mismatched_passwords(self):
        """Test registration fails if passwords don't match."""
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'password123',
            'password2': 'password456',  # Mismatched passwords
        })

        # Ensure the user was not created
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 200)  # Stay on the form
        
        # Check that the form is invalid and errors exist
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_registration_with_duplicate_email(self):
        """Test registration fails if email is already in use."""
        # Create a user with the same email
        User.objects.create_user(username='existinguser', email='testuser@example.com', password='password123')

        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'testuser@example.com',  # Duplicate email
            'password1': 'password123',
            'password2': 'password123',
        })

        # Ensure the user was not created
        self.assertEqual(User.objects.count(), 1)  # Only the initial user exists
        self.assertEqual(response.status_code, 200)  # Stay on the form
        self.assertFormError(response, 'form', 'email', "This email is already in use.")

    def test_default_user_type_is_normal_user(self):
        """Test that the default user_type for new users is 'normal user'."""
        user = User.objects.create_user(username='defaultusertest', email='default@example.com', password='password123')
        self.assertEqual(user.user_type, 1)  # Default to "normal user"