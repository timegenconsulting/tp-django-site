import logging
import json
from .handlers import CoreHandler
logger = logging.getLogger("notify")


class NotifyHandler():

    def handle(self, body):
        try:
            notification_data = json.loads(body)
            result = CoreHandler.send_data(notification_data)

            return result
        except Exception as e:
            logger.error("Exception happended in notify handler. Exception {}".format(str(e)))

        return False
