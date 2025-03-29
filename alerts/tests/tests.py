import string
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.contrib.gis.geos import Point
from rest_framework import status
from hypothesis.extra.django import TestCase
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from datetime import timedelta
from django.utils import timezone
from django.http import HttpResponseForbidden
from unittest.mock import patch, MagicMock
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APITestCase
from django.contrib.gis.geos import Point
from django.db.models import Q

from alerts.tests.factories import (UserFactory, AlertFactory)
from users.models import User
from alerts.models import (Alert, Earthquake, Flood,
                           Tornado, Fire, AlertUserVote)



class HomeViewTest(TestCase):
    """
    Test the home view of the alerts app.

    This test case checks the following:
      - The home view returns a 200 status code.
      - The context contains the expected data.
      - The alerts are paginated to 4 per page.
      - The hazard_details_dict is processed correctly for each alert in page_obj.
      - The users in context are ordered by descending alerts_upvoted and filtered by is_suspended=False.
    """

    def setUp(self):
        # Create test users using factories.
        self.user1 = UserFactory(alerts_upvoted=20)
        self.user2 = UserFactory(alerts_upvoted=10)
        # This user is suspended so should not appear in the context.
        self.user3 = UserFactory(alerts_upvoted=15, is_suspended=True)

        # Create 5 alerts using the AlertFactory.
        # HomeView paginates alerts to 4 per page, so creating 5 helps test pagination.
        for i in range(5):
            AlertFactory.create(
                description=f"Test Alert {i}",
                location=Point(0, 0),
                country="Testland",
                city="Testcity",
                reported_by=self.user1,
                is_active=True,
                soft_deletion_time=now() + timedelta(days=2)
            )

    def test_home_view_status_and_context(self):
        """
        Verify that the HomeView returns a 200 status code and includes the required context variables.
        """
        url = reverse('home') 
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Verify that 'page_obj' (paginated alerts) is present in the context.
        self.assertIn('page_obj', response.context)
        # Verify that 'users' (top users by alerts_upvoted) is present in the context.
        self.assertIn('users', response.context)

    def test_home_view_pagination(self):
        """
        Ensure that the alerts are paginated properly (maximum 4 alerts on the first page).
        """
        url = reverse('home')
        response = self.client.get(url)
        page_obj = response.context['page_obj']
        # The first page should contain at most 4 alerts.
        self.assertLessEqual(len(page_obj.object_list), 4)

    def test_hazard_details_dict_processing(self):
        """
        Verify that each alert in page_obj has its hazard_details_dict properly created:
          - The 'id' key is removed.
          - Any None values are replaced by "Not provided".
        """
        url = reverse('home')
        response = self.client.get(url)
        page_obj = response.context['page_obj']

        for alert in page_obj:
            # Only test alerts that have hazard_details (via GenericForeignKey).
            if alert.hazard_details:
                hazard_dict = alert.hazard_details_dict
                # Check that the 'id' key is removed.
                self.assertNotIn('id', hazard_dict)
                # For each key in hazard_details_dict, ensure no None values exist.
                for key, value in hazard_dict.items():
                    self.assertIsNotNone(value)
                    if value is None:
                        self.assertEqual(value, "Not provided")

    def test_users_ordering_and_filtering(self):
        """
        Check that the context users list:
          - Only contains users that are not suspended.
          - Is ordered in descending order of alerts_upvoted.
        """
        url = reverse('home')
        response = self.client.get(url)
        users = list(response.context['users'])
        # Verify that no suspended user is present.
        for user in users:
            self.assertFalse(user.is_suspended)
        # Verify that the users are sorted by alerts_upvoted in descending order.
        upvotes = [user.alerts_upvoted for user in users]
        self.assertEqual(upvotes, sorted(upvotes, reverse=True))


class AboutViewTest(TestCase):
    """
    Test case for the AboutView.

    This class verifies that the About page:
      - Returns a 200 HTTP status.
      - Uses the correct template.
      - Provides a valid context.
    """

    def test_about_view_status_and_template(self):
        """
        Test that the AboutView returns a 200 status code and uses the 'alerts/about.html' template.
        """
        url = reverse('about')
        # Perform a GET request to the view.
        response = self.client.get(url)
        # Check that the response status code is 200.
        self.assertEqual(response.status_code, 200)
        # Verify that the correct template is used.
        self.assertTemplateUsed(response, 'alerts/about.html')
        # Check that the context is not None (even if no extra context is provided).
        self.assertIsNotNone(response.context)


