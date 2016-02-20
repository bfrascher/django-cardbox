import collections

from django.db.models import Q

from cardbox.models import (
    Card
)


def filter_cards_by_name(queryset, name, method='icontains'):
    """Filter cards by name.

    :param queryset: The card queryset to filter.

    :param str name: The name to filter for.

    :param str method: (optional) The method to filter with.
        Available: 'icontains', 'exact', 'regex'.

    :returns: The filtered queryset.

    """
    if name is None or name == '':
        return queryset
    if method == 'exact':
        return queryset.filter(name=name)
    if method == 'regex':
        return queryset.filter(name__regex=name)
    return queryset.filter(name__icontains=name)


# TODO(benedikt) Rework
def filter_cards_by_types(queryset, types, op_and=True):
    """Filter cards by type.

    :param queryset: The card queryset to filter.

    :param str types: A string containing different types to filter
        for.

    :param bool op_and: (optional) If ``True`` a card has to have
        satisfy all given types.  Otherwise a card only has to satisfy
        one of the given types.

    """
    if types is None or types == '':
        return queryset
    q = Q()
    for t in types:
        if op_and:
            q = q & Q(types__icontains=t)
        else:
            q = q | Q(types__icontains=t)

    return queryset.filter(q)


def filter_cards_by_rules(queryset, rules):
    """Filter cards by rules text."""
    return queryset.filter(rules__icontains=rules)


def filter_cards_by_flavour(queryset, flavour):
    """Filter cards by flavour text."""
    return queryset.filter(rules__icontains=flavour)


# TODO(benedikt) Implement
def filter_cards_by_multi_type(queryset):
    return queryset


# TODO(benedikt) Implement
def filter_cards_by_colour(queryset):
    return queryset


def filter_cards_by_format(queryset):
    return queryset


def filter_cards_by_artist(queryset):
    return queryset


def filter_cards_by_mana(queryset, mana, op='='):
    return queryset


def filter_cards_by_cmc(queryset, cmc, op='='):
    if cmc is None:
        return queryset
    if op == '=':
        return queryset.filter(cmc=cmc)
    if op == '>=':
        return queryset.filter(cmc__gte=cmc)
    if op == '<=':
        return queryset.filter(cmc_lte=cmc)
    if op == '>':
        return queryset.filter(cmc__gt=cmc)
    if op == '<':
        return queryset.filter(cmc__lt=cmc)
    raise ValueError("Unknown operator '{0}'.".format(op))


def filter_cards_by_rarity(queryset):
    return queryset


def filter_cards_by_power(queryset, power, op='='):
    if power is None:
        return queryset
    if op == '=':
        return queryset.filter(power=power)
    if op == '>=':
        return queryset.filter(power__gte=power)
    if op == '<=':
        return queryset.filter(power_lte=power)
    if op == '>':
        return queryset.filter(power__gt=power)
    if op == '<':
        return queryset.filter(power__lt=power)
    raise ValueError("Unknown operator '{0}'.".format(op))


def filter_cards_by_toughness(queryset, toughness, op='='):
    if toughness is None:
        return queryset
    if op == '=':
        return queryset.filter(toughness=toughness)
    if op == '>=':
        return queryset.filter(toughness__gte=toughness)
    if op == '<=':
        return queryset.filter(toughness_lte=toughness)
    if op == '>':
        return queryset.filter(toughness__gt=toughness)
    if op == '<':
        return queryset.filter(toughness__lt=toughness)
    raise ValueError("Unknown operator '{0}'.".format(op))


def filter_cards_by_loyalty(queryset, loyalty, op='='):
    if loyalty is None:
        return queryset
    if op == '=':
        return queryset.filter(loyalty=loyalty)
    if op == '>=':
        return queryset.filter(loyalty__gte=loyalty)
    if op == '<=':
        return queryset.filter(loyalty_lte=loyalty)
    if op == '>':
        return queryset.filter(loyalty__gt=loyalty)
    if op == '<':
        return queryset.filter(loyalty__lt=loyalty)
    raise ValueError("Unknown operator '{0}'.".format(op))


def filter_cards_by_sets(queryset, codes):
    """Filter cards by sets.

    :param queryset: The cards to filter.

    :type codes: list or tuple
    :param codes: A list of set codes to filter for.  If a card
        belongs to any of the sets, it will be included.

    :returns: The filtered cards.
    """
    if not (isinstance(codes, list) or isinstance(codes, tuple)):
        return queryset
    q = Q()
    for code in codes:
        q = q | Q(editions__mtgset__code=code.upper())
    return queryset.filter(q)
