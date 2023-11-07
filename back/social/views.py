from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import TrigramSimilarity
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db.models.functions import Greatest
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import AddMember, AddRole, ClubRequestForm, EditClub, EditProfile
from .models import Category, Club, Membership, NotificationToken, Role, Student
from .serializers import (
    ClubSerializer,
    ClubSerializerLite,
    RoleSerializer,
    StudentSerializer,
)


@login_required
def index_users(request):
    all_student_list = Student.objects.order_by(
        "-promo__year", "user__first_name", "user__last_name"
    )
    context = {
        "all_student_list": all_student_list,
        "display_students_with_react": True,
    }
    return render(request, "social/index_users.html", context)


class StudentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows students to be viewed.
    """

    queryset = Student.objects.all().order_by(
        "-promo__year", "user__first_name", "user__last_name"
    )
    serializer_class = StudentSerializer
    http_method_names = ["get"]


class OneStudentView(APIView):
    """
    API endpoint that allows a unique student to be viewed.
    """

    def get(self, request):
        student = get_object_or_404(Student, user__id=request.GET["id"])
        serializer = StudentSerializer(student)
        return Response({"student": serializer.data})

    @classmethod
    def get_extra_actions(cls):
        return []


class CurrentStudentView(APIView):
    """
    API endpoint that returns the current student.
    """

    def get(self, request):
        student = get_object_or_404(Student, user__id=request.user.id)
        serializer = StudentSerializer(student)
        return Response({"student": serializer.data})

    @classmethod
    def get_extra_actions(cls):
        return []


class StudentCanPublishAs(APIView):
    """
    API endpoint that returns the clubs that student can publish as.
    """

    def get(self, request):
        data = {"-1": "Élève"}
        for membership in Membership.objects.filter(student__user__id=request.user.id):
            data[membership.club.id] = membership.club.name
        return Response({"can_publish_as": data})

    @classmethod
    def get_extra_actions(cls):
        return []


class StudentMembershipView(APIView):
    """
    API endpoint that returns the clubs that student can publish as.
    """

    def get(self, request):
        student = get_object_or_404(Student, user__pk=request.GET["id"])
        data = []
        for membership in Membership.objects.filter(student__user__id=student.user.id):
            club = Club.objects.get(id=membership.club.id)
            serializer = ClubSerializerLite(club)
            club_data = serializer.data
            club_data["is_admin"] = membership.is_admin
            club_data["is_old"] = membership.is_old
            data.append(club_data)
        return Response({"is_member_of": data})

    @classmethod
    def get_extra_actions(cls):
        return []


class SearchRole(APIView):
    """
    API endpoint that returns the roles whose name contains the query.
    """

    def get(self, request):
        if "role" in request.GET and request.GET["role"].strip():
            query = request.GET.get("role", None)
            roles = Role.objects.filter(name__icontains=query).order_by("-name")[:3]
        else:
            roles = Role.objects.all().order_by("-name")[:3]
        serializer = RoleSerializer(roles, many=True)
        return Response({"roles": serializer.data})


class SearchStudent(APIView):
    """
    API endpoint that returns the student whose username contains the query.
    """

    def get(self, request):
        if "user" in request.GET and request.GET["user"].strip():
            students, searched_expression = search_user(request)
            students = students[:25]
        else:
            students = Student.objects.all().order_by(
                "-promo__year", "user__first_name", "user__last_name"
            )[:25]
        serializer = StudentSerializer(students, many=True)
        return Response({"students": serializer.data})


class NotificationTokenView(APIView):
    """
    API endpoint that returns or edit the student whose username contains the query.
    """

    def post(self, request):
        token = request.data["token"]
        if not NotificationToken.objects.filter(token=token).exists():
            NotificationToken.objects.create(
                student=Student.objects.get(user__id=request.user.id), token=token
            )
            return Response({"status": "created"})
        return Response({"status": "exists"})


class ClubsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows clubs to be viewed.
    """

    queryset = Club.objects.all().order_by("label", "name", "nickname")
    serializer_class = ClubSerializer
    http_method_names = ["get"]


class OneClubView(APIView):
    """
    API endpoint that allows a unique club to be viewed.
    """

    def get(self, request):
        club = get_object_or_404(Club, id=request.GET["id"])
        serializer = ClubSerializer(club)
        return Response({"club": serializer.data})

    @classmethod
    def get_extra_actions(cls):
        return []


