# Create your views here.

from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from social.models import Club
from trade.forms import EditPrice

from .forms import EditAlcohol


def manage_accounts(request):
    context = {}
    return render(request, "pochtron/test.html", context)


def shop(request):
    context = {}
    return render(request, "pochtron/test.html", context)


def create_consos(request):
    context = {}
    if request.method == "POST":
        if "Create" in request.POST:
            conso_form = EditAlcohol(
                request.user.id,
                request.POST,
                request.FILES,
            )
            if conso_form.is_valid():
                conso = conso_form.save(commit=False)
                conso.club = get_object_or_404(Club, name="Foyer")
                conso.save()
                price_form = EditPrice(
                    request.user.id,
                    request.POST,
                    request.FILES,
                )
                if price_form.is_valid:
                    price = price_form.save(commit=False)
                    price.date = timezone.now()
                    price.good = conso
                    price.save()
        return render(request, "pochtron/create_consos.html", context)
    else:
        conso_form = EditAlcohol(get_object_or_404(Club, name="Foyer"))
        price_form = EditPrice()
    context["EditAlcohol"] = conso_form
    context["EditPrice"] = price_form
    return render(request, "pochtron/create_consos.html", context)


def global_stats(request):
    context = {}
    return render(request, "pochtron/test.html", context)
