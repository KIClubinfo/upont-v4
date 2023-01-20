from courses.models import Timeslot
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.dateparse import parse_datetime
from news.models import Event
from rest_framework import views
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from social.models import Student


class CalendarData(views.APIView):
    """
    API endpoint to fetch data for the calendar
    """

    pagination_class = None

    def get(self, request):
        # --------------------------------------------------
        #    Filtering
        # --------------------------------------------------

        # We use Model.object.none() to create empty queryset
        # to reduce the number of condition in the next
        # filtering operations: the filter are the same but
        #  they are costless for empty querysets
        fetch_courses = self.request.GET.get("courses")
        if fetch_courses is not None:
            if fetch_courses == "true":
                courses_queryset = Timeslot.objects.all()
            elif fetch_courses == "false":
                courses_queryset = Timeslot.objects.none()
            else:
                raise ValidationError(
                    detail="Error in parsing courses parameter: must be either 'true' or 'false'"
                )
        else:
            courses_queryset = Timeslot.objects.all()

        fetch_events = self.request.GET.get("events")
        if fetch_events is not None:
            if fetch_events == "true":
                events_queryset = Event.objects.all()
            elif fetch_events == "false":
                events_queryset = Event.objects.none()
            else:
                raise ValidationError(
                    detail="Error in parsing events paramter: must be either 'true' or 'false'"
                )
        else:
            events_queryset = Event.objects.all()

        start = self.request.GET.get("start")
        if start is not None:
            start_datetime = parse_datetime(start)
            if start_datetime is not None:
                events_queryset = events_queryset.filter(
                    Q(date__gte=start_datetime) | Q(end__gte=start_datetime)
                )
                courses_queryset = courses_queryset.filter(
                    Q(start__gte=start_datetime) | Q(end__gte=start_datetime)
                )
            else:
                raise ValidationError(
                    detail="Error in parsing start parameter, the date must be in ISO format"
                )

        end = self.request.GET.get("end")
        if end is not None:
            end_datetime = parse_datetime(end)
            if end_datetime is not None:
                events_queryset = events_queryset.filter(
                    Q(date__lte=end_datetime) | Q(end__lte=end_datetime)
                )
                courses_queryset = courses_queryset.filter(
                    Q(start__lte=end_datetime) | Q(end__lte=end_datetime)
                )
            else:
                raise ValidationError(
                    detail="Error in parsing end parameter, the date must be in ISO format"
                )

        # Must be the last filter applied because no filter is allowed after queryset
        # union of difference
        is_enrolled = self.request.GET.get("is_enrolled")
        if is_enrolled is not None:
            student = get_object_or_404(Student, user__id=self.request.user.id)
            if is_enrolled == "true":
                events_queryset = events_queryset.intersection(student.events.all())
                courses_queryset = courses_queryset.filter(
                    course_groups__enrolment__student=student
                )
            elif is_enrolled == "false":
                events_queryset = events_queryset.difference(student.events.all())
                courses_queryset = courses_queryset.exclude(
                    course_groups__enrolment__student=student
                )
            else:
                raise ValidationError(
                    detail="is_enrolled must be either 'true' or 'false'"
                )

        # --------------------------------------------------
        #    Formatting
        # --------------------------------------------------
        scheduled = []
        for course in courses_queryset:
            if course.course_groups.exists():
                course_name = course.course_groups.first().course.name
            else:
                course_name = ""
            scheduled.append(
                {
                    "id": course.pk,
                    "type": "course",
                    "title": course_name,
                    "start": course.start,
                    "end": course.end,
                }
            )

        for event in events_queryset:
            scheduled.append(
                {
                    "id": event.id,
                    "type": "event",
                    "title": event.name,
                    "start": event.date,
                    "end": event.end,
                }
            )

        return Response(scheduled)


@login_required
def view_calendar(request):
    return render(request, "calendar/calendar.html")


@login_required
def export_schedule(request):
    student = get_object_or_404(Student, user__pk=request.user.id)

    events = Event.objects.all().intersection(student.events.all())
    courses = Timeslot.objects.filter(course_groups__enrolment__student=student)

    def date_to_TZ(date):
        return "{year:04d}{month:02d}{day:02d}T{hour:02d}{min:02d}{sec:02d}Z".format(
            year=date.year,
            month=date.month,
            day=date.day,
            hour=date.hour,
            min=date.minute,
            sec=date.second,
        )

    ics_data = (
        "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//hacksw/handcal//NONSGML v1.0//EN"
    )

    for course in courses:
        if course.course_groups.exists():
            course_name = course.course_groups.first().course.name
        else:
            course_name = ""

        ics_data += """
            BEGIN:VEVENT
            DTSTART:{start}
            DTEND:{end}
            SUMMARY:{title}
            LOCATION:{place}
            CATEGORIES:{categorie}
            END:VEVENT\
            """.format(
            title=course_name,
            start=date_to_TZ(course.start),
            end=date_to_TZ(course.end),
            place=course.place,
            categorie="Cours",
        )

    for event in events:
        ics_data += """
            BEGIN:VEVENT
            DTSTART:{start}
            DTEND:{end}
            SUMMARY:{title}
            LOCATION:{place}
            ORGANIZER;CN={organizer}
            CATEGORIES:{categorie}
            END:VEVENT\
            """.format(
            title=event.name,
            start=date_to_TZ(event.date),
            end=date_to_TZ(event.end),
            place=event.location,
            organizer=event.club.name,
            categorie="Event",
        )

    ics_data += "\nEND:VCALENDAR"
    response = HttpResponse(ics_data, content_type="text/plain")
    response["Content-Disposition"] = 'attachment; filename="emploidutemps_upont.ics"'
    return response
