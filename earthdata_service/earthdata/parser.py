import logging
import os
import datetime
import time
import requests

from netCDF4 import Dataset
from bs4 import BeautifulSoup

from earthdata.models import Session, Locations, SoilMoisture, EventHook, Events
from earthdata.notifications import Notifier

logger = logging.getLogger("parser")


class Parser(object):
    eventservice_id = os.getenv('MOISTURE_EVENT_ID')

    notification_sender = Notifier()
    session = Session()

    AMSR_URL = os.getenv('AMSR_URL', 'https://lance.itsc.uah.edu/amsr2-science/data/level2/land/R02/nc/')
    AMSR_USER = os.getenv('AMSR_USER', 'swahle')
    AMSR_PASS = os.getenv('AMSR_PASSWORD', 'TerraPorta1!')

    def get_data(self):
        try:
            s = requests.Session()

            r = s.get(self.AMSR_URL, auth=(self.AMSR_USER, self.AMSR_PASS))
            s.get(r.url, auth=(self.AMSR_USER, self.AMSR_PASS))

            # check currant day and day before
            date_list = [(datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d'), datetime.datetime.now().strftime('%Y%m%d')]
            for date in date_list:
                path = os.getcwd()
                folder_path = '{}/AMSR/'.format(path)
                if not os.path.isdir('{}{}'.format(folder_path, date)):
                    os.mkdir('{}{}'.format(folder_path, date))

                data_url = "{}{}/".format(self.AMSR_URL, date)
                logger.info("response status {}".format(data_url))
                r = s.get(data_url)
                response = r.text.split('Parent Directory</a>', 1)

                soup = BeautifulSoup(response[1], 'html.parser')
                for check in soup.find_all('a'):
                    file_url = check.get('href')
                    file_path = '{}{}/{}'.format(folder_path, date, file_url)
                    if not os.path.isfile(file_path):
                        url = '{}{}'.format(data_url, file_url)
                        response = s.get(url)
                        open(file_path, 'wb').write(response.content)

                        dataset = Dataset(file_path)

                        logger.info('Dataset response: {}'.format(dataset))
                        parsed_data = []
                        for x in range(dataset.dimensions['Points'].size):
                            if dataset.variables['SoilMoistureNPD'][x] != '--' or dataset.variables['SoilMoistureSCA'][x] != '--':

                                parsed_data.append({
                                    'time': dataset.variables['Time'][x],
                                    'latitude': dataset.variables['Latitude'][x],
                                    'longitude': dataset.variables['Longitude'][x],
                                    'soilMoistureNPD': dataset.variables['SoilMoistureNPD'][x],
                                    'soilMoistureSCA': dataset.variables['SoilMoistureSCA'][x]
                                })
                        self.insert_amsr_data(parsed_data)
            self.send_moisture_data_to_subscribers()
        except Exception as e:
            logger.error('Parser error: {}'.format(str(e)))

    def remove_deprecated_files(self):
        try:
            path = os.getcwd()
            DIR = '{}/AMSR/'.format(path)
            path, dirs, files = next(os.walk(DIR))

            now = time.time()
            old = now - 5 * 24 * 60 * 60

            for d in dirs:
                if os.path.isdir('{}{}'.format(DIR, d)):
                    stat = os.stat('{}{}'.format(DIR, d))
                    if stat.st_ctime < old:
                        path, dirs, files = next(os.walk('{}{}'.format(DIR, d)))
                        for f in files:
                            print("removing: ", f, d)
                            os.remove('{}{}/{}'.format(DIR, d, f))
                        os.rmdir('{}{}'.format(DIR, d))
        except Exception as e:
            logger.error('Delete error: {}'.format(str(e)))

    def insert_amsr_data(self, parsed_data):
        try:
            for data in parsed_data:
                time = datetime.datetime.fromtimestamp(data['time'])
                # check if location alredy exists
                locations = Locations.objects.filter(
                    location__near=[float(data['longitude']), float(data['latitude'])],
                    location__max_distance=0
                )
                if locations:
                    locations[0].update(
                        push__moisture_data=SoilMoisture(
                            moisture_NPD=data['soilMoistureNPD'],
                            moisture_SCA=data['soilMoistureSCA'],
                            time=time
                        ).save()
                    )
                    locations[0].update(time=datetime.datetime.now())
                else:
                    # insert new location with moisture data
                    moisture_data = SoilMoisture(
                        moisture_NPD=data['soilMoistureNPD'],
                        moisture_SCA=data['soilMoistureSCA'],
                        time=time).save()
                    loc = [float(data['longitude']), float(data['latitude'])]
                    Locations(
                        location=loc,
                        moisture_data=[moisture_data]
                        ).save()
            logger.info('Data is saved')
        except Exception as e:
            logger.error("Database error exception {}".format(e))
            return False

    def send_moisture_data_to_subscribers(self):
        try:
            time_diff = datetime.datetime.now() - datetime.timedelta(minutes=int(os.getenv("SCHEDULE_TIME_MOISTURE", 15))+1)
            event_subscribers = self.session.query(EventHook).join(Events).filter(Events.service_id == self.eventservice_id).all()
            for subscriber in event_subscribers:
                if subscriber.org.active and subscriber.org.billing_date > datetime.datetime.now(datetime.timezone.utc):
                    locations = Locations.objects.filter(
                        location__near=[
                            float(subscriber.body['longitude']),
                            float(subscriber.body['latitude'])
                        ],
                        location__max_distance=subscriber.body['radius'],
                        time__gte=time_diff
                    )

                    if locations:
                        data = {
                            "subscriber": subscriber,
                            "locations": [],
                        }

                        for loc in locations:
                            moisture_data = loc['moisture_data'][-1]
                            location = loc.to_mongo()
                            location['moisture_data'] = moisture_data.to_mongo()
                            if subscriber.body['maxMoisture'] < moisture_data['moisture_NPD']:
                                location['alert_type'] = 'maxMoisture'
                                location['alert_value'] = subscriber.body['maxMoisture']
                            elif subscriber.body['minMoisture'] > moisture_data['moisture_NPD']:
                                location['alert_type'] = 'maxMoisture'
                                location['alert_value'] = subscriber.body['minMoisture']
                            data['locations'].append(location)

                        self.notification_sender.send(data)

        except Exception as e:
            logger.error("Database error exception {}".format(e))
            return False
