import logging
import schedule
import os

from .parser import Parser

logger = logging.getLogger("sched")

sched_time = os.getenv("SCHEDULE_TIME_FIRE")
sched_del_days = os.getenv("SCHEDULE_DELETE_DAYS_FIRE")


def job():
    Parser().proccess()


# def delete_job():
#     Parser().remove_deprecated_files()


def sched():
    schedule.every(int(sched_time)).minutes.do(job)
    # schedule.every(int(sched_del_days)).days.do(delete_job)

    while True:
        schedule.run_pending()