class ManageAlertsViewTest(TestCase):
    """
    Test case for the ManageAlertsView.

    This class verifies that:
      - An authenticated user can access the manage alerts page.
      - The view returns the correct template and context.
      - Alerts are properly paginated and processed (hazard details adjusted).
    """

    def setUp(self):
        # Create and log in a user
        self.user = UserFactory()
        self.client.login(username=self.user.username, password='password123')

        # Create multiple alerts using the expanded AlertFactory.
        # We create 6 alerts to test pagination (view is set to 4 alerts per page).
        for i in range(6):
            AlertFactory.create(
                description=f"Test Alert {i}",
                location=Point(0, 0),
                country="Testland",
                city="Testcity",
                reported_by=self.user,
                is_active=True,
                soft_deletion_time=now() + timedelta(days=2)
            )

    def test_manage_alerts_view_status_and_context(self):
        """
        Ensure the ManageAlertsView is accessible for an authenticated user,
        uses the correct template, and contains the expected context.
        """
        url = reverse(
            'manage_alerts')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Check that the template is used
        self.assertTemplateUsed(response, 'alerts/manage_alerts.html')
        self.assertIn('page_obj', response.context)

        # For each alert, verify hazard_details_dict processing:
        page_obj = response.context['page_obj']
        for alert in page_obj:
            if alert.hazard_details:
                # The 'id' key should have been removed
                self.assertNotIn('id', alert.hazard_details_dict)
                # None values should be replaced with "Not Provided"
                for key, value in alert.hazard_details_dict.items():
                    self.assertIsNotNone(value)
                    if value is None:
                        self.assertEqual(value, "Not Provided")

    def test_manage_alerts_view_pagination(self):
        """
        Test that the alerts are paginated correctly (maximum of 4 alerts on the first page).
        """
        url = reverse('manage_alerts')
        response = self.client.get(url)
        page_obj = response.context['page_obj']
        self.assertLessEqual(len(page_obj.object_list), 4)


