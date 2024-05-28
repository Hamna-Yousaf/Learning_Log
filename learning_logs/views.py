from django.shortcuts import render,get_object_or_404
from django.http import HttpResponseRedirect, Http404
from .models import Topic,Entries
from django.contrib.auth.decorators import login_required
# For Forms

from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import TopicForm,EntryForm

def index(request):
    return render(request, 'learning_logs/index.html')

# Create your views here.
@login_required
def topics(request):
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': topics}
    return render(request,'learning_logs/topics.html',context=context)
@login_required
def topic(request, topic_id):
    """Show a single topic and all its entries."""
    topic = get_object_or_404(Topic, id=topic_id)
    if topic.owner != request.user:
        raise Http404
    

    entries = topic.entries_set.order_by('date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)


@login_required
def new_topic(request):
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = TopicForm()
    else:
        # POST data submitted; process data.
        form = TopicForm(request.POST)
        if form.is_valid():
            new_topic=form.save(commit=False)
            new_topic.owner = request.user
            form.save()
            return HttpResponseRedirect(reverse('learning_logs:topics'))
    
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)


@login_required
def new_entry(request, topic_id):
    """Add a new entry for a particular topic."""
    topic = Topic.objects.get(id=topic_id)
    
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = EntryForm()
    else:
        # POST data submitted; process data.
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return HttpResponseRedirect(reverse('learning_logs:topic', args=[topic_id]))
    
    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)


@login_required
def edit_entry(request, entry_id):
    """Edit an existing entry."""
    # Get the entry object from the database or return a 404 error if not found.
    entry = get_object_or_404(Entries, id=entry_id)
    topic = entry.topic
    if topic.owner != request.user:
        raise Http404
    
    if request.method == 'POST':
        # POST data submitted; process data.
        form = EntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            # Redirect to the topic detail page after successful edit.
            return HttpResponseRedirect(reverse('learning_logs:topic', args=[topic.id]))
    else:
        # Initial request; pre-fill form with the current entry.
        form = EntryForm(instance=entry)
    
    # Render the template with the form, entry, and topic.
    context = {'form': form, 'entry': entry, 'topic': topic}
    return render(request, 'learning_logs/edit_entry.html', context)
