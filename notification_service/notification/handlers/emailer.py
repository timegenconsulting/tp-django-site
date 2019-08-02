"""
Contains smtp server configurations
"""
import logging
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger("notify")


class Emailer(object):
    """
    Creates connection and mail message body.

    """
    def run_server(self, host, port, username, password):
        """
        This function manages connection to SMTP or ESMTP server.

        Args:
            - host: host name
            - port: host port
            - username: username on the host server
            - password: password on the host server
        """
        try:
            server = smtplib.SMTP(host, port)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(username, password)
            return server
        except (smtplib.SMTPException) as e:
            logger.error('Could not establish SMTP connection: {}'.format(e))
            raise e

    def create_msg(self, subject, body, to, sender):
        """
        Creates e-mail message

        Args:
            - subject: mail's subject
            - body: mail's message body
            - to: recipients
            - sender: the one who sends the mail
        """
        # bcc STRING of all recipeints
        bcc = to

        message = MIMEMultipart('alternative')
        message['subject'] = subject
        message['to'] = ""  # we'll send all messages as bcc
        message['from'] = sender

        to = [to]
        # add all recipients to bcc LIST
        if type(bcc) in [str]:
            bcc = [bcc]
            to += bcc
        html_body = MIMEText(body, "plain", "utf-8")

        message.attach(html_body)

        logger.debug('Created email message: {}'.format(message))
        return message
