from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework import status



class RecoveryTest(APITestCase):
    def setUp(self):
        # We want to go ahead and originally create a user.
        kwargs = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
            "is_active": True
        }
        self.test_user = User.objects.create(**kwargs)

    def test_recovery_password_request(self):
        data = {
            'email': self.test_user.email
        }

        response = self.client.post(reverse('password_recovery_request'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('recovery_key', response.data)

    def test_recovery_password(self):
        data = {
            'email': self.test_user.email
        }
        response = self.client.post(reverse('password_recovery_request'), data, format='json')

        data = {
        	"new_password": "newpassword",
        	"repeated_password": "newpassword"
        }

        response = self.client.put(reverse('password_recovery', kwargs={'code': response.data['recovery_key']}), data, format='json')
        self.test_user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check if password is changed
        self.assertEqual(self.test_user.check_password(data['new_password']), True)
        # user should not be able to login with old passwod
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_recovery_username(self):
        data = {
            'email': self.test_user.email
        }
        response = self.client.post(reverse('username_recovery'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, "Email was successfully sent")

    def test_error_recovery_username(self):
        data = {
            'email': 'wrong@example.com'
        }
        response = self.client.post(reverse('username_recovery'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Not found.")

    def test_recovery_username_missing_data(self):
        data = {
            'email': ''
        }
        response = self.client.post(reverse('username_recovery'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, "Missing email")

