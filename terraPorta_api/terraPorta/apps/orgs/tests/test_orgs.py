from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework import status

from terraPorta.apps.orgs.models import Organization


class CreateOrgsTest(APITestCase):
    def setUp(self):
        self.test_user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        kwargs = {'name': 'Test Organization', 'location': 'test location', 'state': 'State'}
        self.test_org = Organization.objects.create(**kwargs)
        self.test_org.members.add(self.test_user)
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'})
        self.token = response.data['token']

        self.create_url = reverse('orgs')


    def test_create_org(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)

        data = {
            'name': 'Terra Organization',
            'location': 'Novi Sad',
            'state': 'Srbija',
        }

        response = self.client.post(self.create_url , data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_organizations_for_user(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)
        response = self.client.get(reverse('list_orgs'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)


class UpdateOrgTest(APITestCase):
    def setUp(self):
        self.test_user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        kwargs = {'name': 'Test Organization', 'location': 'test location', 'state': 'State', 'owner': self.test_user}
        self.test_org = Organization.objects.create(**kwargs)
        self.test_org.members.add(self.test_user)
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'})
        self.token = response.data['token']

    def test_update_org(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)

        data = {
            'location': 'Novi Sad',
            'state': 'Srbija',
        }

        response = self.client.put(reverse('get_update_delete_org', kwargs={'id': self.test_org.id}), data, format='json')
        self.test_org.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['location'], data['location'])
        self.assertEqual(response.data['members'][0], self.test_user.id)

        get_org_data = Organization.objects.get(id=self.test_org.id)
        self.assertEqual(self.test_org, get_org_data)

    def test_update_org_404(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)

        data = {
            'location': 'Novi Sad',
            'state': 'Srbija',
        }

        response = self.client.put(reverse('get_update_delete_org', kwargs={'id': 100}), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Not found.')

    def test_get_org(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)

        response = self.client.get(reverse('get_update_delete_org', kwargs={'id': self.test_org.id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_org(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)
        response = self.client.delete(reverse('get_update_delete_org', kwargs={'id': self.test_org.id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

