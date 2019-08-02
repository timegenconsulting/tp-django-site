"""
Contains smtp server configurations
"""
import logging
import os
from earthdata.rabbit import Publisher

logger = logging.getLogger("notifications")


class Notifier(object):
    def __init__(self, url=None):
        if url:
            self.url = url
        else:
            self.url = os.getenv("RABBITURL")
        self.destination = os.getenv("NOTIFY_EXCHANGE")

    def send(self, data):
        try:
            logger.info("Data received in notify {}".format(data))
            alert_data = {
                "service": "moistureservice",
                "subject": "Soil moisture Alert!",
                "alert_type": "moisturealert",
                "type": data['subscriber'].hook_type,
                "value": data['subscriber'].hook_link,
                "locations": [
                    {
                        "latitude": x['location']['coordinates'][0],
                        "longitude": x['location']['coordinates'][1],
                        "time": x['moisture_data']['time'].strftime("%m/%d/%Y %H:%M %Z"),
                        "moisture_NPD": x['moisture_data']['moisture_NPD'],
                        "moisture_SCA": x['moisture_data']['moisture_SCA'],
                        "alert_type": x['alert_type'],
                        "alert_value": x['alert_value']
                    } for x in data['locations']
                ]
            }
            logger.info("Alert data {} destination {}".format(alert_data, self.destination))
            publisher = Publisher(self.url)
            publisher.publish_message(alert_data, self.destination)
        except Exception as e:
            logger.error("Error sending notification. Exception {}".format(str(e)))
        return False
