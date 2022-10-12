import re  # Regular expressions

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from social.models import Club, Student
from trade.forms import EditPrice, EditTradeAdmin
from trade.models import TradeAdmin, Transaction

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

    if (
        club.is_member(student.id)
        and not TradeAdmin.objects.filter(student=student, club=club).exists()
    ):
        # Add member of Foyer to Pochtron Admin
        admin = TradeAdmin(student=student, club=club)
        admin.save()

    context["admin"] = TradeAdmin.objects.filter(student=student, club=club).exists()
    context["user_balance"] = student.balance_in_euros(club)

    context["transactions"] = [
        {
            "product": t.good.name,
            "quantity": t.quantity,
            "price": -t.quantity * t.good.price_at_date(t.date) / 100,
            "date": t.date,
        }
        for t in Transaction.objects.filter(student=student)
        .filter(good__club=club)
        .order_by("-date")
    ]

    return render(request, "pochtron/home.html", context)


@login_required
def admin_home_page(request):
    club = get_object_or_404(Club, name="Foyer")
    student = get_object_or_404(Student, user__pk=request.user.id)

    try:
        admin = TradeAdmin.objects.get(student=student, club=club)
    except TradeAdmin.DoesNotExist:
        raise PermissionDenied

    consommations = Alcohol.objects.filter(club=club)
    for c in consommations:
        c.price_euro = c.price() / 100
    context = {"consommations": consommations, "admin": admin}
    return render(request, "pochtron/admin.html", context)


@login_required
def manage_accounts(request):
    club = get_object_or_404(Club, name="Foyer")
    student = get_object_or_404(Student, user__pk=request.user.id)

    try:
        TradeAdmin.objects.get(student=student, club=club, manage_credits=True)
    except TradeAdmin.DoesNotExist:
        raise PermissionDenied

    context = {}
    return render(request, "pochtron/manage_accounts.html", context)


@login_required
def shop(request):
    context = {}
    club = get_object_or_404(Club, name="Foyer")
    student = get_object_or_404(Student, user__pk=request.user.id)

    try:
        TradeAdmin.objects.get(student=student, club=club, manage_transactions=True)
    except TradeAdmin.DoesNotExist:
        raise PermissionDenied

    return render(request, "pochtron/shop.html", context)


def remove_price_mask(price):
    """
    Remove the mask '000,00 €' of price input and return the price in cents
    """
    # The last element of the spliting is the € symbole
    euro_and_cents = re.split(",| ", price)[:-1]
    if len(euro_and_cents) == 1:
        # the price has no cents
        euro_and_cents.append("00")

    return "".join(euro_and_cents)


@login_required
def conso_create(request):
    context = {"create": True}
    club = get_object_or_404(Club, name="Foyer")
    student = get_object_or_404(Student, user__pk=request.user.id)

    try:
        TradeAdmin.objects.get(student=student, club=club, manage_goods=True)
    except TradeAdmin.DoesNotExist:
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
                {
                    "price": remove_price_mask(request.POST["price"]),
                    "date": timezone.now(),
                    "good": conso,
                },
            )
            if price_form.is_valid():
                price_form.save()
                return HttpResponseRedirect(reverse("pochtron:admin"))
            else:
                # Prevent a good to exists without associated price
                conso.delete()
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

    try:
        TradeAdmin.objects.get(student=student, club=club, manage_goods=True)
    except TradeAdmin.DoesNotExist:
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
                {
                    "price": remove_price_mask(request.POST["price"]),
                    "date": timezone.now(),
                    "good": conso,
                },
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
def manage_admins(request):
    club = get_object_or_404(Club, name="Foyer")
    student = get_object_or_404(Student, user__pk=request.user.id)

    try:
        TradeAdmin.objects.get(student=student, club=club, manage_admins=True)
    except TradeAdmin.DoesNotExist:
        raise PermissionDenied

    context = {"admins": TradeAdmin.objects.filter(club=club).all()}
    return render(request, "pochtron/manage_admins.html", context)


@login_required
def admin_edit(request, admin_id):
    club = get_object_or_404(Club, name="Foyer")
    student = get_object_or_404(Student, user__pk=request.user.id)
    admin = get_object_or_404(TradeAdmin, pk=admin_id, club=club)

    try:
        TradeAdmin.objects.get(student=student, club=club, manage_admins=True)
    except TradeAdmin.DoesNotExist:
        raise PermissionDenied

    if request.method == "POST":
        if "Supprimer" in request.POST:
            admin.delete()
            return redirect("pochtron:manage_admins")
        elif "Valider" in request.POST:
            POST = request.POST.copy()
            POST["club"] = club
            POST["student"] = admin.student
            admin_form = EditTradeAdmin(POST, instance=admin)
            if admin_form.is_valid():
                admin = admin_form.save()
                return redirect("pochtron:manage_admins")
    else:
        admin_form = EditTradeAdmin()
        admin_form.fields["club"].disabled = True
        admin_form.fields["club"].initial = club
        admin_form.fields["student"].disabled = True
        admin_form.fields["student"].initial = admin.student
        admin_form.fields["manage_goods"].initial = admin.manage_goods
        admin_form.fields["manage_transactions"].initial = admin.manage_transactions
        admin_form.fields["manage_credits"].initial = admin.manage_credits
        admin_form.fields["manage_admins"].initial = admin.manage_admins

        context = {
            "Edit": True,
            "admin": admin,
            "EditTradeAdmin": admin_form,
        }
        return render(request, "pochtron/admin_edit.html", context)


@login_required
def admin_create(request):
    club = get_object_or_404(Club, name="Foyer")
    student = get_object_or_404(Student, user__pk=request.user.id)

    try:
        TradeAdmin.objects.get(student=student, club=club, manage_admins=True)
    except TradeAdmin.DoesNotExist:
        raise PermissionDenied

    if request.method == "POST":
        if "Valider" in request.POST:
            POST = request.POST.copy()
            POST["club"] = club
            # admin_student = None if the pair (student, club) is not yet related to a TradeAdmin object
            admin_student = TradeAdmin.objects.filter(
                club=club, student=POST["student"]
            ).first()
            admin_form = EditTradeAdmin(POST, instance=admin_student)
            if admin_form.is_valid():
                admin_form.save()
                return redirect("pochtron:manage_admins")
    else:
        admin_form = EditTradeAdmin()
        admin_form.fields["club"].disabled = True
        admin_form.fields["club"].initial = club
        admin_form.fields["manage_goods"].initial = False
        admin_form.fields["manage_transactions"].initial = False
        admin_form.fields["manage_credits"].initial = False
        admin_form.fields["manage_admins"].initial = False

        context = {
            "Edit": False,
            "EditTradeAdmin": admin_form,
        }
        return render(request, "pochtron/admin_edit.html", context)


class PochtronId(APIView):
    """
    API endpoint that returns the id of the club "Foyer".
    """

    def get(self, request):
        club = get_object_or_404(Club, name="Foyer")
        return Response({"id": club.id})
