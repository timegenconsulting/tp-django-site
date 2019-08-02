import os

from .rabbit import Consumer


class Receiver(Consumer):
    """Notification Service receiver."""
    EXCHANGE = str(os.getenv("NOTIFY_EXCHANGE"))
    EXCHANGE_TYPE = 'direct'
    QUEUE = str(os.getenv("NOTIFY_QUEUE"))
    ROUTING_KEY = ''
