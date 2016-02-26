# django-cardbox -- A collection manager for Magic: The Gathering
# Copyright (C) 2016 Benedikt Rascher-Friesenhausen
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import F
from django.db.utils import IntegrityError
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, get_list_or_404, render
from django.utils import timezone
from django_ajax.decorators import ajax
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from cardbox.models import (
    Set,
    Card,
    CardEdition,
    Collection,
    CollectionEntry,
)

from cardbox.utils.auth import (
    can_edit_collection,
    can_view_collection,
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
    filter_cards_by_blocks_sets,
)


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
    errors = {}
    fstr_name = request.GET.get('fna', '')
    fstr_types = request.GET.get('fty', '')
    fstr_rules = request.GET.get('fru', '')
    fstr_flavour = request.GET.get('ffl', '')
    fstr_mana = request.GET.get('fma', '')
    fstr_power = request.GET.get('fpo', '')
    fstr_toughness = request.GET.get('fto', '')
    fstr_loyalty = request.GET.get('flo', '')
    fstr_cmc = request.GET.get('fcm', '')
    fstr_artist = request.GET.get('far', '')
    fstr_rarity = request.GET.get('fra', '')
    fstr_format = request.GET.get('ffo', '')
    fstr_multi_type = request.GET.get('fmt', '')
    fstr_block_sets = request.GET.get('fbs', '')

    filtered, errors['fna'] = filter_cards_by_name(filtered, fstr_name)
    filtered, errors['fty'] = filter_cards_by_types(filtered, fstr_types)
    filtered, errors['fru'] = filter_cards_by_rules(filtered, fstr_rules)
    filtered, errors['ffl'] = filter_cards_by_flavour(filtered, fstr_flavour)
    filtered, errors['fma'] = filter_cards_by_mana(filtered, fstr_mana)
    filtered, errors['fpo'] = filter_cards_by_power(filtered, fstr_power)
    filtered, errors['fto'] = filter_cards_by_toughness(filtered, fstr_toughness)
    filtered, errors['flo'] = filter_cards_by_loyalty(filtered, fstr_loyalty)
    filtered, errors['fcm'] = filter_cards_by_cmc(filtered, fstr_cmc)
    filtered, errors['far'] = filter_cards_by_artist(filtered, fstr_artist)
    filtered, errors['fra'] = filter_cards_by_rarity(filtered, fstr_rarity)
    filtered, errors['ffo'] = filter_cards_by_format(filtered, fstr_format)
    filtered, errors['fmt'] = filter_cards_by_multi_type(filtered, fstr_multi_type)
    filtered, errors['fbs'] = filter_cards_by_blocks_sets(filtered, fstr_block_sets)

    return filtered.distinct(), errors


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
                         "You were successfully logged out.")
    return HttpResponseRedirect(reverse('cardbox:index'))


def cards(request):
    layout = request.GET.get('layout', 'list')
    if layout not in ['list', 'grid']:
        layout = 'list'

    card_list, ferrors = _filter_cards(request, Card.objects.all())
    paginator = Paginator(card_list, 30, request=request)

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
        'ferrors': ferrors,
    })


def card(request, card_id):
    card = get_object_or_404(Card, pk=card_id)
    editions = get_list_or_404(CardEdition, card=card)
    return render(request, 'cardbox/card_detail.html', {
        'card': card,
        'editions': editions,
        'legality': card.get_legality(),
    })


@login_required
def collection(request, collection_id):
    collection = get_object_or_404(Collection, pk=collection_id)
    if not can_view_collection(request.user, collection):
        raise PermissionDenied

    card_list = Card.objects.filter(editions__collection__id=collection_id)
    card_list, ferrors = _filter_cards(request, card_list)
    list_entries = [(*card.get_count_in_collection(collection_id),
                     card) for card in card_list]

    paginator = Paginator(list_entries, 30, request=request)

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
        'ferrors': ferrors,
    })


@login_required
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
                raise PermissionDenied("You are not the owner of this collection.")
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


