import json

from datetime import datetime, timedelta

from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework import status

from terraPorta.apps.orgs.models import Organization
from terraPorta.apps.events.models import Events


class EventsTest(APITestCase):
    def setUp(self):
        self.test_user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        self.test_user.is_staff = True
        self.test_user.save()
        expire_date = datetime.now()+timedelta(days=2)
        kwargs = {'name': 'Test Organization', 'location': 'test location', 'state': 'State', 'owner': self.test_user, 'active': True, 'billing_date': expire_date}
        self.test_org = Organization.objects.create(**kwargs)
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'})
        self.token = response.data['token']

        self.url = reverse('events')

    def test_create_event(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.token)

        data = {
            'event': 'event',
            'body': json.dumps({'something': 'something bla bla bla'})
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.test_user.pk, response.data['owner'])
        self.assertEqual(response.data['event'], data['event'])

    def test_create_event_missing_param(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.token)

        data = {
            'event': '',
            'body': json.dumps({'something': 'something bla bla bla'})
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['event'][0], 'This field may not be blank.')

    def test_get_events(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.token)
        kwargs = {'event': 'test event', 'body': json.dumps({'event data': 'event data data'}), 'owner': self.test_user}
        Events.objects.create(**kwargs)

        response = self.client.get(self.url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)

    def test_user_is_not_owner(self):
        User.objects.create_user('owner', 'owner@example.com', 'testpassword')
        response = self.client.post(reverse('login'), {'username': 'owner', 'password': 'testpassword'})
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + response.data['token'])

        data = {
            'event': 'event',
            'body': json.dumps({'something': 'something bla bla bla'})
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, 'Is not staff or superuser')


class EventTest(APITestCase):
    def setUp(self):
        self.test_user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        self.test_user.is_superuser = True
        self.test_user.save()
        kwargs = {'name': 'Test Organization', 'location': 'test location', 'state': 'State', 'owner': self.test_user}
        self.test_org = Organization.objects.create(**kwargs)
        kwargs = {'event': 'test event', 'body': json.dumps({'event data': 'event data data'}), 'owner': self.test_user}
        self.create_event = Events.objects.create(**kwargs)
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'})
        self.token = response.data['token']

    def test_get_event(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.token)

        response = self.client.get(reverse('update_delete', kwargs={'id': self.create_event.id}), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['event']['event'], self.create_event.event)
        self.assertEqual(response.data['event']['owner'], self.test_user.id)

    def test_update_event(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.token)
        data = {
            "event": self.create_event.event,
            "body": json.dumps({'event data': 'updated event data'})
        }

        response = self.client.put(reverse('update_delete', kwargs={'id': self.create_event.id}), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['owner'], self.test_user.id)
        self.assertEqual(response.data['body'], data['body'])

    def test_delete_event(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.token)
        kwargs = {'event': 'event test', 'body': json.dumps({'hook': 'event data hook'}), 'owner': self.test_user}
        event = Events.objects.create(**kwargs)

        response = self.client.delete(reverse('update_delete', kwargs={'id': event.id}), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, 'Event has been deleted')



