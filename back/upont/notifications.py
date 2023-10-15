import time

import requests
from celery import shared_task
from exponent_server_sdk import DeviceNotRegisteredError, PushClient, PushMessage
from social.models import NotificationToken, Student

# Optionally providing an access token within a session if you have enabled push security
session = requests.Session()
session.headers.update(
    {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate",
        "content-type": "application/json",
    }
)


def send_push_message_to_all_students(title, message, extra=None):
    students = Student.objects.all()
    send_push_message_to_group(students, title, message, extra)


def send_push_message_to_student(student, title, message, extra=None):
    tokens = NotificationToken.objects.filter(student=student)
    for token in tokens:
        send_push_message(token.token, title, message, extra)


@shared_task
def send_push_message_to_group(students, title, message, extra=None):
    for i in range(len(students)):
        if i > 0 and i % 90 == 0:
            time.sleep(2)
        tokens = NotificationToken.objects.filter(student=students[i])
        for token in tokens:
            send_push_message(token.token, title, message, extra)


# Basic arguments. You should extend this function with the push features you
# want to use, or simply pass in a `PushMessage` object.
def send_push_message(token, title, message, extra=None):
    try:
        PushClient(session=session).publish(
            PushMessage(to=token, title=title, body=message, data=extra)
        )
    except DeviceNotRegisteredError:
        # Mark the push token as inactive
        from social.models import NotificationToken

        NotificationToken.objects.delete(token=token)
