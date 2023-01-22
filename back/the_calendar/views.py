from courses.models import Timeslot
from django.contrib.auth.decorators import login_required
from django.db.models import Q
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
                ).distinct()
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
