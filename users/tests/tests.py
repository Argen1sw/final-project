# Framework Imports
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model, login, authenticate
from rest_framework import status
from rest_framework.test import APITestCase
from django.shortcuts import resolve_url

User = get_user_model()


class UserRegisterViewTest(TestCase):
    """
    Test suite for the User Registration view.
    This suite covers:
    - GET request to the registration page
    - Successful registration with valid data
    - Registration with an existing email
    """

    def setUp(self):
        self.url = reverse("register")

    def test_get_register_view(self):
        """
        A GET request to the registration page should return status 200
        and render the registration template.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/register.html")
        # Check that the form is present in context
        self.assertIn("form", response.context)

    def test_successful_registration(self):
        """
        A valid POST request should create a new user, log them in,
        set the user_type to 1 (normal user), and redirect to home.
        """
        valid_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "StrongPass123",
            "password2": "StrongPass123",
        }
        response = self.client.post(self.url, data=valid_data)
        # The view redirects to home on successful registration.
        self.assertRedirects(response, reverse("home"))
        # Verify the user was created with the expected attributes.
        self.assertTrue(User.objects.filter(username="newuser").exists())
        user = User.objects.get(username="newuser")
        self.assertEqual(user.user_type, 1)
        # Optionally, check that the user is authenticated by simulating a follow-up request.
        response = self.client.get(reverse("home"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_registration_with_existing_email(self):
        """
        Submitting registration data with an email that already exists should
        re-render the form with an error message.
        """
        # Create an initial user with a given email.
        User.objects.create_user(
            username="existing", email="duplicate@example.com", password="testpass", user_type=1
        )
        invalid_data = {
            "username": "anotheruser",
            "email": "duplicate@example.com",  # same email as above
            "password1": "StrongPass123",
            "password2": "StrongPass123",
        }
        response = self.client.post(self.url, data=invalid_data)
        # The form should be re-rendered with status 200.
        self.assertEqual(response.status_code, 200)
        # Verify that the error for the email field is present.
        self.assertFormError(response, "form", "email",
                             "This email is already in use.")
        # No new user with username "anotheruser" should have been created.
        self.assertFalse(User.objects.filter(username="anotheruser").exists())


class CustomLoginViewTest(TestCase):
    """
    Test suite for the Custom Login view.
    
    This suite covers:
    - GET request to the login page
    - Successful login with valid credentials
    - Login attempt with a suspended user
    """
    
    def setUp(self):
        self.login_url = reverse("login")
        # Create an active user
        self.active_user = User.objects.create_user(
            username="activeuser",
            password="testpass123",
            email="active@example.com",
            user_type=1,
            is_suspended=False
        )
        # Create a suspended user
        self.suspended_user = User.objects.create_user(
            username="suspendeduser",
            password="testpass123",
            email="suspended@example.com",
            user_type=1,
            is_suspended=True
        )

    def test_get_login_view(self):
        """
        A GET request to the login view should return status 200 and use the correct template.
        """
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/login.html")
        self.assertIn("form", response.context)

    def test_successful_login(self):
        """
        A POST request with valid credentials for an active user should log the user in and redirect.
        """
        data = {"username": "activeuser", "password": "testpass123"}
        response = self.client.post(self.login_url, data, follow=True)
        # Check that the response is a redirect (usually to "home" or similar)
        self.assertTrue(response.redirect_chain)
        # Check that the user is authenticated on the subsequent request.
        user = response.wsgi_request.user
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.username, "activeuser")

    def test_suspended_user_login(self):
        """
        A POST request with valid credentials for a suspended user should not log in the user.
        The form should show an error message.
        """
        data = {"username": "suspendeduser", "password": "testpass123"}
        response = self.client.post(self.login_url, data)
        # The view should re-render the login form (status 200) with an error.
        self.assertEqual(response.status_code, 200)
        form = response.context.get("form")
        self.assertIsNotNone(form)
        # Check that the form contains the suspended user error message.
        # Note: Depending on how errors are rendered, you may need to inspect form.non_field_errors.
        errors = form.non_field_errors()
        self.assertIn(
            "Your account is suspended. Please contact support.", errors)
        # Ensure the user is not authenticated.
        user = response.wsgi_request.user
        self.assertFalse(user.is_authenticated)


class ManageUsersViewTest(TestCase):
    """
    Test suite for the Manage Users view.
    
    This suite covers:
    - Access by admin users
    - Access by ambassador users
    - Access by normal users
    - Access by anonymous users
    """
    def setUp(self):
        self.manage_users_url = reverse("manage_users")
        self.home_url = reverse("home")
        self.login_url = reverse("login")

        # Create an admin user (user_type=3)
        self.admin = User.objects.create_user(
            username="adminuser",
            password="testpass",
            email="admin@example.com",
            user_type=3
        )
        # Create an ambassador user (user_type=2)
        self.ambassador = User.objects.create_user(
            username="ambassadoruser",
            password="testpass",
            email="ambassador@example.com",
            user_type=2
        )
        # Create a normal user (user_type=1)
        self.normal_user = User.objects.create_user(
            username="normaluser",
            password="testpass",
            email="normal@example.com",
            user_type=1
        )
        # Create additional users so that pagination (2 per page) can be tested.
        # Here we create 4 more normal users.
        for i in range(4):
            User.objects.create_user(
                username=f"testuser{i}",
                password="testpass",
                email=f"testuser{i}@example.com",
                user_type=1
            )

    def test_admin_can_access_manage_users(self):
        """
        An admin should be able to access the manage users view and see a paginated list.
        """
        self.client.login(username="adminuser", password="testpass")
        response = self.client.get(self.manage_users_url)
        self.assertEqual(response.status_code, 200)
        # Check that the template is used.
        self.assertTemplateUsed(response, "users/manage_users.html")
        # Check that the context contains a paginator page object.
        self.assertIn("page_obj", response.context)
        page_obj = response.context["page_obj"]
        # Verify the page object is paginated with 2 users per page.
        self.assertEqual(page_obj.paginator.per_page, 2)
        self.assertGreaterEqual(len(page_obj.object_list), 1)

    def test_ambassador_can_access_manage_users(self):
        """
        An ambassador should be able to access the manage users view.
        """
        self.client.login(username="ambassadoruser", password="testpass")
        response = self.client.get(self.manage_users_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/manage_users.html")
        self.assertIn("page_obj", response.context)

    def test_normal_user_redirected_to_home(self):
        """
        A normal user (non-admin, non-ambassador) should be redirected to the home page.
        """
        self.client.login(username="normaluser", password="testpass")
        response = self.client.get(self.manage_users_url)
        # The view redirects normal users to home.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.home_url)

    def test_anonymous_user_redirected_to_login(self):
        """
        Anonymous users should be redirected to the login page.
        """
        response = self.client.get(self.manage_users_url)
        # LoginRequiredMixin should cause a redirect.
        self.assertEqual(response.status_code, 302)
        # Check that the redirect URL contains the login URL.
        self.assertIn(self.login_url, response.url)


class ManageUsersPaginatedViewTest(APITestCase):
    """
    Test suite for the paginated user management view.

    This suite covers:
    - Access by admin users
    - Access by ambassador users
    - Access by normal users
    - Access by anonymous users
    """

    def setUp(self):
        self.url = reverse("paginated_manager_users")
        self.home_url = reverse("home")
        self.login_url = reverse("login")

        # Create users with different roles
        self.admin = User.objects.create_user(
            username="adminuser",
            password="testpass",
            email="admin@example.com",
            user_type=3  # admin
        )
        self.ambassador = User.objects.create_user(
            username="ambassadoruser",
            password="testpass",
            email="ambassador@example.com",
            user_type=2  # ambassador
        )
        self.normal_user = User.objects.create_user(
            username="normaluser",
            password="testpass",
            email="normal@example.com",
            user_type=1  # normal user
        )

        # Create additional users for pagination testing (total at least 5 users)
        # These can be any type; for simplicity we'll make them normal users.
        for i in range(5):
            User.objects.create_user(
                username=f"extrauser{i}",
                password="testpass",
                email=f"extrauser{i}@example.com",
                user_type=1
            )

    def test_admin_can_access_paginated_view(self):
        """
        An admin user should be able to access the paginated user list,
        and receive a JSON response with the expected keys.
        """
        self.client.login(username="adminuser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        # Check that the JSON response includes the expected keys.
        self.assertIn("users", data)
        self.assertIn("page", data)
        self.assertIn("num_pages", data)
        self.assertIn("has_next", data)
        self.assertIn("has_previous", data)
        # Check that the admin's user_type is returned.
        self.assertEqual(data.get("user_type"), self.admin.user_type)
        # Check that the number of users returned on this page is as expected 
        # (paginator set to 2 per page).
        self.assertLessEqual(len(data["users"]), 2)

    def test_ambassador_can_access_paginated_view(self):
        """
        An ambassador should be able to access the paginated user list.
        """
        self.client.login(username="ambassadoruser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertIn("users", data)
        self.assertEqual(data.get("user_type"), self.ambassador.user_type)

    def test_normal_user_redirected(self):
        """
        A normal user should not be allowed to access this view and be redirected to home.
        """
        self.client.login(username="normaluser", password="testpass")
        response = self.client.get(self.url)
        # Since the view redirects non-admin/ambassador users, we expect a redirect response.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.home_url)

    def test_normal_user_redirected(self):
        self.client.login(username="normaluser", password="testpass")
        response = self.client.get(self.url, HTTP_ACCEPT="application/json")
        # DRF will return 403 Forbidden for authenticated users failing permission checks.
        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_unauthorized(self):
        response = self.client.get(self.url, HTTP_ACCEPT="application/json")
        # IsAuthenticated anonymous requests will be 403.
        self.assertEqual(response.status_code, 403)


class SuspendUnsuspendUserViewTest(TestCase):
    """
    Test suite for the Suspend/Unsuspend User view.

    This suite covers:
    - Admin user can suspend and unsuspend any user.
    - Ambassador user can suspend a normal user.
    - Ambassador user cannot suspend an admin user.
    - Normal user should be redirected to home.
    - Anonymous user should be redirected to login.
    """

    def setUp(self):
        # Create users with different roles
        # Admin (user_type=3)
        self.admin = User.objects.create_user(
            username="adminuser",
            password="testpass",
            email="admin@example.com",
            user_type=3
        )
        # Ambassador (user_type=2)
        self.ambassador = User.objects.create_user(
            username="ambassadoruser",
            password="testpass",
            email="ambassador@example.com",
            user_type=2
        )
        # Normal user (user_type=1)
        self.normal_user = User.objects.create_user(
            username="normaluser",
            password="testpass",
            email="normal@example.com",
            user_type=1,
            is_suspended=False
        )
        # Another normal user for additional testing.
        self.another_normal = User.objects.create_user(
            username="anothernormal",
            password="testpass",
            email="anothernormal@example.com",
            user_type=1,
            is_suspended=False
        )
        self.home_url = reverse("home")
        self.manage_users_url = reverse("manage_users")

    def _get_suspend_url(self, user_id):
        return reverse("suspend_unsuspend_user", kwargs={"user_id": user_id})

    def test_admin_can_suspend_and_unsuspend_user(self):
        """
        An admin should be able to suspend and unsuspend any user.
        """
        self.client.login(username="adminuser", password="testpass")
        url = self._get_suspend_url(self.normal_user.id)

        # Initially, normal_user is not suspended.
        self.assertFalse(self.normal_user.is_suspended)

        # Admin suspends the user.
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, self.manage_users_url)

        # Reload from DB.
        self.normal_user.refresh_from_db()
        self.assertTrue(self.normal_user.is_suspended)
        # Check for a success message in response messages.
        messages_list = list(response.context["messages"])
        self.assertTrue(any("suspended" in m.message.lower()
                        for m in messages_list))

        # Admin unsuspends the user.
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, self.manage_users_url)
        self.normal_user.refresh_from_db()
        self.assertFalse(self.normal_user.is_suspended)
        messages_list = list(response.context["messages"])
        self.assertTrue(any("unsuspended" in m.message.lower()
                        for m in messages_list))

    def test_ambassador_can_suspend_normal_user(self):
        """
        An ambassador should be able to suspend a normal user.
        """
        self.client.login(username="ambassadoruser", password="testpass")
        url = self._get_suspend_url(self.another_normal.id)

        # ambassador suspends the normal user.
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, self.manage_users_url)
        self.another_normal.refresh_from_db()
        self.assertTrue(self.another_normal.is_suspended)

    def test_ambassador_cannot_suspend_non_normal_user(self):
        """
        An ambassador should NOT be allowed to suspend a user who is not a normal user.
        For instance, trying to suspend an admin should return 403 Forbidden.
        """
        self.client.login(username="ambassadoruser", password="testpass")
        url = self._get_suspend_url(self.admin.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertIn("not allowed", response.content.decode().lower())
        # Ensure the admin's suspended status is unchanged.
        self.admin.refresh_from_db()
        self.assertFalse(self.admin.is_suspended)

    def test_normal_user_redirected(self):
        """
        A normal user should not be allowed to access this view and is redirected to home.
        """
        self.client.login(username="normaluser", password="testpass")
        url = self._get_suspend_url(self.another_normal.id)
        response = self.client.get(url)
        # Since the dispatch returns a redirect for users without permission,
        # expect a 302 redirect to the home page.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.home_url)

    def test_anonymous_user_redirected_to_login(self):
        """
        Anonymous users should be redirected to the login page.
        """
        url = self._get_suspend_url(self.normal_user.id)
        response = self.client.get(url)
        # LoginRequiredMixin should redirect anonymous users to the login URL.
        self.assertEqual(response.status_code, 302)
        # You can check that the login URL is in the redirection target.
        login_url = resolve_url("login")
        self.assertIn(login_url, response.url)


class UserProfileViewTest(TestCase):
    """
    Test suite for the User Profile view.

    This suite covers:
    - GET request to the profile page
    - POST request to update user information
    - POST request to update user password
    - POST request to update user email
    """

    def setUp(self):
        # Create a test user with an initial password and email.
        self.user_password = "InitialPass123"
        self.user = User.objects.create_user(
            username="testuser",
            password=self.user_password,
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
            bio="Initial bio",
            user_type=1
        )
        self.profile_url = reverse("profile")

    def test_get_profile_view_context(self):
        """
        GET request should return the profile view with three forms:
        update_information, update_password, and update_email.
        """
        self.client.login(username="testuser", password=self.user_password)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        # Check that the context contains our three form keys.
        self.assertIn("update_information", response.context)
        self.assertIn("update_password", response.context)
        self.assertIn("update_email", response.context)
        # Check that update_email is initialized with the user's current email.
        update_email_form = response.context["update_email"]
        self.assertEqual(update_email_form.initial.get(
            "email"), self.user.email)

    def test_post_update_information(self):
        """
        Submitting the update_information form should update the user's first_name,
        last_name, and bio.
        """
        self.client.login(username="testuser", password=self.user_password)
        new_data = {
            "update_information": "true",
            "first_name": "NewFirst",
            "last_name": "NewLast",
            "bio": "Updated bio",
        }
        response = self.client.post(self.profile_url, data=new_data)
        # Expect a redirect to the profile page on success.
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "NewFirst")
        self.assertEqual(self.user.last_name, "NewLast")
        self.assertEqual(self.user.bio, "Updated bio")

    def test_post_update_password_success(self):
        """
        Submitting valid data to update_password form should update the user's password.
        """
        self.client.login(username="testuser", password=self.user_password)
        new_password = "NewStrongPass456"
        password_data = {
            "update_password": "true",
            "current_password": self.user_password,
            "new_password": new_password,
            "repeat_new_password": new_password,
        }
        response = self.client.post(self.profile_url, data=password_data)
        # Successful password update redirects to profile.
        self.assertEqual(response.status_code, 302)
        # After password change, log out and check that the user can log in with new password.
        self.client.logout()
        user = authenticate(username="testuser", password=new_password)
        self.assertIsNotNone(user)

    def test_post_update_password_invalid(self):
        """
        Submitting invalid password data (e.g. wrong current password) should not update the password,
        and the view should re-render the form with errors.
        """
        self.client.login(username="testuser", password=self.user_password)
        password_data = {
            "update_password": "true",
            "current_password": "WrongPassword",
            "new_password": "NewPass1234",
            "repeat_new_password": "NewPass1234",
        }
        response = self.client.post(self.profile_url, data=password_data)
        # Expect the form to be re-rendered (status 200) with errors.
        self.assertEqual(response.status_code, 200)
        form = response.context.get("update_password")
        # Check that errors are present (for current_password).
        self.assertTrue(form.errors)
        self.assertIn("The current password is incorrect.",
                      form.errors.get("current_password", []))
        # Ensure password remains unchanged.
        user = User.objects.get(username="testuser")
        self.assertTrue(user.check_password(self.user_password))

    def test_post_update_email_success(self):
        """
        Submitting valid data to update_email form should update the user's email.
        """
        self.client.login(username="testuser", password=self.user_password)
        new_email = "updated@example.com"
        email_data = {
            "update_email": "true",
            "email": new_email,
        }
        response = self.client.post(self.profile_url, data=email_data)
        # Successful update redirects to profile.
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, new_email)

    def test_post_update_email_duplicate(self):
        """
        Submitting an email that's already in use should produce a form error.
        """
        # Create another user with a specific email.
        User.objects.create_user(
            username="otheruser",
            password="otherpass",
            email="duplicate@example.com",
            user_type=1
        )
        self.client.login(username="testuser", password=self.user_password)
        email_data = {
            "update_email": "true",
            "email": "duplicate@example.com",
        }
        response = self.client.post(self.profile_url, data=email_data)
        # Expect the form to be re-rendered with an error.
        self.assertEqual(response.status_code, 200)
        form = response.context.get("update_email")
        self.assertTrue(
            form.errors, f"Expected form errors but got: {form.errors}")
        self.assertIn("This email is already in use.",
                      form.errors.get("email", []))
        # Ensure the user's email remains unchanged.
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.email, "duplicate@example.com")
