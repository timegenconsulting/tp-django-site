import sys
import signal
import notification.logger  # noqa: F401
import os

# from rabbit.consumer import Consumer
# from observer import Observer

from notification.receiver import Receiver
from notification.notify import NotifyHandler

global consum
consum = None


def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    consum.stop()
    sys.exit(0)


def main():

    consum = Receiver(os.getenv("RABBITURL"))
    consum.deamon = True
    consum.subscribe(NotifyHandler())
    consum.start()

    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C')
    signal.pause()

    sys.exit(0)


if __name__ == '__main__':
    main()
