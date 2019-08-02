from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from terraPorta.apps.accounts.models import Profile


class AccountsTest(APITestCase):
    def setUp(self):
        # We want to go ahead and originally create a user.
        self.test_user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'})
        self.token = response.data['token']

        # URL for creating an account.
        self.create_url = reverse('users')

    def test_create_user(self):
        """
        Ensure we can create a new user and a valid token is created with it.
        """
        data = {
            'username': 'mara',
            'email': 'mara@example.com',
            'password': 'somepassword',
            'is_active': False,
            'org': {
                'name': 'Test organizacija',
                'location': 'Novi Sad'
            }
        }

        response = self.client.post(self.create_url , data, format='json')

        # And that we're returning a 201 created code.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('key', response.data)
        # We want to make sure we have two users in the database..
        self.assertEqual(User.objects.count(), 2)

    def test_create_user_serializer_error_pass(self):

        data = {
            'username': 'mara',
            'email': 'mara@example.com',
            'password': 'not6',
            'is_active': False,
            'org': {
                'name': 'Test organizacija',
                'location': 'Novi Sad'
            }
        }

        response = self.client.post(self.create_url , data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], 'Ensure this field has at least 8 characters.')

    def test_create_user_serializer_error_exist_username(self):

        data = {
            'username': 'testuser',
            'email': 'mara@example.com',
            'password': 'marapassword',
            'is_active': False,
            'org': {
                'name': 'Test organizacija',
                'location': 'Novi Sad'
            }
        }

        response = self.client.post(self.create_url , data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['username'][0], 'This field must be unique.')

    def test_activate_user(self):
        data = {
            'username': 'test',
            'email': 'test1@example.com',
            'password': 'testpassword',
            'is_active': False,
            'org': {
                'name': 'Test organizacija',
                'location': 'Novi Sad'
            }
        }

        response = self.client.post(self.create_url , data, format='json')

        response = self.client.put(reverse('activation', kwargs={'code': response.data['key']}), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, 'Account has been successfully activate')

    def test_error_user_is_active(self):
        data = {
            'username': 'username',
            'email': 'email@example.com',
            'password': 'testpassword',
            'is_active': True,
            'org': {
                'name': 'Test organizacija',
                'location': 'Novi Sad'
            }
        }

        response = self.client.post(self.create_url , data, format='json')

        response = self.client.put(reverse('activation', kwargs={'code': response.data['key']}), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, 'Account has already been activated')

    def test_activation_key_expired_or_invalid(self):
        key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJrZXkiOiJ1c2VybmFtZSIsImV4cCI6MTU0NDk1ODkyMn0.hPHu2iinMMZtqXDuA1lRaimrAbY3"
        response = self.client.put(reverse('activation', kwargs={'code': key}), format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, 'Activation key invalid or expired')

    def test_get_user(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)

        response = self.client.get(self.create_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.test_user.username)
        self.assertEqual(response.data['email'], self.test_user.email)

    def test_get_user_unauthorized(self):

        response = self.client.get(self.create_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_data(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)
        data = {
            'first_name': 'test',
            'last_name': 'testtest'
        }
        response = self.client.put(self.create_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], data['first_name'])
        self.assertEqual(response.data['last_name'], data['last_name'])


    def test_change_password(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)

        data = {
            'current_password': 'testpassword',
            'new_password': 'newpassword',
            'repeated_password': 'newpassword'
        }

        response = self.client.put(reverse('change_password'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, "Password changed succesfully")

    def test_change_password_not_match(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)

        data = {
            'current_password': 'testpassword',
            'new_password': 'newpassword',
            'repeated_password': 'notmatchpassword'
        }

        response = self.client.put(reverse('change_password'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], "Passwords doesn't match!")

    def test_deactivate_user(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)

        data = {
            'username': 'deactive',
            'email': 'deactive@example.com',
            'password': 'testpassword',
            'is_active': True,
            'org': {
                'name': 'Test organizacija',
                'location': 'Novi Sad'
            }
        }

        self.client.post(self.create_url , data, format='json')
        user = User.objects.get(username='deactive')

        response = self.client.put(reverse('user_deactivation', kwargs={'id': user.id}), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertFalse(user.is_active)
        self.assertEqual(response.data, 'User is deactivated')

    def test_user_alredy_deactivate(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)

        data = {
            'username': 'deactive',
            'email': 'deactive@example.com',
            'password': 'testpassword',
            'is_active': True,
            'org': {
                'name': 'Test organizacija',
                'location': 'Novi Sad'
            }
        }

        self.client.post(self.create_url , data, format='json')
        user = User.objects.get(username='deactive')

        self.client.put(reverse('user_deactivation', kwargs={'id': user.id}), format='json')
        user.refresh_from_db()
        self.assertFalse(user.is_active)
        response = self.client.put(reverse('user_deactivation', kwargs={'id': user.id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TokenTests(APITestCase):
    def setUp(self):
        User.objects.create_user(username="testtest", password="testpassword")
        self.client = APIClient()

    def test_create_token(self):
        User.objects.get(username="testtest")

        response = self.client.post(reverse('login'),
                                    {'username': 'testtest', 'password': 'testpassword'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_bad_token(self):
        User.objects.get(username="testtest")

        response = self.client.post(reverse('login'),
                                    {'username': 'notest', 'password': 'testpassword'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], 'Unable to log in with provided credentials.')


class UpdateProfileTests(APITestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(username="testuser", email='test@example.com', password="testpassword")
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'})
        self.token = response.data['token']

    def test_update_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)

        profile = {
            "location": "Novi Sad",
            "state": "Serbia",
            "birth_date": "10/20/2018",
            "email": self.test_user.email,
            "first_name": "Test Test",
            "last_name": "Test"
        }

        user_profile = self.test_user.profile
        response = self.client.put(reverse('profile'), profile, format='json')
        self.test_user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['location'], profile['location'])
        self.assertEqual(response.data['state'], profile['state'])
        self.assertEqual(response.data['birth_date'], profile['birth_date'])

        get_profile = Profile.objects.get(id=user_profile.id)
        self.assertEqual(user_profile, get_profile)

    def test_get_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)

        profile = {
            "location": "Novi Sad",
            "state": "Serbia",
            "birth_date": "10/20/2018",
            "email": self.test_user.email,
            "first_name": self.test_user.first_name,
            "last_name": self.test_user.last_name
        }

        response = self.client.put(reverse('profile'), profile, format='json')
        self.test_user.refresh_from_db()

        response = self.client.get(reverse('profile'), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('email', response.data)
        self.assertEqual(response.data['location'], profile['location'])
