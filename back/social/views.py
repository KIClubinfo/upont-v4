from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q
from django.db.models.functions import Greatest
from django.shortcuts import get_object_or_404, redirect, render
from django.http import Http404

from .forms import EditProfile
from .models import Club, Membership, Student, Category


@login_required(login_url="/login/")
def index_users(request):
    all_student_list = Student.objects.order_by("-promo__year", "user__first_name")
    context = {
        "all_student_list": all_student_list,
        "student_displayed_list": all_student_list
        }
    return render(request, "social/index_users.html", context)


@login_required(login_url="/login/")
def profile(request, student_id=None):
    if student_id is None:
        student_id = request.user.id
    student = get_object_or_404(Student, pk=student_id)
    membership_club_list = Membership.objects.filter(student__pk=student_id)
    all_student_list = Student.objects.order_by("user__first_name")
    context = {
        "all_student_list": all_student_list,
        "student": student,
        "membership_club_list": membership_club_list,
    }
    if student_id == request.user.id:
        return render(request, "social/profile.html", context)
    else:
        return render(request, "social/profile_viewed.html", context)


@login_required(login_url="/login/")
def search(request):
    searched_expression = "Avant de trouver quelque chose, il faut le chercher."

    if ("user" in request.GET) and request.GET["user"].strip():
        all_student_list = Student.objects.order_by("-promo__year", "user__first_name")
        context = {"all_student_list": all_student_list}
        found_students, searched_expression = search_user(request)
        context["student_displayed_list"] = found_students
        context["searched_expression"] = searched_expression
        return render(request, "social/index_users.html", context)

    if ("club" in request.GET) and request.GET["club"].strip():
        all_clubs_list = Club.objects.order_by("name")
        all_categories_list = Category.objects.order_by("name")
        my_memberships_list = Membership.objects.filter(student__user__id=request.user.id)
        context = {
            "all_clubs_list": all_clubs_list,
            "all_categories_list": all_categories_list,
            "my_memberships_list": my_memberships_list
            }
        found_clubs, searched_expression = search_club(request)
        context["club_displayed_list"] = found_clubs
        context["searched_expression"] = searched_expression
        return render(request, "social/index_clubs.html", context)

    raise Http404


def partition(words):
    gaps = len(words) - 1  # one gap less than words (fencepost problem)
    for i in range(1 << gaps):  # the 2^n possible partitions
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
    queryset = Student.objects.none()

    for possible_list in partition(key_words_list):
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
    queryset = Club.objects.none()

    for possible_list in partition(key_words_list):
        partial_queryset = Club.objects.all()

        for key_word in possible_list:
            partial_queryset = partial_queryset.annotate(
                similarity=Greatest(
                    TrigramSimilarity("name", key_word),
                    TrigramSimilarity("nickname", key_word),
                    TrigramSimilarity("category__name", key_word),
                )
            )
            partial_queryset = partial_queryset.filter(
                Q(name__trigram_similar=key_word)
                | Q(nickname__iexact=key_word)
                | Q(category__name__iexact=key_word),
                similarity__gt=0.3,
            )
        queryset |= partial_queryset.distinct("name")
    found_clubs = queryset.order_by("name")
    return found_clubs, searched_expression


@login_required
def index_profile(request):
    return render(request, "social/index_profile.html")


@login_required
@login_required(login_url="/login/")
def profile_edit(request):
    student_id = request.user.id
    student = get_object_or_404(Student, pk=student_id)
    membership_club_list = Membership.objects.filter(student__pk=student_id)
    all_student_list = Student.objects.order_by("user__first_name")
    context = {
        "all_student_list": all_student_list,
        "student": student,
        "membership_club_list": membership_club_list,
    }

    if request.method == "POST":
        if "Annuler" in request.POST:
            return redirect("/social/profile")
        elif "Valider" in request.POST:
            form = EditProfile(
                request.POST,
                request.FILES,
                instance=Student.objects.get(user=request.user),
            )
            if form.is_valid():
                if "picture" in request.FILES:
                    student.picture.delete()
                form.save()
                return redirect("/social/profile")

    else:
        form = EditProfile()
        form.fields["phone_number"].initial = student.phone_number
        form.fields["department"].initial = student.department
        context["EditProfile"] = form
    return render(request, "social/profile_edit.html", context)


@login_required
def index_clubs(request):
    all_clubs_list = Club.objects.order_by("name")
    context = {
        "all_clubs_list": all_clubs_list,
        "club_displayed_list": all_clubs_list,
    }
    all_categories_list = Category.objects.order_by("name")
    context["all_categories_list"] = all_categories_list

    my_memberships_list = Membership.objects.filter(student__user__id=request.user.id)
    context["my_memberships_list"] = my_memberships_list
    return render(request, "social/index_clubs.html", context)


@login_required
def view_club(request, club_id):
    club = get_object_or_404(Club, pk=club_id)
    members = Membership.objects.filter(club__id=club_id)
    context = {"club": club, "members": members}
    return render(request, "social/view_club.html", context)


@login_required(login_url="/login/")
def club_edit(request, club_id):
    student_id = request.user.id
    student = get_object_or_404(Student, pk=student_id)
    club = get_object_or_404(Club, pk=club_id)
    membership_club_list = Membership.objects.filter(student__pk=student_id, club__pk=club_id)
    context = {
        "all_student_list": all_student_list,
        "student": student,
        "membership_club_list": membership_club_list,
    }

    if request.method == "POST":
        if "Annuler" in request.POST:
            return redirect("/social/profile")
        elif "Valider" in request.POST:
            form = EditProfile(
                request.POST,
                request.FILES,
                instance=Club.objects.get(user=request.user),
            )
            if form.is_valid():
                if "picture" in request.FILES:
                    student.picture.delete()
                form.save()
                return redirect("/social/profile")

    else:
        form = EditProfile()
        form.fields["phone_number"].initial = student.phone_number
        form.fields["department"].initial = student.department
        context["EditProfile"] = form
    return render(request, "social/profile_edit.html", context)