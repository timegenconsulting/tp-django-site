from unittest import TestCase
import requests
import datetime
import mock
from earthdata import logger  # noqa: F401
from earthdata import models
from earthdata.parser import Parser
from earthdata.notifications import Notifier


class ParserTestCase(TestCase):

    data = [
        {
          'soilMoistureNPD': 0.08258207,
          'longitude': 108.54375,
          'latitude': 48.114197,
          'time': 8.24878588e+08,
          'soilMoistureSCA': 0.01,
        }, {
          'soilMoistureNPD': 0.09952749,
          'longitude': 108.60752,
          'latitude': 47.85247,
          'time': 8.24878587e+08,
          'soilMoistureSCA': 0.01,
        }, {
          'soilMoistureNPD': 0.09847949,
          'longitude': 108.804794,
          'latitude': 48.121258,
          'time': 8.2487858e+08,
          'soilMoistureSCA': 0.01,
        }, {
          'soilMoistureNPD': 0.10823301,
          'longitude': 108.81134,
          'latitude': 47.820957,
          'time': 8.24878581e+08,
          'soilMoistureSCA': 0.01,
        }, {
          'soilMoistureNPD': 0.10992623,
          'longitude': 108.83308,
          'latitude': 47.545864,
          'time': 8.24878581e+08,
          'soilMoistureSCA': 0.01,
        }, {
          'soilMoistureNPD': 0.09699237,
          'longitude': 109.067024,
          'latitude': 47.817043,
          'time': 8.24878573e+08,
          'soilMoistureSCA': 0.01,
        }, {
          'soilMoistureNPD': 0.1085883,
          'longitude': 109.13873,
          'latitude': 47.003033,
          'time': 8.24878572e+08,
          'soilMoistureSCA': 0.01048119,
        }, {
          'soilMoistureNPD': 0.09814976,
          'longitude': 109.32418,
          'latitude': 45.257527,
          'time': 8.24878567e+08,
          'soilMoistureSCA': 0.01,
        }, {
          'soilMoistureNPD': 0.78668,
          'longitude': 19.8122,
          'latitude': 45.257527,
          'time': 8.24878572e+08,
          'soilMoistureSCA': 0.01048119,
        }]

    def setUp(self):
        super(ParserTestCase, self).setUp()
        self.session = models.Session()

    def tearDown(self):
        super(ParserTestCase, self).tearDown()
        models.mongo_connection.drop_database('earthtestdb')
        self.session.query(models.EventHook).delete()
        self.session.query(models.Events).delete()
        self.session.query(models.EventService).delete()
        self.session.query(models.Organization).delete()
        self.session.commit()
        self.session.close()

    def test_insert_data(self):
        Parser().insert_amsr_data(self.data)
        location = models.Locations.objects.filter(location__near=[float(self.data[0]['longitude']), float(self.data[0]['latitude'])], location__max_distance=0)
        self.assertEqual(location[0]['moisture_data'][0]['moisture_NPD'], self.data[0]['soilMoistureNPD'])
        self.assertEqual(len(location[0]['moisture_data']), 1)

    def test_send_notification(self):
        self.eventservice = models.EventService(
            name="MoistureService",
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
              "radius": 178942.17121708542,
              "maxMoisture": 0,
              "minMoisture": -1,
              "longitude": 108.54375,
              "latitude": 48.114197
            }
        )
        self.session.add(self.organization)
        self.session.add(self.eventservice)
        self.session.add(self.event)
        self.session.add(self.eventhook)
        self.session.commit()

        Parser().insert_amsr_data(self.data)
        Parser().send_moisture_data_to_subscribers()
        location = models.Locations.objects.filter(location__near=[float(self.data[0]['longitude']), float(self.data[0]['latitude'])], location__max_distance=0)
        self.assertEqual(location[0]['moisture_data'][0]['moisture_NPD'], self.data[0]['soilMoistureNPD'])
        self.assertEqual(len(location[0]['moisture_data']), 1)
        self.assertTrue(False)

    def test_update_data(self):
        self.data.extend(self.data)
        Parser().insert_amsr_data(self.data)

        time = datetime.datetime.now().strftime('%Y%m%d %H:%M')
        location = models.Locations.objects.filter(location__near=[float(self.data[-1]['longitude']), float(self.data[-1]['latitude'])], location__max_distance=0)
        self.assertEqual(location[0]['moisture_data'][-1]['moisture_NPD'], self.data[-1]['soilMoistureNPD'])
        self.assertEqual(len(location[0]['moisture_data']), 2)
        self.assertEqual(location[0]['time'].strftime('%Y%m%d %H:%M'), time)

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
                    "moisture_data": {
                        "time": datetime.datetime.now(),
                        "moisture_NPD": 2.00,
                        "moisture_SCA": 25.00,
                    },
                    "alert_type": "MAX moisture",
                    "alert_value": "1.25"
                }
            ]
        }

        result = notify.send(data)

        self.assertTrue(result)
