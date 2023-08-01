from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
)
import requests

from social.models import Student, NotificationToken

# Optionally providing an access token within a session if you have enabled push security
session = requests.Session()
session.headers.update(
    {
        "Authorization": "Bearer iiBDmsbzZGGi19zWgLy9uhrBfCiSPVsl5ah5H0jZ",
        "accept": "application/json",
        "accept-encoding": "gzip, deflate",
        "content-type": "application/json",
    }
)


def send_push_message_to_all_students(title, message, extra=None):
    students = Student.objects.all()
    for student in students:
        send_push_message_to_student(student, title, message, extra)


def send_push_message_to_student(student, title, message, extra=None):
    tokens = NotificationToken.objects.filter(student=student)
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
