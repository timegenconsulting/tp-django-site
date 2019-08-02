from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework import status


class BillingTest(APITestCase):
    def setUp(self):
        self.test_user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'})
        self.token = response.data['token']

    def test_billing(self):
        pass
        # self.client.credentials(HTTP_AUTHORIZATION="JWT " + self.token)

        # data = {
        #     'user': self.test_user.username,
        #     'amount': 100
        # }

        # response = self.client.post(reverse('charge'), data, format='json')
        # print(response.data)
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