class SearchClub(APIView):
    """
    API endpoint that returns the club whose name contains the query.
    """

    def get(self, request):
        if "club" in request.GET and request.GET["club"].strip():
            clubs, searched_expression = search_club(request)
            clubs = clubs[:25]
        else:
            clubs = Club.objects.all().order_by("label", "name", "nickname")[:25]
        serializer = ClubSerializer(clubs, many=True)
        return Response({"clubs": serializer.data})


class ProfilePicUpdate(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        image = request.data["image"]
        print(request.data)
        student = get_object_or_404(Student, user__id=request.user.id)
        student.picture = image
        student.save()
        return Response({"status": "ok"})


@login_required
def profile(request, user_id=None):
    if user_id is None:
        user_id = request.user.id
    student = get_object_or_404(Student, user__pk=user_id)
    membership_club_list = Membership.objects.filter(student__user__pk=user_id)
    all_student_list = Student.objects.order_by("user__first_name")
    context = {
        "all_student_list": all_student_list,
        "student": student,
        "membership_club_list": membership_club_list,
        "complete_name": student.user.first_name + " " + student.user.last_name,
    }
    if user_id == request.user.id:
        return render(request, "social/profile.html", context)
    else:
        return render(request, "social/profile_viewed.html", context)


@login_required
def search(request):
    searched_expression = "Si trouver quelque chose tu veux, le chercher il te faut."

    if "user" in request.GET:
        all_student_list = Student.objects.order_by("-promo__year", "user__first_name")
        context = {"all_student_list": all_student_list}
        if request.GET["user"].strip():
            found_students, searched_expression = search_user(request)
            context["student_displayed_list"] = found_students
        context["searched_expression"] = searched_expression
        return render(request, "social/index_users.html", context)

    if "club" in request.GET:
        all_clubs_list = Club.objects.order_by("name")
        all_categories_list = Category.objects.order_by("name")
        all_label_list = Club.Label.choices
        my_memberships_list = Membership.objects.filter(
            student__user__id=request.user.id
        )
        context = {
            "all_clubs_list": all_clubs_list,
            "all_categories_list": all_categories_list,
            "my_memberships_list": my_memberships_list,
            "all_label_list": all_label_list,
        }
        if request.GET["club"].strip():
            found_clubs, searched_expression = search_club(request)
            context["club_displayed_list"] = found_clubs
        context["searched_expression"] = searched_expression
        return render(request, "social/index_clubs.html", context)

    raise Http404


def partition(words):
    gaps = len(words) - 1  # one gap less than words (fencepost problem)
    for i in range(1, 1 << gaps):  # the 2^n possible partitions
        result = words[:1]  # The result starts with the first word
        for word in words[1:]:
            if i & 1:
                result.append(word)  # If "1" split at the gap
            else:
                result[-1] += " " + word  # If "0", don't split at the gap
            i >>= 1  # Next 0 or 1 indicating split or don't split
        yield result  # cough up r


def search_user(request):
    searched_expression = request.GET.get("user", None)
    key_words_list = [word.strip() for word in searched_expression.split()]
    all_possible_lists = [key_words_list]
    if len(key_words_list) > 1:
        all_possible_lists += [
            possible_list for possible_list in partition(key_words_list)
        ]
    queryset = Student.objects.none()

    for possible_list in all_possible_lists:
        partial_queryset = Student.objects.all()

        for key_word in possible_list:
            partial_queryset = partial_queryset.annotate(
                similarity=Greatest(
                    TrigramSimilarity("user__first_name", key_word),
                    TrigramSimilarity("user__last_name", key_word),
                    TrigramSimilarity("promo__nickname", key_word),
                    TrigramSimilarity("department", key_word),
                )
            )
            partial_queryset = partial_queryset.filter(
                Q(user__first_name__trigram_similar=key_word)
                | Q(user__last_name__trigram_similar=key_word)
                | Q(promo__nickname__iexact=key_word)
                | Q(department__iexact=key_word),
                similarity__gt=0.3,
            )
        queryset |= partial_queryset
    found_students = queryset.order_by("-promo__year", "user__first_name")
    return found_students, searched_expression


def search_club(request):
    searched_expression = request.GET.get("club", None)
    key_words_list = [word.strip() for word in searched_expression.split()]
    all_possible_lists = [key_words_list]
    if len(key_words_list) > 1:
        all_possible_lists += [
            possible_list for possible_list in partition(key_words_list)
        ]

    queryset = Club.objects.none()

    for possible_list in all_possible_lists:
        partial_queryset = Club.objects.all()

        for key_word in possible_list:
            partial_queryset = partial_queryset.annotate(
                similarity=Greatest(
                    TrigramSimilarity("name", key_word),
                    TrigramSimilarity("nickname", key_word),
                    TrigramSimilarity("category__name", key_word),
                    TrigramSimilarity("label__name", key_word),
                )
            )
            partial_queryset = partial_queryset.filter(
                Q(name__trigram_similar=key_word)
                | Q(nickname__iexact=key_word)
                | Q(category__name__iexact=key_word)
                | Q(label__name__iexact=key_word),
                similarity__gt=0.3,
            )
        queryset |= partial_queryset.distinct("name")
    found_clubs = queryset.order_by("name")
    return found_clubs, searched_expression


@login_required
def profile_edit(request):
    user_id = request.user.id
    student = get_object_or_404(Student, user__pk=user_id)
    membership_club_list = Membership.objects.filter(student__user__pk=user_id)
    context = {
        "student": student,
        "membership_club_list": membership_club_list,
    }

    if request.method == "POST":
        if "Annuler" in request.POST:
            return redirect("social:profile")
        elif "Valider" in request.POST:
            form = EditProfile(
                request.POST,
                request.FILES,
                instance=Student.objects.get(user=request.user),
            )
            if form.is_valid():
                form.save()
                if "picture" in request.FILES:
                    student.picture.delete(save=False)
                return redirect("social:profile")

    else:
        form = EditProfile()
        form.fields["phone_number"].initial = student.phone_number
        form.fields["department"].initial = student.department
        form.fields["picture"].initial = student.picture
        form.fields["gender"].initial = student.gender
        form.fields["birthdate"].initial = student.birthdate
        form.fields["biography"].initial = student.biography
    context["EditProfile"] = form
    return render(request, "social/profile_edit.html", context)


@login_required
def index_clubs(request):
    all_clubs_list = Club.objects.order_by("name")
    active_clubs_list = Club.objects.filter(active=True).order_by("name")
    inactive_clubs_list = Club.objects.filter(active=False).order_by("name")
    ASSO_club_list = Club.objects.filter(label=Club.Label.ASSO, active=True).order_by(
        "name"
    )
    CLUB_club_list = Club.objects.filter(label=Club.Label.CLUB, active=True).order_by(
        "name"
    )
    LISTE_club_list = Club.objects.filter(label=Club.Label.LISTE, active=True).order_by(
        "name"
    )
    POLE_club_list = Club.objects.filter(label=Club.Label.POLE, active=True).order_by(
        "name"
    )
    context = {
        "all_clubs_list": all_clubs_list,
        "club_displayed_list": active_clubs_list,
        "inactive_clubs_list": inactive_clubs_list,
        "ASSO_club_list": ASSO_club_list,
        "CLUB_club_list": CLUB_club_list,
        "LISTE_club_list": LISTE_club_list,
        "POLE_club_list": POLE_club_list,
    }
    all_categories_list = Category.objects.order_by("name")
    context["all_categories_list"] = all_categories_list

    my_memberships_list = Membership.objects.filter(student__user__id=request.user.id)
    context["my_memberships_list"] = my_memberships_list
    return render(request, "social/index_clubs.html", context)


def get_old_members(club_id):  # Grouping old members of club_id by promos in a dict
    old_members = {}
    promos = (
        Membership.objects.filter(club__id=club_id, is_old=True)
        .values("student__promo__nickname")
        .distinct()
        .order_by("-student__promo__year")
    )  # Getting every promo nickname with old members
    for promo in promos:
        promo_nickname = promo["student__promo__nickname"]
        promo_members = Membership.objects.filter(
            club__id=club_id, is_old=True, student__promo__nickname=promo_nickname
        )
        old_members[promo_nickname] = promo_members
    return old_members


@login_required
def view_club(request, club_id):
    club = get_object_or_404(Club, pk=club_id)
    active_members = Membership.objects.filter(club__id=club_id, is_old=False)
    old_members = get_old_members(club_id)
    membership_club_list = Membership.objects.filter(
        student__user__id=request.user.id, club__pk=club_id
    )
    if not membership_club_list:  # If no match is found
        is_admin = False
    elif not membership_club_list[0].is_admin:  # If the user does not have the rights
        is_admin = False
    else:
        is_admin = True
    context = {
        "club": club,
        "active_members": active_members,
        "old_members": old_members,
        "is_admin": is_admin,
    }
    return render(request, "social/view_club.html", context)


@login_required
def club_edit(request, club_id):
    student = get_object_or_404(Student, user__id=request.user.id)
    club = get_object_or_404(Club, pk=club_id)
    student_membership_club = Membership.objects.filter(
        student__pk=student.id, club__pk=club_id
    )
    all_active_club_memberships = Membership.objects.filter(
        club__pk=club_id, is_old=False
    )
    all_old_club_memberships = get_old_members(club_id)
    if not student_membership_club:  # If no match is found
        raise PermissionDenied
    if not student_membership_club[0].is_admin:  # If the user does not have the rights
        raise PermissionDenied

    context = {
        "student": student,
        "club": club,
        "all_active_club_memberships": all_active_club_memberships,
        "all_old_club_memberships": all_old_club_memberships,
    }

    if request.method == "POST":
        if "Annuler" in request.POST:
            return redirect("social:club_detail", club_id=club.id)

        elif "Valider" in request.POST:
            form_club = EditClub(
                request.POST,
                request.FILES,
                instance=Club.objects.get(id=club.id),
            )
            if form_club.is_valid():
                if "logo" in request.FILES:
                    club.logo.delete(save=False)
                if "background_picture" in request.FILES:
                    club.background_picture.delete(save=False)
                form_club.save()
                return redirect("social:club_detail", club_id=club.id)

        elif "Ajouter-Membre" in request.POST:
            if (
                not request.POST["student"].isdigit()
                or not request.POST["role"].isdigit()
            ):
                context[
                    "error"
                ] = "Fais bien attention à sélectionner l'élève ET le rôle"
                context["AddMember"] = AddMember()
                return render(request, "social/club_edit.html", context)

            else:
                try:
                    membership_added = Membership.objects.filter(
                        student__id=request.POST["student"], club=club
                    )
                    if membership_added:
                        membership_added = membership_added[0]
                    else:
                        membership_added = Membership.objects.create(
                            student=get_object_or_404(
                                Student, pk=request.POST["student"]
                            ),
                            club=club,
                            role=None,
                            is_admin=False,
                        )
                    form_membership = AddMember(request.POST, instance=membership_added)
                    if form_membership.is_valid():
                        form_membership.save()
                    return redirect("social:club_edit", club_id=club.id)
                except Student.DoesNotExist:
                    return redirect("social:club_edit", club_id=club.id)

        elif "Vieux" in request.POST:
            old_member = Membership.objects.get(
                club=club, student__id=request.POST["student_id"]
            )
            old_member.is_admin = False
            old_member.is_old = True
            old_member.save()
            if student.id == int(
                request.POST["student_id"]
            ):  # If the user commits sudoku
                return redirect("social:club_detail", club_id=club.id)
            else:
                return redirect("social:club_edit", club_id=club.id)

        elif "Actif" in request.POST:
            not_old_member = Membership.objects.get(
                club=club, student__id=request.POST["student_id"]
            )
            not_old_member.is_old = False
            not_old_member.save()
            return redirect("social:club_edit", club_id=club.id)

        elif "Supprimer" in request.POST:
            deleted_member = Membership.objects.get(
                club=club, student__id=request.POST["student_id"]
            )
            deleted_member.delete()
            if student.id == int(
                request.POST["student_id"]
            ):  # If the user commits sudoku
                return redirect("social:club_detail", club_id=club.id)
            else:
                return redirect("social:club_edit", club_id=club.id)

        elif "Ajouter-Role" in request.POST:
            form_role = AddRole(request.POST)
            existing_role_names = list(
                Role.objects.all().values_list("name", flat=True)
            )
            if form_role.is_valid() and (
                form_role["name"].value() not in existing_role_names
            ):
                form_role.save()
            return redirect("social:club_edit", club_id=club.id)

    else:
        form_club = EditClub()
        form_membership = AddMember()
        form_role = AddRole()

        form_club.fields["name"].initial = club.name
        form_club.fields["nickname"].initial = club.nickname
        form_club.fields["logo"].initial = club.logo
        form_club.fields["background_picture"].initial = club.background_picture
        form_club.fields["description"].initial = club.description
        form_club.fields["active"].initial = club.active
        form_club.fields["has_fee"].initial = club.has_fee
        form_club.fields["category"].initial = [
            category.pk for category in club.category.all()
        ]
        form_club.fields["label"].initial = club.label

    context["EditClub"] = form_club
    context["AddMember"] = form_membership
    context["AddRole"] = form_role
    return render(request, "social/club_edit.html", context)


@login_required
def club_request(request):
    context = {}

    if request.method == "POST":
        if "Annuler" in request.POST:
            return redirect("social:club_index")
        elif "Valider" in request.POST:
            form = ClubRequestForm(
                request.POST,
            )
            if form.is_valid():
                new_request = form.save(commit=False)
                new_request.student = Student.objects.get(user__id=request.user.id)
                new_request.save()
                return redirect("social:club_index")

    else:
        form = ClubRequestForm()
    context["ClubRequest"] = form
    return render(request, "social/club_request.html", context)
