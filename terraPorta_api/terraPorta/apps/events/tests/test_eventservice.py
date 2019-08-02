import json

from datetime import datetime, timedelta

from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework import status

from terraPorta.apps.orgs.models import Organization
from terraPorta.apps.events.models import Events, EventService


class EventServiceTest(APITestCase):
    def setUp(self):
        self.test_user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        self.test_user.is_staff = True
        self.test_user.save()
        expire_date = datetime.now()+timedelta(days=2)
        kwargs = {'name': 'Test Organization', 'location': 'test location', 'state': 'State', 'owner': self.test_user, 'active': True, 'billing_date': expire_date}
        self.test_org = Organization.objects.create(**kwargs)
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'})
        self.token = response.data['token']
        self.eventService = EventService.objects.create(
            name="ServiceEvent1",
            description="Some description"
        )
        self.eventService = EventService.objects.create(
            name="ServiceEvent2",
            description="Some description"
        )

        self.url = reverse('eventservices')

    def test_get_event_services(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.token)

        response = self.client.get(self.url, format='json')
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
