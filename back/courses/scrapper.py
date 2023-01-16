import datetime

import requests
from bs4 import BeautifulSoup
from django.utils import timezone

from .models import Course, Group, Timeslot


def parse_hours(date, text_hour):
    hour_min = text_hour.split(":")
    return timezone.make_aware(
        datetime.datetime(
            date.year, date.month, date.day, int(hour_min[0]), int(hour_min[1])
        )
    )


def get_schedule(date):
    """
    Update the timeslot store in database for the date given in date
    according to emploidutemps.enpc.org
    """
    url = "https://emploidutemps.enpc.fr/?code_departement=&mydate={day:02d}%2F{month:02d}%2F{year}".format(
        day=date.day, month=date.month, year=date.year
    )
    page = requests.get(url)
    page.encoding = "utf-8"

    soup = BeautifulSoup(page.content, "html.parser")

    entry = soup.find_all("tr", attrs={"height": "30"})

    today_range = [
        timezone.make_aware(datetime.datetime(date.year, date.month, date.day, 0, 0)),
        timezone.make_aware(datetime.datetime(date.year, date.month, date.day, 23, 59)),
    ]

    Timeslot.objects.filter(start__range=today_range).delete()

    for course_entry in entry:
        # --------------------------------------------------
        # Scrapping the data from the website page
        # --------------------------------------------------
        infos = course_entry.find_all("td")
        start, end = map(
            lambda h: parse_hours(date, h), infos[0].text.strip().split("-")
        )
        department = infos[1].text.strip()
        emplacement = infos[2].text.split("-")[0].strip()
        group = infos[3].text.strip()
        group_number = int(group[3]) if group else None
        if "-" not in infos[4].text:
            acronym = ""
            # name = infos[4].text.strip()
        else:
            acronym, _ = map(lambda s: s.strip(), infos[4].text.split("-", maxsplit=1))

        # --------------------------------------------------
        # Inserting the data in the database
        # --------------------------------------------------

        # The courses for the DLC department have no accronym so they should be identify
        # by name (and sometime the name on the website is not fully written)
        # therefore we have to handle them separately
        if acronym and department != "DLC":
            course_query = Course.objects.filter(acronym=acronym)
            if course_query.exists():
                course = course_query.first()

                # Sometimes there are several timeslot for the same course but
                # the group number is not specify, this is handle by the second
                # condition of "or" operator
                if (group_number is not None) or (
                    group_number is None
                    and not Timeslot.objects.filter(
                        start__range=[start, end], course_groups__course=course
                    ).exists()
                ):

                    timeslot = Timeslot(
                        start=start,
                        end=end,
                        place=emplacement,
                    )
                    timeslot.save()

                    if group_number is not None:
                        group_query = Group.objects.filter(
                            course=course,
                            number=group_number,
                        )

                        if group_query.exists():
                            group = group_query.first()
                        else:
                            group = Group(
                                course=course,
                                teacher=course.teacher,
                                number=group_number,
                            )
                            group.save()

                        timeslot.course_groups.add(group)
                    else:
                        group_query = Group.objects.filter(
                            course=course,
                        )

                        if group_query.exists():
                            timeslot.course_groups.add(*group_query)
                        else:
                            group = Group(course=course, teacher=course.teacher)
                            group.save()
                            timeslot.course_groups.add(group)