class AlertGeoJsonListViewTest(APITestCase):
    """
    Test case for the AlertGeoJsonListView.

    This class verifies that:
      - The view returns a 200 HTTP status.
      - The response is in GeoJSON format (FeatureCollection).
      - Only active alerts are returned.
      - Each feature contains hazard type and hazard details.
    """

    def setUp(self):
        # Create a few active alerts.
        self.active_alerts = []
        for i in range(3):
            alert = AlertFactory.create(
                description=f"Active Alert {i}",
                location=Point(1, 1),
                is_active=True,
            )
            self.active_alerts.append(alert)
        # Create an inactive alert which should be filtered out.
        AlertFactory.create(
            description="Inactive Alert",
            location=Point(2, 2),
            is_active=False,
        )
        # Get the URL for the GeoJSON view.
        self.url = reverse('alerts-geojson') 

    def test_alert_geojson_list_status_and_format(self):
        """
        Ensure that the AlertGeoJsonListView returns a 200 status code and valid GeoJSON.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # Check that the response is JSON.
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        # Verify that the top-level GeoJSON type is 'FeatureCollection'.
        self.assertEqual(data.get('type'), 'FeatureCollection')
        # Check that the number of features equals the number of active alerts.
        features = data.get('features', [])
        self.assertEqual(len(features), len(self.active_alerts))

    def test_geojson_feature_properties(self):
        """
        Verify that each GeoJSON feature includes hazard type and hazard details.
        """
        response = self.client.get(self.url)
        data = response.json()
        features = data.get('features', [])
        for feature in features:
            properties = feature.get('properties', {})
            # Check that hazard_type is provided 
            self.assertIn('hazard_type', properties)
            # Check that hazard_details is provided.
            self.assertIn('hazard_details', properties)


class CreateAlertViewTest(APITestCase):
    """
    Test case for the CreateAlertView.

    This class verifies that:
      - A missing latitude or longitude returns an error.
      - An invalid effect radius returns an error.
      - An invalid hazard type returns an error.
      - Reverse geocoding errors are handled.
      - A valid POST request creates an alert successfully and returns the expected JSON.
    """

    def setUp(self):
        # Create and authenticate a test user.
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.url = reverse('create_alert')
        # Basic valid data for an alert creation request.
        self.valid_data = {
            "lat": 40.7128,
            "lng": -74.0060,
            "effect_radius": 5000,
            "description": "Test Alert Description",
            "source_url": "http://example.com",
            "hazard_type": "earthquake",
            "hazard_data": {
                "magnitude": 6.2,
                "depth": 12.0,
                "epicenter_description": "Near test location"
            }
        }
        fake_token = MagicMock()
        fake_token.user = self.user
        self.client.force_authenticate(user=self.user, token=fake_token)

    def test_missing_lat_lng(self):
        """
        Ensure that missing latitude or longitude results in a 400 response with the appropriate error message.
        """
        data = self.valid_data.copy()
        data.pop("lat")
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_invalid_effect_radius(self):
        """
        Ensure that an effect radius that is too high or negative returns a 400 error with the correct message.
        """
        for invalid_radius in [-10, 150000]:
            data = self.valid_data.copy()
            data["effect_radius"] = invalid_radius
            response = self.client.post(self.url, data, format='json')
            self.assertEqual(response.status_code, 400)

    def test_invalid_hazard_type(self):
        """
        Ensure that providing an invalid hazard type returns a 400 error with the correct message.
        """
        data = self.valid_data.copy()
        data["hazard_type"] = "invalid_hazard"
        with patch("alerts.views.Nominatim") as mock_nominatim:
            # Patch reverse geocoding to return a valid location.
            fake_location = MagicMock()
            fake_location.raw = {"address": {"country": "USA", "city": "New York", "county": "New York County"}}
            instance = mock_nominatim.return_value
            instance.reverse.return_value = fake_location
            response = self.client.post(self.url, data, format='json')
            self.assertEqual(response.status_code, 400)

    def test_reverse_geocoding_failure(self):
            """
            Simulate a failure in reverse geocoding and ensure it returns a 400 error with an appropriate message.
            """
            data = self.valid_data.copy()
            with patch("alerts.views.Nominatim") as mock_nominatim:
                # Simulate an exception during reverse geocoding.
                instance = mock_nominatim.return_value
                instance.reverse.side_effect = Exception("Geocoding error")
                response = self.client.post(self.url, data, format='json')
                self.assertEqual(response.status_code, 400)

    @patch("alerts.views.Nominatim")
    def test_successful_alert_creation(self, mock_nominatim):
        """
        Ensure that a valid POST request creates an alert successfully and returns the expected JSON response.
        """
        data = self.valid_data.copy()

        # Patch reverse geocoding to return a fake location with address details.
        fake_location = MagicMock()
        fake_location.raw = {
            "address": {
                "country": "USA",
                "city": "New York",
                "town": "New York",
                "county": "New York County"
            }
        }
        instance = mock_nominatim.return_value
        instance.reverse.return_value = fake_location

        response = self.client.post(self.url, data, format='json')
        response_data = response.data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Verify that the response includes key fields.
        self.assertIn("id", response_data)
        self.assertEqual(response_data.get("description"), data["description"])
        self.assertEqual(response_data.get("effect_radius"), data["effect_radius"])
        self.assertEqual(response_data.get("hazard_type"), data["hazard_type"])
        self.assertEqual(response_data.get("hazard_details"), data["hazard_data"])
        self.assertEqual(response_data.get("reported_by"), str(self.user))
        self.assertEqual(response_data.get("source_url"), data["source_url"])
        self.assertEqual(response_data.get("country"), "USA")
        self.assertEqual(response_data.get("city"), "New York")
        self.assertEqual(response_data.get("county"), "New York County")

        # Verify that the alert is created in the database.
        self.assertTrue(Alert.objects.filter(id=response_data["id"]).exists())

        # Verify that the user's alerts_created count has been incremented.
        self.user.refresh_from_db()
        self.assertEqual(self.user.alerts_created, 1)


class AlertsPaginatedViewTest(APITestCase):
    """
    Test case for the AlertsPaginatedView.
    
    This class verifies that:
      - The view returns the correct paginated alerts.
      - The alerts are sorted by created_at in descending order.
      - The view handles search queries correctly.
      - The view filters out inactive alerts.
    """
    
    def setUp(self):
        self.url = reverse('paginated_alert')
        # Create 10 active alerts with decreasing created_at so the most recent comes first.
        # Page size in the view is 4, so we expect 3 pages (4, 4, and 2 items).
        for i in range(10):
            Alert.objects.create(
                description=f"Test alert {i}",
                location=Point(0 + i, 0 + i),
                effect_radius=1000 + i,
                reported_by=None,
                source_url="http://example.com",
                country="Testland",
                city="Test City",
                county="Test County",
                is_active=True,
                created_at=timezone.now() - timedelta(minutes=i)
            )

        # Create one inactive alert which should not appear in the results.
        Alert.objects.create(
            description="Inactive alert",
            location=Point(0, 0),
            effect_radius=500,
            reported_by=None,
            source_url="http://example.com",
            country="Testland",
            city="Test City",
            county="Test County",
            is_active=False,
            created_at=timezone.now()
        )

    def test_get_first_page_alerts(self):
        """
        Test that a GET request without a search query returns the first page of active alerts.
        Expecting 4 alerts, page 1, with has_next True and has_previous False.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertIn("alerts", data)
        self.assertEqual(len(data["alerts"]), 4)
        self.assertEqual(data["page"], 1)
        self.assertEqual(data["num_pages"], 3)
        self.assertTrue(data["has_next"])
        self.assertFalse(data["has_previous"])

    def test_get_second_page_alerts(self):
        """
        Test that requesting page 2 returns the correct set of alerts.
        """
        response = self.client.get(self.url, {'page': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data["page"], 2)
        # Page 2 should also have 4 alerts.
        self.assertEqual(len(data["alerts"]), 4)
        self.assertTrue(data["has_next"])
        self.assertTrue(data["has_previous"])

    def test_get_last_page_alerts(self):
        """
        Test that requesting page 3 returns the last set of alerts.
        """
        response = self.client.get(self.url, {'page': 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data["page"], 3)
        # Since we created 10 active alerts, page 3 should have 2 alerts.
        self.assertEqual(len(data["alerts"]), 2)
        self.assertFalse(data["has_next"])
        self.assertTrue(data["has_previous"])

    def test_search_alerts(self):
        """
        Create an alert with a unique term and then use a search query to filter it.
        """
        # Create a unique alert that should be found by the search query.
        unique_alert = Alert.objects.create(
            description="Unique search term alert",
            location=Point(10, 10),
            effect_radius=2000,
            reported_by=None,
            source_url="http://example.com",
            country="Testland",
            city="Test City",
            county="Test County",
            is_active=True,
            created_at=timezone.now()
        )
        # The search query will match part of the description.
        response = self.client.get(self.url, {'q': 'Unique search'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        # We expect at least one alert to be returned.
        self.assertGreaterEqual(len(data["alerts"]), 1)
        # Confirm that the unique alert is among the results.
        descriptions = [alert["description"] for alert in data["alerts"]]
        self.assertIn("Unique search term alert", descriptions)


class AlertDetailsAndEditViewTest(TestCase):
    """
    Test case for the AlertDetailsAndEditView.
    
    This class verifies that:
      - The view returns the correct context for both owners and non-owners.
      - The view handles GET and POST requests correctly.
      - The view processes hazard details appropriately.
    """
    
    def setUp(self):
        # Create two users: one will be the owner and one a non-owner.
        self.owner = User.objects.create_user(
            username='owner', password='testpass', email='owner@example.com'
        )
        self.non_owner = User.objects.create_user(
            username='nonowner', password='testpass', email='nonowner@example.com'
        )
        # For permission methods, we assume neither has admin or ambassador rights by default.
        self.owner.is_admin = lambda: False
        self.owner.is_ambassador = lambda: False
        self.non_owner.is_admin = lambda: False
        self.non_owner.is_ambassador = lambda: False

        # Create a basic alert (without hazard details)
        self.alert = Alert.objects.create(
            description="Original alert description",
            location=Point(10.0, 20.0),
            effect_radius=5000,
            reported_by=self.owner,
            source_url="http://example.com/original",
            country="CountryA",
            city="CityA",
            county="CountyA",
            is_active=True,
            created_at=timezone.now() - timedelta(minutes=5)
        )
        # Ensure hazard details are empty
        self.alert.hazard_details = None
        self.alert.save()

    def test_get_context_as_owner_without_hazard(self):
        """
        Verify that an owner (without a hazard) sees the correct context flags,
        and that hazard-related context is not injected.
        """
        self.client.force_login(self.owner)
        url = reverse('alert_details', kwargs={'pk': self.alert.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        context = response.context
        alert_context = context.get('alert')
        self.assertIsNotNone(alert_context)
        # Owner should have editing permissions.
        self.assertTrue(context.get('can_edit'))
        self.assertTrue(context.get('can_vote'))
        self.assertTrue(context.get('can_delete'))
        # Without extra permissions, can_archive is False.
        self.assertFalse(context.get('can_archive'))
        # Since there is no hazard details, hazard_type should be None.
        self.assertIsNone(alert_context.hazard_type)
        self.assertIsNone(alert_context.hazard_details_dict)

    def test_get_context_as_owner_with_hazard(self):
        """
        Create an Earthquake hazard instance and attach it to the alert.
        Verify that the GET context includes dynamic hazard fields.
        """
        # Create an Earthquake hazard instance.
        earthquake = Earthquake.objects.create(
            magnitude=5.0,
            depth=10.0,
            epicenter_description="Old epicenter description"
        )
        # Associate the hazard with the alert.
        self.alert.hazard_details = earthquake
        self.alert.content_type = ContentType.objects.get_for_model(Earthquake)
        self.alert.object_id = earthquake.id
        self.alert.save()

        self.client.force_login(self.owner)
        url = reverse('alert_details', kwargs={'pk': self.alert.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        context = response.context
        alert_context = context.get('alert')
        # The view should attach hazard_type and hazard_details_dict.
        self.assertEqual(alert_context.hazard_type, 'earthquake')
        self.assertIsNotNone(alert_context.hazard_details_dict)
        # The dictionary should contain the fields from EarthquakeForm except the "id".
        self.assertNotIn('id', alert_context.hazard_details_dict)
        self.assertIn('magnitude', alert_context.hazard_details_dict)
        self.assertIn('depth', alert_context.hazard_details_dict)
        self.assertIn('epicenter_description', alert_context.hazard_details_dict)
        # If any field is None, it should be replaced with "N/A".
        for value in alert_context.hazard_details_dict.values():
            self.assertNotEqual(value, None)

    def test_post_edit_as_owner_without_hazard(self):
        """
        As the owner, submit a valid update for an alert without hazard details.
        """
        self.client.force_login(self.owner)
        url = reverse('alert_details', kwargs={'pk': self.alert.pk})
        valid_soft_deletion = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
        form_data = {
            "description": "Updated description",
            "effect_radius": 6000,
            "soft_deletion_time": valid_soft_deletion,
            "country": "CountryB",
            "city": "CityB",
            "county": "CountyB",
            "source_url": "http://example.com/updated",
        }
        response = self.client.post(url, data=form_data)
        # On successful update, the view should redirect.
        self.assertEqual(response.status_code, 302)
        # Confirm that the alert was updated.
        self.alert.refresh_from_db()
        self.assertEqual(self.alert.description, "Updated description")
        self.assertEqual(self.alert.effect_radius, 6000)
        self.assertEqual(self.alert.country, "CountryB")
        self.assertEqual(self.alert.city, "CityB")
        self.assertEqual(self.alert.county, "CountyB")
        # The success URL should point back to alert details.
        expected_url = reverse('alert_details', kwargs={'pk': self.alert.pk})
        self.assertEqual(response.url, expected_url)

    def test_post_edit_as_owner_with_hazard(self):
        """
        As the owner, update an alert that has associated Earthquake hazard details.
        The test submits both the alert fields and hazard fields.
        """
        # Create and associate an Earthquake instance.
        earthquake = Earthquake.objects.create(
            magnitude=5.0,
            depth=10.0,
            epicenter_description="Old epicenter description"
        )
        self.alert.hazard_details = earthquake
        self.alert.content_type = ContentType.objects.get_for_model(Earthquake)
        self.alert.object_id = earthquake.id
        self.alert.save()

        self.client.force_login(self.owner)
        url = reverse('alert_details', kwargs={'pk': self.alert.pk})
        valid_soft_deletion = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
        # Include both the alert fields and hazard fields from EarthquakeForm.
        form_data = {
            "description": "Updated description with hazard",
            "effect_radius": 7000,
            "soft_deletion_time": valid_soft_deletion,
            "country": "CountryC",
            "city": "CityC",
            "county": "CountyC",
            "source_url": "http://example.com/hazard-updated",
            "magnitude": 6.5,
            "depth": 15.0,
            "epicenter_description": "New epicenter description"
        }
        response = self.client.post(url, data=form_data)
        # Expect a redirect on successful update.
        self.assertEqual(response.status_code, 302)
        # Refresh alert and hazard data.
        self.alert.refresh_from_db()
        earthquake.refresh_from_db()
        self.assertEqual(self.alert.description, "Updated description with hazard")
        self.assertEqual(self.alert.effect_radius, 7000)
        self.assertEqual(self.alert.country, "CountryC")
        self.assertEqual(self.alert.city, "CityC")
        self.assertEqual(self.alert.county, "CountyC")
        # Check that the hazard details were updated.
        self.assertEqual(earthquake.magnitude, 6.5)
        self.assertEqual(earthquake.depth, 15.0)
        self.assertEqual(earthquake.epicenter_description, "New epicenter description")
        # Confirm redirection to the alert details page.
        expected_url = reverse('alert_details', kwargs={'pk': self.alert.pk})
        self.assertEqual(response.url, expected_url)

    def test_post_edit_as_non_owner(self):
        """
        A non-owner without proper permissions should not be able to edit the alert.
        """
        self.client.force_login(self.non_owner)
        url = reverse('alert_details', kwargs={'pk': self.alert.pk})
        valid_soft_deletion = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
        form_data = {
            "description": "Illegal update attempt",
            "effect_radius": 8000,
            "soft_deletion_time": valid_soft_deletion,
            "country": "CountryX",
            "city": "CityX",
            "county": "CountyX",
            "source_url": "http://example.com/illegal",
        }
        response = self.client.post(url, data=form_data)
        # The view should return 403 Forbidden.
        self.assertEqual(response.status_code, 403)
        # Verify that the alert remains unchanged.
        self.alert.refresh_from_db()


class AlertDeleteViewTest(TestCase):
    """
    Test case for the AlertDeleteView.
    
    This class verifies that:
      - The owner can delete their own alert.
      - A non-owner cannot delete someone else's alert.
      - An admin or ambassador can delete any alert.
      - Anonymous users are redirected to the login page.
    """
    
    def setUp(self):
        # Create a normal user (owner, user_type=1)
        self.owner = User.objects.create_user(
            username='owner',
            password='testpass',
            email='owner@example.com',
            user_type=1
        )
        # Create another normal user (non-owner, user_type=1)
        self.non_owner = User.objects.create_user(
            username='nonowner',
            password='testpass',
            email='nonowner@example.com',
            user_type=1
        )
        # Create an ambassador (user_type=2)
        self.ambassador = User.objects.create_user(
            username='ambassador',
            password='testpass',
            email='ambassador@example.com',
            user_type=2
        )
        # Create an admin (user_type=3)
        self.admin = User.objects.create_user(
            username='admin',
            password='testpass',
            email='admin@example.com',
            user_type=3
        )
        # Create an alert owned by the owner.
        self.alert = Alert.objects.create(
            description="Alert to delete",
            location=Point(10, 10),
            effect_radius=5000,
            reported_by=self.owner,
            source_url="http://example.com",
            country="Testland",
            city="Testcity",
            county="Testcounty",
            is_active=True,
            created_at=timezone.now() - timedelta(minutes=10)
        )
        self.delete_url = reverse('delete_alert', kwargs={'pk': self.alert.pk})

    def test_owner_can_delete_alert(self):
        """
        The owner (normal user) should be able to delete their own alert.
        """
        self.client.login(username='owner', password='testpass')
        response = self.client.post(self.delete_url)
        # A successful delete should redirect (status 302).
        self.assertEqual(response.status_code, 302)
        # The alert should no longer exist.
        self.assertFalse(Alert.objects.filter(pk=self.alert.pk).exists())
        # Verify redirection to the manage alerts page.
        self.assertEqual(response.url, reverse('manage_alerts'))

    def test_non_owner_cannot_delete_alert(self):
        """
        A normal user (non-owner) should not be able to delete someone else's alert.
        """
        self.client.login(username='nonowner', password='testpass')
        response = self.client.post(self.delete_url)
        # The view should return 403 Forbidden.
        self.assertEqual(response.status_code, 403)
        # The alert should still exist.
        self.assertTrue(Alert.objects.filter(pk=self.alert.pk).exists())

    def test_admin_can_delete_alert(self):
        """
        An admin (user_type=3) should be able to delete any alert.
        """
        self.client.login(username='admin', password='testpass')
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Alert.objects.filter(pk=self.alert.pk).exists())
        self.assertEqual(response.url, reverse('manage_alerts'))

    def test_ambassador_can_delete_alert(self):
        """
        An ambassador (user_type=2) should be able to delete any alert.
        """
        self.client.login(username='ambassador', password='testpass')
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Alert.objects.filter(pk=self.alert.pk).exists())
        self.assertEqual(response.url, reverse('manage_alerts'))

    def test_anonymous_cannot_delete_alert(self):
        """
        Anonymous users should be redirected to the login page.
        """
        response = self.client.post(self.delete_url)
        # LoginRequiredMixin should cause a redirect (status 302) to the login page.
        self.assertEqual(response.status_code, 302)
        # The alert should still exist.
        self.assertTrue(Alert.objects.filter(pk=self.alert.pk).exists())


class AlertVoteViewTest(TestCase):
    """
    Test case for the AlertVoteView.
    
    This class verifies that:
      - A valid upvote creates an AlertUserVote and updates the alert's positive_votes.
      - A valid downvote creates an AlertUserVote and updates the alert's negative_votes.   
      - Repeating the same vote deletes the vote and updates the alert's counts.
      - Changing a vote from upvote to downvote updates the alert's counts accordingly.
    """
    
    def setUp(self):
        # Create the alert owner (user who created the alert).
        self.owner = User.objects.create_user(
            username='owner',
            password='testpass',
            email='owner@example.com',
            user_type=1  # normal user
        )
        # Create a voter who will cast votes.
        self.voter = User.objects.create_user(
            username='voter',
            password='testpass',
            email='voter@example.com',
            user_type=1  # normal user
        )
        # Create an alert owned by self.owner.
        self.alert = Alert.objects.create(
            description="Alert for voting",
            location=Point(0, 0),
            effect_radius=5000,
            reported_by=self.owner,
            source_url="http://example.com",
            country="Testland",
            city="Testcity",
            county="Testcounty",
            is_active=True,
            created_at=timezone.now() - timedelta(minutes=5),
            positive_votes=0,
            negative_votes=0
        )
        # Ensure owner's alerts_upvoted count starts at 0.
        self.owner.alerts_upvoted = 0
        self.owner.save()
        self.vote_url = reverse('vote_alert', kwargs={'pk': self.alert.pk})

    def test_upvote_creation(self):
        """
        A valid upvote should create an AlertUserVote, increase alert.positive_votes,
        and increment the alert owner's alerts_upvoted.
        """
        self.client.login(username='voter', password='testpass')
        response = self.client.post(self.vote_url, data={'vote': '1'})
        # Expect a redirect back to alert_details.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('alert_details', kwargs={'pk': self.alert.pk}))

        self.alert.refresh_from_db()
        self.owner.refresh_from_db()

        # Since this is the first vote, positive_votes should increase by 1.
        self.assertEqual(self.alert.positive_votes, 1)
        # Negative votes remain unchanged.
        self.assertEqual(self.alert.negative_votes, 0)
        # Owner's alerts_upvoted count increased by 1.
        self.assertEqual(self.owner.alerts_upvoted, 1)
        # A vote record should exist for this voter.
        vote = AlertUserVote.objects.filter(alert=self.alert, user=self.voter).first()
        self.assertIsNotNone(vote)
        self.assertTrue(vote.vote)

    def test_downvote_creation(self):
        """
        A valid downvote should create an AlertUserVote and increase alert.negative_votes.
        For downvotes, the owner's alerts_upvoted is not adjusted.
        """
        self.client.login(username='voter', password='testpass')
        response = self.client.post(self.vote_url, data={'vote': '-1'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('alert_details', kwargs={'pk': self.alert.pk}))

        self.alert.refresh_from_db()
        self.owner.refresh_from_db()

        self.assertEqual(self.alert.negative_votes, 1)
        self.assertEqual(self.alert.positive_votes, 0)
        # For downvotes, owner's alerts_upvoted is not incremented.
        self.assertEqual(self.owner.alerts_upvoted, 0)
        vote = AlertUserVote.objects.filter(alert=self.alert, user=self.voter).first()
        self.assertIsNotNone(vote)
        self.assertFalse(vote.vote)

    def test_repeating_same_vote_deletes_vote(self):
        """
        If the voter votes the same way twice (upvote in this test), the vote is deleted.
        The alert's positive_votes decreases and owner's alerts_upvoted is reduced.
        """
        self.client.login(username='voter', password='testpass')
        # First upvote.
        self.client.post(self.vote_url, data={'vote': '1'})
        # Second upvote (should delete the vote).
        response = self.client.post(self.vote_url, data={'vote': '1'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('alert_details', kwargs={'pk': self.alert.pk}))

        self.alert.refresh_from_db()
        self.owner.refresh_from_db()
        # The vote was removed, so positive_votes should be back to 0.
        self.assertEqual(self.alert.positive_votes, 0)
        # Owner's alerts_upvoted should be reduced accordingly.
        self.assertEqual(self.owner.alerts_upvoted, 0)
        # The vote record should no longer exist.
        vote = AlertUserVote.objects.filter(alert=self.alert, user=self.voter).first()
        self.assertIsNone(vote)

    def test_change_vote(self):
        """
        If a voter changes their vote from upvote to downvote,
        the alert's counts and the owner's alerts_upvoted should update accordingly.
        """
        self.client.login(username='voter', password='testpass')
        # First, cast an upvote.
        self.client.post(self.vote_url, data={'vote': '1'})
        # Now change to downvote.
        response = self.client.post(self.vote_url, data={'vote': '-1'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('alert_details', kwargs={'pk': self.alert.pk}))

        self.alert.refresh_from_db()
        self.owner.refresh_from_db()
        # Changing vote: subtract one from positive_votes, add one to negative_votes.
        self.assertEqual(self.alert.positive_votes, 0)
        self.assertEqual(self.alert.negative_votes, 1)
        # When switching from upvote to downvote, owner's alerts_upvoted is decreased by 1.
        self.assertEqual(self.owner.alerts_upvoted, 0)
        vote = AlertUserVote.objects.filter(alert=self.alert, user=self.voter).first()
        self.assertIsNotNone(vote)
        self.assertFalse(vote.vote)

    def test_invalid_vote_value(self):
        """
        An invalid vote value should return a 400 Bad Request.
        """
        self.client.login(username='voter', password='testpass')
        response = self.client.post(self.vote_url, data={'vote': 'abc'})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid vote type", response.content.decode())

    def test_anonymous_vote(self):
        """
        Anonymous users should be redirected to the login page.
        """
        response = self.client.post(self.vote_url, data={'vote': '1'})
        # LoginRequiredMixin should trigger a redirect.
        self.assertEqual(response.status_code, 302)
        # Ensure that no vote is recorded.
        vote = AlertUserVote.objects.filter(alert=self.alert).first()
        self.assertIsNone(vote)


class ArchiveAlertViewTest(TestCase):
    """
    Test case for the ArchiveAlertView.
    
    This class verifies that:
      - An admin can archive an alert.
      - An ambassador can archive an alert.
      - A normal user cannot archive an alert.
      - An anonymous user is redirected to the login page.
    """
    
    def setUp(self):
        # Create users with different types:
        # Normal user (user_type=1)
        self.normal_user = User.objects.create_user(
            username='normal',
            password='testpass',
            email='normal@example.com',
            user_type=1
        )
        # Ambassador (user_type=2)
        self.ambassador = User.objects.create_user(
            username='ambassador',
            password='testpass',
            email='ambassador@example.com',
            user_type=2
        )
        # Admin (user_type=3)
        self.admin = User.objects.create_user(
            username='admin',
            password='testpass',
            email='admin@example.com',
            user_type=3
        )
        # Create an alert that is initially active.
        self.alert = Alert.objects.create(
            description="Alert to archive",
            location=Point(10, 10),
            effect_radius=5000,
            reported_by=self.normal_user,
            source_url="http://example.com",
            country="Testland",
            city="Testcity",
            county="Testcounty",
            is_active=True,
            created_at=timezone.now() - timedelta(minutes=10)
        )
        self.archive_url = reverse('archive_alert', kwargs={'pk': self.alert.pk})

    def test_admin_can_archive_alert(self):
        """
        An admin should be able to archive an alert via POST.
        The alert's is_active flag should be set to False and the user is redirected.
        """
        self.client.login(username='admin', password='testpass')
        response = self.client.post(self.archive_url)
        # A successful archive should redirect to the manage alerts page.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('manage_alerts'))
        self.alert.refresh_from_db()
        self.assertFalse(self.alert.is_active)

    def test_ambassador_can_archive_alert(self):
        """
        An ambassador should be able to archive an alert via POST.
        """
        self.client.login(username='ambassador', password='testpass')
        response = self.client.post(self.archive_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('manage_alerts'))
        self.alert.refresh_from_db()
        self.assertFalse(self.alert.is_active)

    def test_normal_user_cannot_archive_alert(self):
        """
        A normal user should not have permission to archive an alert.
        The view should return a 403 and the alert remains active.
        """
        self.client.login(username='normal', password='testpass')
        response = self.client.post(self.archive_url)
        self.assertEqual(response.status_code, 403)
        self.alert.refresh_from_db()
        self.assertTrue(self.alert.is_active)

    def test_anonymous_user_redirected(self):
        """
        Anonymous users should be redirected to the login page.
        """
        response = self.client.post(self.archive_url)
        # LoginRequiredMixin should cause a redirect to the login page.
        self.assertEqual(response.status_code, 302)
        self.alert.refresh_from_db()
        self.assertTrue(self.alert.is_active)

