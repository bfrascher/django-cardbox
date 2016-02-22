from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models import F
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from cardbox.models import (
    Set,
    Card,
    CardEdition,
    Collection,
    CollectionEntry,
)

from cardbox.utils.filters import (
    filter_cards_by_name,
    filter_cards_by_types,
    filter_cards_by_rules,
    filter_cards_by_flavour,
    filter_cards_by_mana,
    filter_cards_by_power,
    filter_cards_by_toughness,
    filter_cards_by_loyalty,
    filter_cards_by_cmc,
    filter_cards_by_artist,
    filter_cards_by_rarity,
    filter_cards_by_format,
    filter_cards_by_multi_type,
    filter_cards_by_sets,
)

LOGIN_URL = '/cardbox/login/'


def _update_many_to_many_field(entries, m2m_manager):
    """Update the entries for a ManyToManyField.

    :param list entries: The entries the ManyToManyField should have
        after the update.

    :param m2m_manager: The model manager.

    """
    for entry in m2m_manager.all():
        if entry not in entries:
            m2m_manager.remove(entry)
    for entry in entries:
        m2m_manager.add(entry)


def _filter_cards(request, queryset):
    """Filter a list of cards.

    :param request: A request object whose POST dictionary contains
        card filters.

    :param queryset: The query set for the cards.

    :returns: A query set for the filtered cards.

    """
    filtered = queryset
    filter_name = request.GET.get('fna', '')
    filter_types = request.GET.get('fty', '')
    filter_rules = request.GET.get('fru', '')
    filter_flavour = request.GET.get('ffl', '')
    filter_mana = request.GET.get('fma', '')
    filter_mana_op = request.GET.get('filterManaOp', '=')
    filter_power = request.GET.get('fpo', '')
    filter_power_op = request.GET.get('filterPowerOp', '=')
    filter_toughness = request.GET.get('fto', '')
    filter_toughness_op = request.GET.get('filterToughnessOp', '=')
    filter_loyalty = request.GET.get('flo', '')
    filter_loyalty_op = request.GET.get('filterLoyaltyOp', '=')
    filter_cmc = request.GET.get('fcm', '')
    filter_cmc_op = request.GET.get('filterCMCOp', '=')
    filter_artist = request.GET.get('far', '')
    filter_rarity = request.GET.get('fra', '')
    filter_format = request.GET.get('ffo', '')
    filter_multi_type = request.GET.get('fmt', '')
    filter_sets = request.GET.getlist('fse', [])

    try:
        filter_power = int(filter_power)
    except ValueError:
        filter_power = None
    try:
        filter_toughness = int(filter_toughness)
    except ValueError:
        filter_toughness = None
    try:
        filter_loyalty = int(filter_loyalty)
    except ValueError:
        filter_loyalty = None
    try:
        filter_cmc = int(filter_cmc)
    except ValueError:
        filter_cmc = None

    filtered = filter_cards_by_name(filtered, filter_name)
    filtered = filter_cards_by_types(filtered, filter_types)
    filtered = filter_cards_by_rules(filtered, filter_rules)
    filtered = filter_cards_by_flavour(filtered, filter_flavour)
    filtered = filter_cards_by_mana(filtered, filter_mana, op=filter_mana_op)
    filtered = filter_cards_by_power(filtered, filter_power, op=filter_power_op)
    filtered = filter_cards_by_toughness(filtered, filter_toughness, op=filter_toughness_op)
    filtered = filter_cards_by_loyalty(filtered, filter_loyalty, op=filter_loyalty_op)
    filtered = filter_cards_by_cmc(filtered, filter_cmc, op=filter_cmc_op)
    filtered = filter_cards_by_artist(filtered, filter_artist)
    filtered = filter_cards_by_rarity(filtered, filter_rarity)
    filtered = filter_cards_by_format(filtered, filter_format)
    filtered = filter_cards_by_multi_type(filtered, filter_multi_type)
    filtered = filter_cards_by_sets(filtered, filter_sets)

    return filtered


def index(request):
    card_list = Card.objects.all()
    paginator = Paginator(card_list, 50, request=request)

    page = request.GET.get('page', 1)
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
            next_url = request.POST.get('next', '')
            if next_url == '':
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


def cards(request):
    layout = request.GET.get('layout', 'list')
    if layout not in ['list', 'grid']:
        layout = 'list'

    card_list = _filter_cards(request, Card.objects)
    paginator = Paginator(card_list, 60, request=request)

    page = request.GET.get('page', 1)
    try:
        cards = paginator.page(page)
    except PageNotAnInteger:
        cards = paginator.page(1)
    except EmptyPage:
        cards = paginator.page(paginator.num_pages)

    return render(request, 'cardbox/cards.html', {
        'cards': cards,
        'get': request.GET,
        'layout': layout,
    })


def card(request, card_id):
    card = get_object_or_404(Card, pk=card_id)
    return render(request, 'cardbox/card_detail.html', {
        'card': card,
    })


