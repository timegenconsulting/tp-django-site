from sqlalchemy import create_engine, Column, Integer, String, JSON, ForeignKey, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os


import logging

logger = logging.getLogger('parser')

# Postgres connection data
Base = declarative_base()
adr = os.getenv("POSTGRES_ADDR", "127.0.0.1")
port = os.getenv("POSTGRES_PORT", "5432")
user = os.getenv("POSTGRES_USER", "terraporta")
password = os.getenv("POSTGRES_PASSWORD", "terraPorta")
name = os.getenv("POSTGRES_DB", "terraporta_db")
postgres_db_url = "postgresql://{}:{}@{}:{}/{}".format(user, password, adr, port, name)


def recreate_test_db():
    # try:
    pg_engine = create_engine("postgresql://{}:{}@{}:{}/{}".format(user, password, adr, port, name), echo=True)  # connect to server
    pg_engine.execution_options(isolation_level="AUTOCOMMIT").execute("DROP DATABASE IF EXISTS pg_test;")  # create db
    pg_engine.execution_options(isolation_level="AUTOCOMMIT").execute("CREATE DATABASE pg_test;")  # create db
    # except Exception as e:
    #     logger.error("Failed to delete and recreate test db with error: {}".format(str(e)))


try:
    if os.getenv("TEST_DB", None):
        # create new postgres test db
        recreate_test_db()
        postgres_db_url = "postgresql://{}:{}@{}:{}/{}".format(user, password, adr, port, 'pg_test')

        logger.info('Creating test db')
except Exception as e:
    logger.info(str(e))
    pass

logger.info("Database postgres connection url {}".format(postgres_db_url))


class EventService(Base):
    __tablename__ = "event_eventservice"

    name = Column(String(500), primary_key=True)

    def __repr__(self):
        return "< EventService {} >".format(self.name)


class Events(Base):
    __tablename__ = "events_events"

    id = Column(Integer, primary_key=True)
    event = Column(String(500))
    service_id = Column(String(500), ForeignKey('event_eventservice.name'))
    service = relationship(EventService, backref='events')

    def __repr__(self):
        return "< Events {}:{}:{} >".format(self.id, self.event, self.service)


class Organization(Base):
    __tablename__ = "orgs_organization"

    id = Column(Integer, primary_key=True)
    active = Column(Boolean)
    billing_date = Column(DateTime)
    name = Column(String(50), unique=True)

    def __repr__(self):
        return "<Organization {}:{}>".format(self.id, self.name)


class EventHook(Base):
    __tablename__ = "events_eventhook"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey(Events.id))
    event = relationship(Events, backref='hooks')
    org_id = Column(Integer, ForeignKey('orgs_organization.id'))
    org = relationship(Organization, backref='event_hooks')
    hook_link = Column(String(500))
    hook_type = Column(String(6))
    body = Column(JSON)

    def __repr__(self):
        return "< EventHook {}:{}:{} >".format(self.id, self.event, self.org)


engine = create_engine(postgres_db_url, echo=True)
Session = sessionmaker()
Session.configure(bind=engine)
Base.metadata.create_all(engine)
