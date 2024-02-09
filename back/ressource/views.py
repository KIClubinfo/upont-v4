from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from rest_framework import views, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Logo
from .serializers import LogoSerializer

# class RessourceData(views.APIView):
#     """
#     API endpoint to fetch data for the ressource page
#     """

#     def get(self, request):
#         return Response()


@login_required
def view_logoDisplay(request):
    return render(request, "ressource/logoDisplay.html")


class LogoViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows logos to be viewed or edited.
    """

    queryset = Logo.objects.all()
    serializer_class = LogoSerializer

    def get_queryset(self):
        return Logo.objects.all()
