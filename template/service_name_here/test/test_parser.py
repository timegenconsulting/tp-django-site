import datetime
import os
from unittest import TestCase

import mock
import requests

# change "service" to correct service| from server import logger  # noqa

# from service import models
# from service.parser import Parser
# from service.notifications import Notifier

# replace below as necessary
"""
class ParserTestCase(TestCase):

    def setUp(self):
        super(ParserTestCase, self).setUp()
        self.session = models.Session()

    def tearDown(self):
        super(ParserTestCase, self).tearDown()
        models.mongo_connection.drop_database('firetestdb')
        self.session.query(models.EventHook).delete()
        self.session.query(models.Events).delete()
        self.session.query(models.EventService).delete()
        self.session.query(models.Organization).delete()
        self.session.commit()
        self.session.close()
        # models.Base.metadata.session.remove()
        # models.Base.metadata.drop_all(models.engine)

    def load_mock_data(self, number=10):
        with open(os.path.join(
                os.path.dirname(__file__),
                'fixtures/data.csv'
                )) as response_file:
            csv_data = response_file.read()

        return "\n".join(csv_data.split('\n')[:number+1])

    @mock.patch.object(requests, 'get')
    def test_parser_parse_data(self, request_get):
        response_mock = mock.MagicMock()
        response_mock.status_code = 200
        response_mock.text = self.load_mock_data()
        request_get.return_value = response_mock

        procesed = Parser().get_csv_and_update_db()
        self.assertTrue(procesed)
        print(len(models.Locations.objects.all()))
        self.assertTrue(len(models.Locations.objects.all()) == 10)

    @mock.patch.object(requests, 'get')
    def test_parser_parse_duplicate_entery(self, request_get):
        response_mock = mock.MagicMock()
        response_mock.status_code = 200
        response_mock.text = self.load_mock_data()
        request_get.return_value = response_mock

        procesed = Parser().get_csv_and_update_db()
        self.assertTrue(procesed)
        print(len(models.Locations.objects.all()))

        procesed = Parser().get_csv_and_update_db()
        self.assertTrue(procesed)
        print(len(models.Locations.objects.all()))

        self.assertTrue(len(models.Locations.objects.all()) == 10)

    @mock.patch.object(requests, 'get')
    def test_parser_parse_extende_entery(self, request_get):
        response_mock = mock.MagicMock()
        response_mock.status_code = 200
        response_mock.text = self.load_mock_data()
        request_get.return_value = response_mock

        procesed = Parser().get_csv_and_update_db()
        self.assertTrue(procesed)
        print(len(models.Locations.objects.all()))
        response_mock.text = self.load_mock_data(20)

        procesed = Parser().get_csv_and_update_db()
        self.assertTrue(procesed)
        print(len(models.Locations.objects.all()))

        self.assertTrue(len(models.Locations.objects.all()) == 20)

    @mock.patch.object(requests, 'get')
    def test_parser_get_event_service_subscritpions(self, request_get):

        self.eventservice = models.EventService(
            name="FireService",
        )
        self.event = models.Events(
            id=1,
            event='event test',
            service=self.eventservice
        )
        self.organization = models.Organization(
            id=1,
            name='organization',
            active=True,
            billing_date=datetime.datetime.now() + datetime.timedelta(days=10)
        )

        self.eventhook = models.EventHook(
            id=1,
            event=self.event,
            org=self.organization,
            hook_link="mrkic.nebojsa@gmail.com",
            hook_type="email",
            body={
                "radius": 300,
                "latitude": 11.13,
                "longitude": 15.04
            }
        )
        self.session.add(self.organization)
        self.session.add(self.eventservice)
        self.session.add(self.event)
        self.session.add(self.eventhook)
        self.session.commit()
        response_mock = mock.MagicMock()
        response_mock.status_code = 200
        response_mock.text = self.load_mock_data()
        request_get.return_value = response_mock

        procesed = Parser().get_csv_and_update_db()
        self.assertTrue(procesed)

        procesed_event = Parser().notify_subscribers()

        self.assertTrue(procesed_event)

    @mock.patch.object(requests, 'get')
    def test_parser_full_flow(self, request_get):

        self.eventservice = models.EventService(
            name="FireService",
        )
        self.event = models.Events(
            id=1,
            event='event test',
            service=self.eventservice
        )
        self.organization = models.Organization(
            id=1,
            name='organization',
            active=True,
            billing_date=datetime.datetime.now() + datetime.timedelta(days=10)
        )

        self.eventhook = models.EventHook(
            id=1,
            event=self.event,
            org=self.organization,
            hook_link="mrkic.nebojsa@gmail.com",
            hook_type="email",
            body={
                "radius": 300,
                "latitude": 11.13,
                "longitude": 15.04
            }
        )

        self.session.add(self.organization)
        self.session.add(self.eventservice)
        self.session.add(self.event)
        self.session.add(self.eventhook)
        self.session.commit()

        response_mock = mock.MagicMock()
        response_mock.status_code = 200
        response_mock.text = self.load_mock_data()
        request_get.return_value = response_mock

        procesed = Parser().proccess()
        self.assertTrue(procesed)
        self.assertFalse(True)

    def test_notification_send(self):
        notify = Notifier()
        subscriber = mock.MagicMock()
        subscriber.hook_type = "email"
        subscriber.hook_link = "mrkic.nebojsa@gmail.com"

        data = {
            "subscriber": subscriber,
            "locations": [
                {
                    "location": {
                        "coordinates": [11.13, 15.04]
                    },
                    "time": datetime.datetime.now(),
                }
            ]
        }

        """

        result = notify.send(data)

        self.assertTrue(result)
