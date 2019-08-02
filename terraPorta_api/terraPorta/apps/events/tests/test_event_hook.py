import json
from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework import status

from terraPorta.apps.orgs.models import Organization
from terraPorta.apps.events.models import Events


class EventsTest(APITestCase):
    def setUp(self):
        self.test_user = User.objects.create_user('testevent', 'testevent@example.com', 'testpassword')
        self.test_user.is_staff = True
        self.test_user.save()
        kwargs = {'name': 'Test Org', 'location': 'test location', 'state': 'State', 'owner': self.test_user}
        self.test_org = Organization.objects.create(**kwargs)
        event_kwargs = {'event': 'event name', 'body': json.dumps({'something': 'something bla bla bla'}), 'owner': self.test_user}
        self.test_event = Events.objects.create(**event_kwargs)

        response = self.client.post(reverse('login'), {'username': 'testevent', 'password': 'testpassword'})
        self.token = response.data['token']

    def test_create_event_hook(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.token)

        # get list of events
        response = self.client.get(reverse('hooks', kwargs={'event': self.test_event.id}), format='json')
        event_id = response.data[0]['id']
        data = {
            'event': event_id,
            'hook_link': 'http://hooklink.com'
        }
        # create hook for choosen event
        response = self.client.post(reverse('hooks', kwargs={'event': self.test_event.id}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['event'], event_id)
        self.assertEqual(response.data['hook_type'], 'url')

    def test_create_event_error(self):
        User.objects.create_user('not_superuser', 'not_superuser@example.com', 'testpassword')
        response = self.client.post(reverse('login'), {'username': 'not_superuser', 'password': 'testpassword'})
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + response.data['token'])

        data = {
        }
        # create hook for choosen event
        response = self.client.post(reverse('hooks', kwargs={'event': self.test_event.id}), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['hook_link'][0], 'This field is required.')

    def test_list_all_hooks_for_org(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.token)

        data = {
            'org': self.test_org.id,
            'hook_link': 'http://hooklink.com'
        }
        # create hook for choosen event
        self.client.post(reverse('hooks', kwargs={'event': self.test_event.id}), data, format='json')

        response = self.client.get(reverse('list_hooks', kwargs={'org': self.test_org.id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_update_hook(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.token)

        # get list of events
        response = self.client.get(reverse('hooks', kwargs={'event': self.test_event.id}), format='json')
        event_id = response.data[0]['id']
        data = {
            'org': self.test_org.id,
            'hook_link': 'http://hooklink.com'
        }
        # create hook for choosen event
        self.client.post(reverse('hooks', kwargs={'event': self.test_event.id}), data, format='json')

        update_data = {
            'event': event_id,
            'hook_link': 'nekimail@example.com',
            'hook_type': 'email'
        }

        response = self.client.put(reverse('event_hook', kwargs={'org': self.test_org.id, 'event': event_id}), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['event'], update_data['event'])
        self.assertEqual(response.data['hook_type'], 'email')

    def test_delete_hook(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.token)

        # get list of events
        response = self.client.get(reverse('hooks', kwargs={'event': self.test_event.id}), format='json')
        event_id = response.data[0]['id']
        data = {
            'org': self.test_org.id,
            'hook_link': 'http://hooklink.com'
        }
        # create hook for choosen event
        self.client.post(reverse('hooks', kwargs={'event': self.test_event.id}), data, format='json')

        response = self.client.delete(reverse('event_hook', kwargs={'org': self.test_org.id, 'event': event_id}), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, 'Event Hook "event name" has been deleted')
