import abc
import logging

logger = logging.getLogger('handler')


class CoreHandler(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def name():
        raise Exception("This method must be overridden!!!")

    @abc.abstractmethod
    def send(data):
        raise Exception("This method must be overridden!!!")

    @classmethod
    def send_data(cls, data):
        handler = [hend for hend in CoreHandler.__subclasses__() if hend.name() == data.get('type', "")]
        logger.info("Hander found {}".format(handler))
        if handler:
            result = handler[0]().send(data)
            return result
        return False
