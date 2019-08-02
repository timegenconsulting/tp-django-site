"""
Contains smtp server configurations
"""
import logging
import os
from fireservice.rabbit import Publisher

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
                "service": "firealert",
                "subject": "Fire Alert",
                "alert_type": "firealert",
                "type": data['subscriber'].hook_type,
                "value": data['subscriber'].hook_link,
                "locations": [
                    {
                        "latitude": x['location']['coordinates'][0],
                        "longitude": x['location']['coordinates'][1],
                        "time": x['time'].strftime("%m/%d/%Y %H:%M %Z")
                    } for x in data['locations']]
            }
            logger.info("Alert data {}".format(alert_data))
            publisher = Publisher(self.url)
            publisher.publish_message(alert_data, self.destination)
        except Exception as e:
            logger.error("Error sending notification. Exception {}".format(str(e)))
        return False
