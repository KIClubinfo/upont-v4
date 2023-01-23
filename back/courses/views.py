import datetime

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import filters, views, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from social.models import Student

from .models import Course, CourseDepartment, Enrolment, Group, Timeslot
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
                queryset = queryset.filter(
                    groups__enrolment__student=student
                ).distinct()
            elif is_enrolled == "false":
                queryset = queryset.exclude(groups__enrolment__student=student)
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
    """
    Viewset that allow Timeslots to be viewed

    Args:

      * "is_enrolled" = true|false

            - if true, return only the timeslots associated with courses in
              which the current user is enrolled

            - if false, return only the timeslots associated with courses in
              which the current user is not enrolled

            - by default, return all timeslots
    """

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


@login_required
def index_courses(request):
    return render(request, "courses/index_courses.html")


@login_required
def view_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    student = get_object_or_404(Student, user__id=request.user.id)
    context = {
        "course": course,
        "student": student,
    }
    return render(request, "courses/view_course.html", context)


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


@login_required
def join_group(request, group_id, action):
    group = get_object_or_404(Group, id=group_id)
    student = get_object_or_404(Student, user__id=request.user.id)
    # Remove all the groups of this course that the student follow
    query = group.course.groups.all() & student.course.all()
    student.course.remove(*query)
    if action == "Join_group" or action == "Join_course":
        enrolment = Enrolment(
            group=group,
            student=student,
        )
        enrolment.save()
        if action == "Join_group":
            # select the null group if he exists
            null_group = group.course.groups.all().filter(number__isnull=True)[:1].get()
            if null_group is not None:
                enrolment = Enrolment(
                    group=null_group,
                    student=student,
                )
                enrolment.save()
    elif action != "Leave_group" and action != "Leave_course":
        return HttpResponse(status=500)
    return redirect("courses:course_detail", group.course.id)
