from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EditEvent
from .models import Event, Post


def posts(request):
    all_posts_list = Post.objects.order_by("-date")
    context = {"all_posts_list": all_posts_list}
    return render(request, "news/posts.html", context)


def events(request):
    all_events_list = Event.objects.order_by("-date")
    context = {"all_events_list": all_events_list}
    return render(request, "news/events.html", context)


def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    context = {"event": event}
    return render(request, "news/event_detail.html", context)


@login_required(login_url="/login/")
def event_edit(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    context = {}
    if request.method == "POST":
        if "Annuler" in request.POST:
            return redirect("news:event_detail", event_id=event.id)
        elif "Valider" in request.POST:
            form = EditEvent(
                request.POST,
                request.FILES,
                instance=Event.objects.get(id=event_id),
            )
            if form.is_valid():
                if "picture" in request.FILES:
                    event.picture.delete()
                form.save()
                return redirect("news:event_detail", event_id=event.id)

    else:
        form = EditEvent()
        form.fields["name"].initial = event.name
        form.fields["description"].initial = event.description
        form.fields["date"].initial = event.date
        form.fields["location"].initial = event.location
        form.fields["poster"].initial = event.poster
    context["EditEvent"] = form
    return render(request, "news/event_edit.html", context)
