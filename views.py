from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from cardbox.models import (
    Card,
    Collection,
)

LOGIN_URL = '/cardbox/login/'


# TODO(benedikt) Fix entries not being removed
def _update_many_to_many_field(entries, m2m_field):
    for entry in m2m_field.all():
        if entry not in entries:
            m2m_field.remove(entry)
    for entry in entries:
        m2m_field.add(entry)


def index(request):
    card_list = Card.objects.all()
    paginator = Paginator(card_list, 50)

    page = request.GET.get('page')
    try:
        cards = paginator.page(page)
    except PageNotAnInteger:
        cards = paginator.page(1)
    except EmptyPage:
        cards = paginator.page(paginator.num_pages)

    return render(request, 'cardbox/index.html', {
        'cards': cards,
    })


def login_view(request):
    data = {'next': request.GET.get('next', '')}
    try:
        username = request.POST['username']
        password = request.POST['password']
    except KeyError:
        return render(request, 'cardbox/login.html', data)

    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            try:
                next_url = request.POST['next']
            except KeyError:
                return HttpResponseRedirect(reverse('cardbox:index'))
            return HttpResponseRedirect(next_url)
        else:
            messages.add_message(request, messages.WARNING, 'User not active!')
            return render(request, 'cardbox/login.html', data)
    else:
        messages.add_message(request, messages.WARNING, 'User not found!')
        return render(request, 'cardbox/login.html', data)


def logout_view(request):
    logout(request)
    messages.add_message(request, messages.SUCCESS,
                         "You've successfully logged out.")
    return HttpResponseRedirect(reverse('cardbox:index'))


def cards(request, layout='list'):
    if layout not in ['list', 'grid']:
        layout = 'list'

    card_list = Card.objects.all()
    paginator = Paginator(card_list, 50)

    page = request.GET.get('page')
    try:
        cards = paginator.page(page)
    except PageNotAnInteger:
        cards = paginator.page(1)
    except EmptyPage:
        cards = paginator.page(paginator.num_pages)

    return render(request, 'cardbox/cards_{0}.html'.format(layout), {
        'cards': cards,
    })


def card(request, card_id):
    card = get_object_or_404(Card, pk=card_id)
    return render(request, 'cardbox/card_detail.html', {
        'card': card,
    })


@login_required(login_url=LOGIN_URL)
def collection(request, collection_id):
    return render(request, 'cardbox/welcome.html')


@login_required(login_url=LOGIN_URL)
def edit_collection(request, collection_id=None):
    """Update or create a collection.

    :param int collection_id: The ID of the collection to edit.  Use 0
        to create a new collection.

    """
    data = {}
    if collection_id is None:
        action = 'created'
        collection = Collection(owner=request.user, date_created=timezone.now())
        data['collection'] = None
    else:
        action = 'updated'
        try:
            collection = Collection.objects.filter(
                owner=request.user).get(pk=collection_id)
            data['collection'] = collection
        except Collection.DoesNotExist:
            raise Http404('Collection not found.')

    try:
        name = request.POST['name']
        editor_list = request.POST.get('editors', '').split(',')
        viewer_list = request.POST.get('viewers', '').split(',')
    except KeyError:
        return render(request, 'cardbox/edit_collection.html', data)

    editors = []
    for editor in editor_list:
        try:
            user = User.objects.get(username=editor)
            editors.append(user)
        except User.DoesNotExist:
            data['error_message'] = 'User {0} not found!'.format(editor)
            return render(request, 'cardbox/edit_collection.html', data)

    viewers = []
    for viewer in viewer_list:
        try:
            user = User.objects.get(username=viewer)
            viewers.append(user)
        except User.DoesNotExist:
            # data['error_message'] = 'User {0} not found!'.format(editor)
            messages.add_message(request, messages.WARNING,
                                 'No user with name {0}.'.format(viewer))
            return render(request, 'cardbox/edit_collection', data)

    collection.name = name
    collection.save()

    _update_many_to_many_field(editors, collection.editors)
    _update_many_to_many_field(viewers, collection.viewers)

    messages.add_message(request, messages.SUCCESS,
                         'Collection {0} successfully {1}.'
                         .format(collection.name, action))
    return HttpResponseRedirect(reverse('cardbox:collection',
                                        args=[collection.id]))


@login_required(login_url=LOGIN_URL)
def delete_collection(request, collection_id):
    collection = get_object_or_404(Collection, pk=collection_id)
    if request.user == collection.owner:
        collection.delete()
        messages.add_message(request, messages.SUCCESS,
                             'Collection {0} successfully deleted.'
                             .format(collection.name))
        return HttpResponseRedirect(reverse('cardbox:index'))
    else:
        raise Http404('Collection not found.')



@login_required(login_url=LOGIN_URL)
def add_collection_entry(request, collection_id):
    collection = get_object_or_404(Collection, pk=collection_id)
    if (not request.user == collection.creator or
        not request.user in collection.editors):
        raise Http404('Collection not found.')

    return render(request, 'cardbox/welcome.html')
