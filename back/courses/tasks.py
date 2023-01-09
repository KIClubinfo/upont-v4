import datetime

from celery.schedules import crontab
from django.utils import timezone
from upont.celery import app

from .models import Timeslot
from .scrapper import get_schedule


@app.task
def update_timeslots():
    """
    Daily run tasks to update courses timeslots with informations from
    emploidutemps.enpc.fr
    """
    today = timezone.now().date()

    Timeslot.objects.filter(start__lte=today - datetime.timedelta(60))

    for i in range(200):
        get_schedule(today + datetime.timedelta(days=i))


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls update_timeslots every day at midnight
    sender.add_periodic_task(
        crontab(minute=0, hour=0), update_timeslots.s(), name="Update courses timeslots"
    )
