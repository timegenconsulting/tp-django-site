import sys
import signal
import earthdata.logger  # noqa: F401

# from rabbit.consumer import Consumer
# from observer import Observer

from earthdata.scheduler import sched

consum = None


def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    consum.stop()
    sys.exit(0)


def main():

    sched()

    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C')
    signal.pause()

    sys.exit(0)


if __name__ == '__main__':
    main()
