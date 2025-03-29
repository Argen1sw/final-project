# Python Imports
from datetime import timedelta

# Django Imports
from django.urls import reverse
from django.utils import timezone
from django.contrib.gis.geos import Point
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch, MagicMock

# Local Imports
from alerts.models import Alert
from users.models import User


class ListAlertsAPIViewTest(APITestCase):
    """
    Test cases for the ListAlertsAPIView.

    This test case checks the behavior of the API when listing alerts.
    It verifies that the API returns the correct GeoJSON format for authenticated users
    and handles unauthenticated requests appropriately.
    """

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',
            email='testuser@example.com',
            user_type=1
        )
        # Create several alerts
        for i in range(3):
            Alert.objects.create(
                description=f"Alert {i}",
                location=Point(10 + i, 20 + i),
                effect_radius=5000 + i,
                reported_by=self.user,
                source_url="http://example.com",
                country="Testland",
                city="Testcity",
                county="Testcounty",
                is_active=True,
                created_at=timezone.now() - timedelta(minutes=i)
            )
        self.url = reverse('list_alerts')

    def test_list_alerts_authenticated(self):
        """
        An authenticated user should receive a GeoJSON FeatureCollection of alerts.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        # The response should be in
        # GeoJSON FeatureCollection format.
        # Verify required keys exist.
        self.assertEqual(data.get("type"), "FeatureCollection")
        self.assertIn("features", data)
        self.assertEqual(len(data["features"]), 3)

        # Optionally, verify one feature's structure.
        feature = data["features"][0]
        self.assertEqual(feature.get("type"), "Feature")
        self.assertIn("geometry", feature)
        self.assertIn("properties", feature)
        self.assertIn("description", feature["properties"])

    def test_list_alerts_unauthenticated(self):
        """
        An unauthenticated request should be rejected.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CreateAlertAPIViewTest(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',
            email='test@example.com',
            user_type=1
        )
        # Create a fake token with a user attribute (used in serializer: request.auth.user)
        fake_token = MagicMock()
        fake_token.user = self.user
        self.client.force_authenticate(user=self.user, token=fake_token)

        self.url = reverse('create_alert_api')
        self.valid_data = {
            "lat": 40.7128,
            "lng": -74.0060,
            "effect_radius": 5000,
            "hazard_type": "earthquake",
            "hazard_data": {
                "magnitude": 6.2,
                "depth": 12.0,
                "epicenter_description": "Test location"
            },
            "description": "Test Alert Description",
            "source_url": "http://example.com"
        }

    @patch("api_tokens.serializers.Nominatim")
    def test_create_alert_success(self, mock_nominatim):
        """
        Test that a valid POST creates an Alert and returns 201.
        """
        # Patch reverse geocoding to return a fake location.
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

        response = self.client.post(
            self.url, data=self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.data
        # Check that a new alert was created with the provided description.
        self.assertIn("id", data)
        self.assertEqual(data.get("description"),
                         self.valid_data["description"])
        self.assertTrue(Alert.objects.filter(pk=data["id"]).exists())

    @patch("api_tokens.serializers.Nominatim")
    def test_create_alert_invalid_effect_radius(self, mock_nominatim):
        """
        Test that an invalid effect_radius (e.g., 150000) results in a 400 error.
        """
        invalid_data = self.valid_data.copy()
        invalid_data["effect_radius"] = 150000
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

        response = self.client.post(self.url, data=invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("The radius of effect cannot exceed",
                      str(response.data.get("effect_radius", "")))

    @patch("api_tokens.serializers.Nominatim")
    def test_create_alert_invalid_hazard_type(self, mock_nominatim):
        """
        Test that an invalid hazard_type results in a 400 error.
        """
        invalid_data = self.valid_data.copy()
        invalid_data["hazard_type"] = "invalid"
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

        response = self.client.post(self.url, data=invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid hazard type", str(
            response.data.get("hazard_type", "")))

    @patch("api_tokens.serializers.Nominatim")
    def test_create_alert_geocoding_failure(self, mock_nominatim):
        """
        Test that a geocoding exception results in a 400 error.
        """
        instance = mock_nominatim.return_value
        instance.reverse.side_effect = Exception("Geocoding error")
        response = self.client.post(
            self.url, data=self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Geocoding failed", str(
            response.data.get("geocoding", "")))
