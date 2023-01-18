import datetime

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render
from rest_framework import filters, views, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from social.models import Student

from .models import Course, CourseDepartment, Group, Timeslot
from .scrapper import get_schedule
from .serializers import CourseSerializer, GroupSerializer, TimeslotSerializer


class ListCourseDepartments(views.APIView):
    """
    View to list all the department a course can belong to
    """

    def get(self, request):
        return Response(CourseDepartment.values)


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    http_method_names = ["get"]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "acronym"]

    def get_queryset(self):
        queryset = Course.objects.all()

        is_enrolled = self.request.GET.get("is_enrolled")
        if is_enrolled is not None:
            student = get_object_or_404(Student, user__id=self.request.user.id)
            if is_enrolled == "true":
                queryset = queryset.filter(group__enrolment__student=student)
            elif is_enrolled == "false":
                queryset = queryset.exclude(group__enrolment__student=student)
            else:
                raise ValidationError(
                    detail="is_enrolled must be either 'true' or 'false'"
                )

        departments = self.request.GET.get("department")
        if departments is not None:
            queryset = queryset.filter(department__in=departments.split(","))

        return queryset.order_by("department", "name")


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    http_method_names = ["get"]


class TimeslotViewSet(viewsets.ModelViewSet):
    serializer_class = TimeslotSerializer
    http_method_names = ["get"]

    def get_queryset(self):
        queryset = Timeslot.objects.all()

        is_enrolled = self.request.GET.get("is_enrolled")
        if is_enrolled is not None:
            student = get_object_or_404(Student, user__id=self.request.user.id)
            if is_enrolled == "true":
                queryset = queryset.filter(course_groups__enrolment__student=student)
            elif is_enrolled == "false":
                queryset = queryset.exclude(course_groups__enrolment__student=student)
            else:
                raise ValidationError(
                    detail="is_enrolled must be either 'true' or 'false'"
                )

        return queryset

    @property
    def paginator(self):
        """
        A parameter no_page is added to disable pagination because we want to
        avoid it for the calendar
        """
        self._paginator = super(TimeslotViewSet, self).paginator
        if "no_page" in self.request.query_params:
            self._paginator = None
        return self._paginator


@login_required
def index_courses(request):
    return render(request, "courses/index_courses.html")


@login_required
def update_timeslots(request):
    if not request.user.is_superuser:
        raise PermissionDenied()

    context = {
        "bad_input": False,
        "updated": False,
    }

    if request.method == "POST":
        input = request.POST["date"].split("/")
        if len(input) != 3:
            context["bad_input"] = True
        else:
            try:
                day = int(input[0])
                month = int(input[1])
                year = int(input[2])
                date = datetime.date(year, month, day)
            except ValueError:
                context["bad_input"] = True
            get_schedule(date)
            context["updated"] = True
            context["date_updated"] = date

    return render(request, "courses/update_timeslots.html", context)
