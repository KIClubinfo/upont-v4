from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from social.models import Club, Student
from trade.forms import EditPrice

from .forms import EditAlcohol
from .models import Alcohol
from .serializers import AlcoholSerializer


class SearchAlcohol(APIView):
    """
    API endpoint that returns the alcohols whose name contains the query.
    """

    def get(self, request):
        if "alcohol" in request.GET and request.GET["alcohol"].strip():
            query = request.GET.get("alcohol", None)
            alcohols = Alcohol.objects.filter(name__icontains=query).order_by("-name")[
                :5
            ]
        else:
            alcohols = Alcohol.objects.all().order_by("-name")[:5]
        serializer = AlcoholSerializer(alcohols, many=True)
        return Response({"alcohols": serializer.data})


@login_required
def home(request):
    context = {}
    club = get_object_or_404(Club, name="Foyer")
    student = get_object_or_404(Student, user__pk=request.user.id)
    context["admin"] = club.is_member(student.id)
    return render(request, "pochtron/home.html", context)


@login_required
def admin_home_page(request):
    club = get_object_or_404(Club, name="Foyer")
    student = get_object_or_404(Student, user__pk=request.user.id)
    if not club.is_member(student.id):
        raise PermissionDenied
    consommations = Alcohol.objects.filter(club=club)
    context = {"consommations": consommations}
    return render(request, "pochtron/admin.html", context)


@login_required
def manage_accounts(request):
    context = {}
    return render(request, "pochtron/test.html", context)


@login_required
def shop(request):
    context = {}
    club = get_object_or_404(Club, name="Foyer")
    student = get_object_or_404(Student, user__pk=request.user.id)
    if not club.is_member(student.id):
        raise PermissionDenied
    return render(request, "pochtron/shop.html", context)


@login_required
def conso_create(request):
    context = {"create": True}
    club = get_object_or_404(Club, name="Foyer")
    student = get_object_or_404(Student, user__pk=request.user.id)
    if not club.is_member(student.id):
        raise PermissionDenied

    if request.method == "POST":
        conso_form = EditAlcohol(
            {
                "name": request.POST["name"],
                "degree": request.POST["degree"],
                "volume": request.POST["volume"],
                "club": club,
            },
        )
        if conso_form.is_valid():
            conso = conso_form.save()
            price_form = EditPrice(
                {"price": request.POST["price"], "date": timezone.now(), "good": conso},
            )
            if price_form.is_valid:
                price_form.save()
                return HttpResponseRedirect(reverse("pochtron:admin"))
    else:
        conso_form = EditAlcohol()
        price_form = EditPrice()
    context["EditAlcohol"] = conso_form
    context["EditPrice"] = price_form
    return render(request, "pochtron/create_consos.html", context)


@login_required
def conso_edit(request, conso_id):
    context = {"edit": True}
    club = get_object_or_404(Club, name="Foyer")
    student = get_object_or_404(Student, user__pk=request.user.id)
    conso = get_object_or_404(Alcohol, pk=conso_id)
    if not club.is_member(student.id):
        raise PermissionDenied

    if request.method == "POST":
        conso_form = EditAlcohol(
            {
                "name": request.POST["name"],
                "degree": request.POST["degree"],
                "volume": request.POST["volume"],
                "club": club,
            },
            instance=conso,
        )
        if conso_form.is_valid():
            conso = conso_form.save()
            price_form = EditPrice(
                {"price": request.POST["price"], "date": timezone.now(), "good": conso},
            )
            if price_form.is_valid:
                price_form.save()
                return HttpResponseRedirect(reverse("pochtron:admin"))
    else:
        conso_form = EditAlcohol()
        price_form = EditPrice()
        conso_form.fields["name"].initial = conso.name
        conso_form.fields["degree"].initial = conso.degree
        conso_form.fields["volume"].initial = conso.volume
        price_form.fields["price"].initial = conso.price
    context["EditAlcohol"] = conso_form
    context["EditPrice"] = price_form
    return render(request, "pochtron/create_consos.html", context)


@login_required
def global_stats(request):
    context = {}
    return render(request, "pochtron/test.html", context)
