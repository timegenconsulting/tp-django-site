from .core import CoreHandler
from .emailer import Emailer
import logging
import json
import os

logger = logging.getLogger('handler')


class EmailHandler(CoreHandler):

    host = os.getenv('EMAIL_HOST')
    port = os.getenv('EMAIL_PORT')
    host_username = os.getenv('EMAIL_HOST_USER')
    host_pass = os.getenv('EMAIL_PASSWORD')
    host_default = os.getenv('DEFAULT_FROM_EMAIL')
    mail_handler = Emailer()

    @staticmethod
    def name():
        return 'email'

    def send(self, data):
        email_template = self.get_template(data['alert_type'])
        logger.info("Handle email notify")
        server = self.mail_handler.run_server(
            self.host,
            self.port,
            self.host_username,
            self.host_pass
        )

        try:

            subject = email_template['subject']
            data['multi_location'] = "".join([email_template['multi_location'].format(**x) for x in data['locations']])
            template = email_template['template'].format(**data)

            msg = self.mail_handler.create_msg(subject,
                                               template,
                                               [data['value']],
                                               self.host_default)

            server.sendmail(self.host_default, [data['value']], msg.as_string())
            return True
        except Exception as e:
            logger.error("Error on send email {}".format(e))

        return False

    def get_template(self, alert_type):
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(ROOT_DIR, "../../assets/email_templates.json")
        logger.info("Path {}".format(path))
        templates = json.load(open(path))

        logger.info("Templates {}".format(templates))
        return templates[alert_type]
