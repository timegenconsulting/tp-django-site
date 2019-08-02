import os
import json
import logging
import pika
import uuid


logger = logging.getLogger("rabbit.publisher")


class Publisher(object):
    """Publisher"""

    EXCHANGE_TYPE = 'direct'
    PUBLISH_INTERVAL = 5
    EXCHANGE = os.getenv('NOTIFY_EXCHANGE')

    def __init__(self, amqp_url):

        self._connection = None
        self._channel = None
        self._url = pika.URLParameters(amqp_url)
        self._closing = False

    def connect(self):
        """
        Opens connection to RabbitMQ

        """
        logger.info('Connecting to {}'.format(self._url))
        return pika.BlockingConnection(self._url)

    def close_connection(self):
        """
        Invoke this command to close the connection to RabbitMQ

        """
        logger.info('Closing connection.')
        self._closing = True
        self._connection.close()

    def close_channel(self):
        """
        Invoke this command to close the channel with RabbitMQ

        """
        logger.info('Closing the channel...')
        if self._channel:
            self._channel.close()

    def publish_message(self, data, destination, corr_id=None, rulet=0):
        """
        Invoke this command to publish data to the destination

        Args:
            data: data to be sent
        """
        self.run()
        if not corr_id:
            corr_id = str(uuid.uuid4())

        data['correlationId'] = corr_id

        properties = pika.BasicProperties(
            content_type='application/json',
            correlation_id=corr_id
        )
        self._channel.basic_publish(
            destination,
            '',
            json.dumps(data, ensure_ascii=False),
            properties
        )

        self.close_channel()
        self.close_connection()
        return True

    def run(self):
        """
        Invoke this command to connect, open channel and declare EXCHANGE.

        """
        self._connection = self.connect()  # open connection
        self._channel = self._connection.channel()  # open channel
        self._channel.exchange_declare(self.EXCHANGE, self.EXCHANGE_TYPE)  # declare queue