@login_required
def delete_collection(request, collection_id):
    collection = get_object_or_404(Collection, pk=collection_id)
    if request.user == collection.owner:
        collection.delete()
        messages.add_message(request, messages.SUCCESS,
                             'Collection {0} successfully deleted.'
                             .format(collection.name))
        return HttpResponseRedirect(reverse('cardbox:index'))
    else:
        raise PermissionDenied("You are not the owner of this collection.")


@login_required
def add_collection_entry(request, collection_id):
    collection = get_object_or_404(Collection, pk=collection_id)
    data = {'collection': collection}
    if not can_edit_collection(request.user, collection):
        raise PermissionDenied("You don't have permission to edit this collection.")

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


@ajax
@login_required
def update_collection_entries(request, collection_id):
    collection = get_object_or_404(Collection, pk=collection_id)
    if not can_edit_collection(request.user, collection):
        raise PermissionDenied("You don't have permission to edit this collection.")
    entry_ids = request.POST.getlist('entryID', [])
    edition_ids = request.POST.getlist('editionID', [])
    counts = request.POST.getlist('count', [])
    fcounts = request.POST.getlist('fcount', [])

    if not (len(entry_ids) == len(counts) == len(fcounts) == len(edition_ids)):
        return HttpResponse("Invalid data", status=400)

    for i, entry_id in enumerate(entry_ids):
        # Ensure that counts[i] and fcounts[i] are numbers to prevent
        # errors when inserting them into the database.
        try:
            if counts[i] is None or counts[i] == 'None':
                count = 0
            else:
                count = int(counts[i])
            if fcounts[i] is None or fcounts[i] == 'None':
                fcount = 0
            else:
                fcount = int(fcounts[i])
        except ValueError:
            return HttpResponse('Invalid data', status=400)

        try:
            entry = CollectionEntry.objects.get(pk=entry_id)
            # The user might have manipulated the entry ids, so we
            # need to check whether or not we are still editing the
            # same collection.
            if collection != entry.collection:
                raise PermissionDenied("You don't have permission to edit this collection entry.")
            # Delete unnecessary entries.
            if count == fcount == 0:
                entry.delete()
                continue
        except (CollectionEntry.DoesNotExist, ValueError):
            edition = get_object_or_404(CardEdition, pk=edition_ids[i])
            entry = CollectionEntry(collection=collection, edition=edition)
        entry.count = count
        entry.foil_count = fcount
        try:
            entry.save()
        except IntegrityError:
            return HttpResponse('Invalid data', status=400)


@ajax
@login_required
def collection_entries(request, collection_id, card_id):
    collection = get_object_or_404(Collection, pk=collection_id)
    card = get_object_or_404(Card, pk=card_id)
    if not can_view_collection(request.user, collection):
        raise PermissionDenied("You don't have permission to access this data.")

    editions = CardEdition.objects.filter(card=card)
    entries = []
    for edition in editions:
        try:
            entry = CollectionEntry.objects.get(collection=collection,
                                                edition=edition)
        except CollectionEntry.DoesNotExist:
            entry = CollectionEntry(count=0, foil_count=0)
        entries.append((edition, entry))
    # data = {
    #     'inner-fragments': {
    #         '#entryTable': render(request, 'cardbox/collection_entry_table.html', {
    #             'card': card,
    #             'collection': collection,
    #             'entries': entries,
    #         }),
    #     }
    # }
    return render(request, 'cardbox/collection_entry_table.html', {
        'card': card,
        'collection': collection,
        'entries': entries,
    })


@login_required
def collection_card(request, collection_id, card_id):
    collection = get_object_or_404(Collection, pk=collection_id)
    card = get_object_or_404(Card, pk=card_id)
    entries = CollectionEntry.objects.filter(collection__id=collection_id,
                                             edition__card__id=card_id)
    if not can_view_collection(request.user, collection):
        raise PermissionDenied("You don't have permission to access this page.")
    if entries is None:
        return Http404('Card {0} is not in the collection {1}'
                       .format(card.name, collection.name))

    return render(request, 'cardbox/card_detail.html', {
        'collection': collection,
        'card': card,
        'entries': entries,
        'legality': card.get_legality(),
    })
