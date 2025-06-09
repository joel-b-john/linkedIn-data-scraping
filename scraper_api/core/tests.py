from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from unittest.mock import patch

class LinkedInProfileAPITest(APITestCase):
    def setUp(self):
        self.url = reverse('linkedin_profile')
        self.token_url = reverse('token_obtain_pair')  # This is from your urls.py for JWT
        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Obtain JWT token by logging in
        response = self.client.post(self.token_url, data={
            'username': 'testuser',
            'password': 'testpass'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.access_token = response.data['access']

    @patch('core.views.login_and_get_cookies')
    @patch('core.views.fetch_profile_data')
    @patch('core.views.load_cookies_if_valid')
    def test_successful_profile_fetch(self, mock_load_cookies, mock_fetch_profile, mock_login):
        mock_load_cookies.return_value = None
        mock_login.return_value = {'cookie_key': 'cookie_value'}
        mock_fetch_profile.return_value = {
            "loggedInUser": {
                "firstName": "John",
                "lastName": "Doe",
                "profileId": "123456789",
                "publicProfileUrl": "https://www.linkedin.com/in/john-doe"
            },
            "connections": [],
            "pagination": {
                "start": 0,
                "count": 0,
                "nextStart": 0
            }
        }

        # Set JWT auth header
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

        response = self.client.post(self.url, data={
            'email': 'test@example.com',
            'password': 'testpassword'
        }, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertIn('loggedInUser', response.json())
