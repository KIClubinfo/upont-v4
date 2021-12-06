from django.shortcuts import render, get_object_or_404
from .models import Post, Event


def posts(request):
    all_posts_list = Post.objects.order_by('-date')
    context = {'all_posts_list': all_posts_list}
    return render(request, 'news/posts.html', context)


def events(request):
    all_events_list = Event.objects.order_by('-date')
    context = {'all_events_list': all_events_list}
    return render(request, 'news/events.html', context)


def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    context = {'event': event}
    return render(request, 'news/event_detail.html', context)
