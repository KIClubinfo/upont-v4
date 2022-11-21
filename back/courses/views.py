from django.http import HttpResponse


def test_to_delete(request):
    return HttpResponse("It works !")
