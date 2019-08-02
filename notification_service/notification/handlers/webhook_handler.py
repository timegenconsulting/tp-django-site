from .core import CoreHandler
import logging
import requests
import json

logger = logging.getLogger('handler')


class WebHookHandler(CoreHandler):

    @staticmethod
    def name():
        return 'url'

    def send(self, data):
        logger.info("Handle webhook notify")
        # logger.info("Webhook data {}".format(data))
        try:
            headers = {'Content-type': 'application/json'}
            response = requests.post(data.pop('value', ''), data=json.dumps(data), headers=headers)
            logger.info("Webhook alert has been sent. Response: {}".format(response))
        except Exception as e:
            logger.error("Web handler request got error. Exception {}".format(str(e)))
        return True
