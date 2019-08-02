from unittest import TestCase
from notification import logger  # noqa

from notification.notify import NotifyHandler


class NotifyTestCase(TestCase):

    def setUp(self):
        super(NotifyTestCase, self).setUp()

    def tearDown(self):
        super(NotifyTestCase, self).tearDown()

    def test_parser_parse_data_email(self):
        received_data = '''{
            "service": "firealert",
            "type": "email",
            "alert_type": "firealert",
            "value": "mrkic.nebojsa@gmail.com",
            "locations": [
                {
                    "latitude": 11.13,
                    "longitude": 15.04,
                    "time": "02/02/2002 23:50"
                },
                {
                    "latitude": 10.13,
                    "longitude": 14.04,
                    "time": "02/02/2002 20:50"
                }
            ],
            "user": "Some user",
            "correlationId": "ab57bff6-3afe-4cd7-8c56-e427c1cd0663"
        }'''
        response = NotifyHandler().handle(received_data)
        self.assertTrue(response)

    def test_parser_pars_data_url(self):
        received_data = '''{
            "service": "firealert",
            "type": "url",
            "alert_type": "firealert",
            "value": "http://test.com/alert",
            "locations": [
                {
                    "latitude": 11.13,
                    "longitude": 15.04,
                    "time": "02/02/2002 23:50"
                },
                {
                    "latitude": 10.13,
                    "longitude": 14.04,
                    "time": "02/02/2002 20:50"
                }
            ],
            "user": "Some user",
            "correlationId": "ab57bff6-3afe-4cd7-8c56-e427c1cd0663"
        }'''
        response = NotifyHandler().handle(received_data)
        self.assertTrue(response)
