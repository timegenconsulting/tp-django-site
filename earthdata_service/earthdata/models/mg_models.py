import mongoengine
import os
import datetime


import logging

logger = logging.getLogger('models.mg_models')

adr = os.getenv("MONGO_ADDR")
port = os.getenv("MONGO_PORT", 27017)
user = os.getenv("MONGO_USER")
password = os.getenv("MONGO_PASSWORD")


# Mongo connection data
mongo_db_url = "mongodb://{}:{}/".format(adr, port)

mongo_connection = None


try:
    if os.getenv("TEST_DB", None):
        mongo_connection = mongoengine.connect(host=mongo_db_url, db='earthtestdb')
    else:
        mongo_connection = mongoengine.connect(db=os.getenv("MONGO_DB_MOISTURE", 'earthdata'), host=mongo_db_url)
except Exception as e:
    logger.info(str(e))
    pass

logger.info("Database mongo connection url {}".format(mongo_db_url))


class SoilMoisture(mongoengine.Document):
    moisture_NPD = mongoengine.FloatField()
    moisture_SCA = mongoengine.FloatField()
    time = mongoengine.DateTimeField(default=datetime.datetime.now)

    def __unicode__(self):
        return "{} {} {}".format(self.moisture_NPD, self.moisture_SCA, self.time)


class Locations(mongoengine.Document):
    location = mongoengine.PointField()
    moisture_data = mongoengine.ListField(mongoengine.ReferenceField(SoilMoisture, required=True))
    time = mongoengine.DateTimeField(default=datetime.datetime.now)

    def __unicode__(self):
        return "{} {} {}".format(self.location, self.moisture_data, self.time)