@login_required(login_url=LOGIN_URL)
def collection(request, collection_id):
    collection = get_object_or_404(Collection, pk=collection_id)
    if (request.user != collection.owner and
        request.user not in collection.editors.all() and
        request.user not in collection.viewers.all()):
        raise PermissionDenied

    card_list = Card.objects.filter(editions__collection__id=collection_id)
    card_list = _filter_cards(request, card_list)
    list_entries = [(*card.get_count_in_collection(collection_id),
                     card) for card in card_list]

    paginator = Paginator(list_entries, 50, request=request)

    page = request.GET.get('page', 1)
    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
    except EmptyPage:
        entries = paginator.page(paginator.num_pages)

    layout = request.GET.get('layout', 'list')
    if layout not in ['list', 'grid']:
        layout = 'list'

    return render(request, 'cardbox/collection.html', {
        'collection': collection,
        'entries': entries,
        'get': request.GET,
        'layout': layout,
    })


@login_required(login_url=LOGIN_URL)
def edit_collection(request, collection_id=None):
    """Update or create a collection.

    :param int collection_id: (optional) The ID of the collection to
        edit.  Use ``None`` to create a new collection.

    """
    data = {}
    if collection_id is None:
        action = 'created'
        collection = Collection(owner=request.user, date_created=timezone.now())
        data['collection'] = None
    else:
        action = 'updated'
        try:
            collection = Collection.objects.get(pk=collection_id)
            if request.user != collection.owner:
                raise PermissionDenied
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
        if editor == '':
            continue
        try:
            user = User.objects.get(username=editor.strip())
            editors.append(user)
        except User.DoesNotExist:
            messages.add_message(request, messages.WARNING,
                                 'No user with name {0}.'.format(editor))
            return render(request, 'cardbox/edit_collection.html', data)

    viewers = []
    for viewer in viewer_list:
        if viewer == '':
            continue
        try:
            user = User.objects.get(username=viewer.strip())
            viewers.append(user)
        except User.DoesNotExist:
            messages.add_message(request, messages.WARNING,
                                 'No user with name {0}.'.format(viewer))
            return render(request, 'cardbox/edit_collection.html', data)

    collection.name = name
    collection.save()

    _update_many_to_many_field(editors, collection.editors)
    _update_many_to_many_field(viewers, collection.viewers)

    messages.add_message(request, messages.SUCCESS,
                         'Collection {0} successfully {1}.'
                         .format(collection.name, action))

    # Redirect the user to the newly created collection.
    if collection_id is None:
        return HttpResponseRedirect(reverse('cardbox:collection',
                                            args=[collection.id]))
    else:
        # Otherwise allow him to review his settings.
        return HttpResponseRedirect(reverse('cardbox:edit_collection',
                                            args=[collection_id]))


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
        raise PermissionDenied



@login_required(login_url=LOGIN_URL)
def add_collection_entry(request, collection_id):
    collection = get_object_or_404(Collection, pk=collection_id)
    data = {'collection': collection}
    if (request.user != collection.owner and
        request.user not in collection.editors.all()):
        raise PermissionDenied

    try:
        set_str = request.POST['set']
        number_str = request.POST['number']
        count = request.POST.get('count', 0)
        fcount = request.POST.get('fcount', 0)
    except KeyError:
        return render(request, 'cardbox/add_collection_entry.html', data)

    try:
        count = int(count)
    except ValueError:
        count = 0
    try:
        fcount = int(fcount)
    except ValueError:
        fcount = 0

    try:
        set_ = Set.objects.get(code=set_str.upper())
    except Set.DoesNotExist:
        try:
            set_ = Set.objects.get(name=set_str)
        except Set.DoesNotExist:
            messages.add_message(request, messages.WARNING,
                                 "Set '{0}' not found.".format(set_str))
            return render(request, 'cardbox/add_collection_entry.html', data)

    try:
        number, number_suffix = CardEdition.parse_number(number_str)
    except ValueError:
        messages.add_message(request, messages.WARNING,
                             "'{0}' is not a valid set number."
                             .format(number_str))
        return render(request, 'cardbox/add_collection_entry.html', data)

    try:
        edition = CardEdition.objects.get(mtgset=set_, number=number,
                                          number_suffix=number_suffix)
    except CardEdition.DoesNotExist:
        messages.add_message(request, messages.WARNING,
                             "No card with number '{0}' in set '{1}'."
                             .format(number_str, set_))
        return render(request, 'cardbox/add_collection_entry.html', data)

    # If there already exists an entry for this edition we just have
    # to update it.
    try:
        entry = CollectionEntry.objects.get(collection=collection,
                                            edition=edition)
        entry.count = F('count') + count
        entry.foil_count = F('foil_count') + fcount
    except CollectionEntry.DoesNotExist:
        entry = CollectionEntry(collection=collection, edition=edition,
                                count=count, foil_count=fcount)

    entry.save()
    messages.add_message(request, messages.SUCCESS,
                         "{0} ({1}) copies of '{2}' added to '{3}'."
                         .format(count, fcount, edition, collection))
    if 'addanother' == request.POST['button']:
        return HttpResponseRedirect(reverse('cardbox:add_collection_entry',
                                            args=[collection.id]))
    else:
        return HttpResponseRedirect(reverse('cardbox:collection',
                                            args=[collection.id]))


def collection_card(request, collection_id, card_id):
    collection = get_object_or_404(Collection, pk=collection_id)
    card = get_object_or_404(Card, pk=card_id)
    entries = CollectionEntry.objects.filter(collection__id=collection_id,
                                             edition__card__id=card_id)
    if entries is None:
        return Http404('Card {0} is not in the collection {1}'
                       .format(card.name, collection.name))

    return render(request, 'cardbox/collection_card.html', {
        'collection': collection,
        'card': card,
        'entries': entries,
    })
