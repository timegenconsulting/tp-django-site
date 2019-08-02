import mock

from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework import status

from terraPorta.apps.orgs.models import Organization
from terraPorta.apps.orgs.tasks import UserInvitation


class InviteUsersTest(APITestCase):
    def setUp(self):
        self.test_user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        kwargs = {'name': 'Test Organization', 'location': 'test location', 'state': 'State', 'owner': self.test_user}
        self.test_org = Organization.objects.create(**kwargs)
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'})
        self.token = response.data['token']

    def test_get_list_of_existing_users(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)
        User.objects.create_user('novi', 'novi@example.com', 'testpassword')
        response = self.client.get(reverse('invite_users', kwargs={'id': self.test_org.id}), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_invite_new_user(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)
        data = {
            'email': 'newuser@example.com'
        }
        response = self.client.post(reverse('invite_users', kwargs={'id': self.test_org.id}), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, 'Invitation was sent')

    def test_invite_existed_user(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)
        user = User.objects.create_user('novi', 'novi@example.com', 'testpassword')
        data = {
            'email': user.email
        }
        response = self.client.post(reverse('invite_users', kwargs={'id': self.test_org.id}), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, 'Invitation was sent')

    def test_invite_user_missing_email(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)
        data = {
            'email': ''
        }
        response = self.client.post(reverse('invite_users', kwargs={'id': self.test_org.id}), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, 'Missing email')

    def test_invite_error_user_is_not_owner(self):
        User.objects.create_user('owner', 'owner@example.com', 'testpassword')
        response = self.client.post(reverse('login'), {'username': 'owner', 'password': 'testpassword'})
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + response.data['token'])

        data = {
            'email': 'notowner@example.com'
        }
        response = self.client.post(reverse('invite_users', kwargs={'id': self.test_org.id}), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, 'User is not the owner or admin')


class ActivationUserTest(APITestCase):
    def setUp(self):
        self.test_user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        kwargs = {'name': 'terraPorta Organization', 'location': 'Terra', 'state': 'Porta', 'owner': self.test_user}
        self.test_org = Organization.objects.create(**kwargs)
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'})
        self.token = response.data['token']

    @mock.patch.object(UserInvitation, 'run')
    def test_user_invitation_active_new_user(self, invitation):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)

        data = {
            'email': 'newtest@example.com'
        }
        self.client.post(reverse('invite_users', kwargs={'id': self.test_org.id}), data, format='json')

        code = list(invitation.call_args_list[0])[0][1]

        response = self.client.get(reverse('user_activation', kwargs={'code': str(code)}), format='json')

        self.assertFalse(response.data)
        data = {
            'username': 'newtest',
            'email': 'newtest@example.com',
            'password': 'newpassword'
        }
        response = self.client.put(reverse('user_activation', kwargs={'code': str(code)}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, 'The user is registered and added to the organization')

    @mock.patch.object(UserInvitation, 'run')
    def test_user_invitation_active_exist_user(self, invitation):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)

        user = User.objects.create_user('newtest', 'newtest@example.com', 'testpassword')
        data = {
            'email': user.email
        }
        self.client.post(reverse('invite_users', kwargs={'id': self.test_org.id}), data, format='json')

        code = list(invitation.call_args_list[0])[0][1]

        response = self.client.get(reverse('user_activation', kwargs={'code': str(code)}), format='json')

        self.assertTrue(response.data)
        data = {
            'username': '',
            'email': '',
            'password': ''
        }
        response = self.client.put(reverse('user_activation', kwargs={'code': str(code)}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, 'User has been added to the organization.')

    @mock.patch.object(UserInvitation, 'run')
    def test_user_invitation_missing_params(self, invitation):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)

        data = {
            'email': "email@example.com"
        }
        self.client.post(reverse('invite_users', kwargs={'id': self.test_org.id}), data, format='json')

        code = list(invitation.call_args_list[0])[0][1]

        response = self.client.get(reverse('user_activation', kwargs={'code': str(code)}), format='json')
        self.assertFalse(response.data)
        data = {
            'username': '',
            'email': 'email@example.com',
            'password': ''
        }
        response = self.client.put(reverse('user_activation', kwargs={'code': str(code)}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # missing username
        self.assertEqual(response.data['username'][0], 'This field may not be blank.')
        # missing password
        self.assertEqual(response.data['password'][0], 'This field may not be blank.')
