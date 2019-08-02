import logging
import os
import datetime
import requests
import csv

from fireservice.models import Session, Locations, FireData, EventHook, Events
from fireservice.notifications import Notifier
from io import StringIO

logger = logging.getLogger("parser")


class Parser(object):

    eventservice_id = os.getenv('FIRE_EVENT_ID')

    notification_sender = Notifier()
    session = Session()

    FIRE_URL = os.getenv('FIRE_URL', 'https://firms.modaps.eosdis.nasa.gov/data/active_fire/viirs/csv/VNP14IMGTDL_NRT_Global_24h.csv')
    count = 0
    all_objects = 0
    updated = 0

    def proccess(self):
        try:
            logger.info("Importing data")
            self.get_csv_and_update_db()
            logger.info("Inport complete")
            self.notify_subscribers()
            logger.info("Notification complete written objects {}, updated {}, all objects {}".format(self.count, self.updated, self.all_objects))
            return True
        except Exception as e:
            logger.error('Parser error: {}'.format(str(e)))

        return False

    def get_csv_and_update_db(self):
        try:
            response = requests.get(self.FIRE_URL)
            csv_reader = csv.DictReader(StringIO(response.text))
            for line in csv_reader:
                line['acq_time'] = int(line['acq_time'])
                self.all_objects += 1
                self.insert_fire_data(line)
            return True
        except Exception as e:
            logger.error("Exception has occured in get csv and update db function. Exception: {}".format(str(e)))
            pass
        return False

    def notify_subscribers(self):
        try:
            time_diff = datetime.datetime.now() - datetime.timedelta(minutes=int(os.getenv("SCHEDULE_TIME_FIRE", 15)))
            event_subscribers = self.session.query(EventHook).join(Events).filter(Events.service_id == self.eventservice_id).all()
            for subscriber in event_subscribers:
                if subscriber.org.active and subscriber.org.billing_date > datetime.datetime.now(datetime.timezone.utc):
                    logger.info("Subscriber is ok")
                    location = Locations.objects.filter(
                        location__near=[
                            float(subscriber.body['longitude']),
                            float(subscriber.body['latitude'])
                        ],
                        location__max_distance=subscriber.body['radius'],
                        last_save__gte=time_diff
                    )
                    logger.info("Locations {}".format(location))
                    if location:
                        # location = location[0]
                        data = {
                            "locations": location,
                            "subscriber": subscriber
                        }
                        self.notification_sender.send(data)

        except Exception as e:
            logger.error("Exception has occured in notify subscribers. Exception: {}".format(str(e)))

        return True

    def insert_fire_data(self, fire):
        try:
            record_time = datetime.datetime.strptime("{acq_date} {acq_time:04d}".format(**fire), "%Y-%m-%d %H%M")
            # check if location alredy exists
            location = Locations.objects.filter(
                location__near=[float(fire['longitude']), float(fire['latitude'])],
                location__max_distance=0,

            )
            # check if record was already written
            if len(location.filter(time__lte=record_time)) == 0:
                self.count += 1
                if location:
                    self.updated += 1
                    location = location[0]
                    location.update(
                        push__data=FireData(
                            confidence=fire['confidence'],
                            brightness=float(fire['bright_ti5']),
                            scan=float(fire['scan']),
                            track=float(fire['track']),
                            time=record_time
                        ).save()
                    )
                    location.update(
                        time=record_time,
                        last_save=datetime.datetime.now()
                    )
                else:
                    # insert new location with moisture data
                    fire_data = FireData(
                        confidence=fire['confidence'],
                        brightness=float(fire['bright_ti5']),
                        scan=float(fire['scan']),
                        track=float(fire['track']),
                        time=record_time
                    ).save()
                    loc = [float(fire['longitude']), float(fire['latitude'])]
                    Locations(
                        location=loc,
                        data=[fire_data],
                        time=record_time,
                        last_save=datetime.datetime.now()
                        ).save()
                return True
        except Exception as e:
            logger.error("Database error exception {}".format(e))
        return False
