import pyparsing as pp
import re

from django.db.models import Q, F
from django.db.utils import DataError

from cardbox.models import (
    Card
)


NOT = '~'
UNOPS = {
    '<=': '__lte',
    '>=': '__gte',
    '<': '__lt',
    '>': '__gt',
    '=': '',
    '': '__icontains',
}
BINOPS = ['&', '|']


fg_not = pp.Literal(NOT).setResultsName('not')
fg_word = pp.Word(pp.alphanums + '*/{}+-\'').setResultsName('word')
fg_binop = pp.oneOf(BINOPS).setResultsName('binop')
fg_unop = pp.oneOf(list(UNOPS.keys())).setResultsName('unop')
fg_regex = pp.Or([pp.QuotedString("r'", endQuoteChar="'", escChar='\\'),
                  pp.QuotedString('r"', endQuoteChar='"', escChar='\\')]).setResultsName('regex')
fg_literal = pp.Or([pp.QuotedString("'", escChar='\\'),
                    pp.QuotedString('"', escChar='\\')]).setResultsName('literal')
fg_atom = pp.Optional(fg_unop) + (fg_regex ^ fg_literal ^ fg_word)
fg_expr_part = pp.ZeroOrMore(pp.Group(fg_not)) + pp.Group(fg_atom) + pp.Optional(pp.Group(fg_binop))
fg_expr = pp.OneOrMore(fg_expr_part)
fg_nested = pp.nestedExpr(content=fg_expr)
fg_syntax_part = pp.ZeroOrMore(pp.Group(fg_not)) + (pp.Group(fg_atom) ^ fg_nested) + pp.Optional(pp.Group(fg_binop))
fg_syntax = pp.OneOrMore(fg_syntax_part)


def _tokenise_filter_string(fstr):
    ftokens = None
    error = None
    try:
        # ftokens = fg_expr.parseString(fstr)
        ftokens = fg_syntax.parseString(fstr)
    except (pp.ParseException, pp.ParseFatalException):
        error = 'has-error'
    return ftokens, error


def _build_q_atom(ftokens, fieldname, q_builder,
                  binop_default='&', unop_default=''):
    """Build a Q object from scratch."""
    binop = binop_default
    unop = unop_default
    negate = False
    for ft in ftokens:
        # Binary operators are in their own group.
        if 'binop' in ft.keys():
            binop = ft.binop
            continue

        # The not operator is in it's own group.
        if 'not' in ft.keys():
            # Flip negate so that multiple negations can cancel each
            # other out.
            negate ^= True
            continue

        # From here on out we are handling a fg_bin or fg_nested
        # match.
        if 'unop' in ft.keys():
            unop = ft.unop

        q = q_builder(ft, fieldname, unop, binop_default,
                      unop_default)

        if negate:
            q = ~q

        yield binop, q

        # Prevent current values from affecting the next
        # fg_bin/fg_nested.
        binop = binop_default
        unop = unop_default
        negate = False


def _build_q_expr(ftokens, fieldname, q_builder,
                  binop_default='&', unop_default=''):
    """Combine Q objects from atoms."""
    q = Q()
    for binop, p in _build_q_atom(ftokens, fieldname, q_builder,
                                  binop_default, unop_default):
        if q:
            if binop == '|':
                q = q | p
            else:
                q = q & p
        # Avoid empty Q objects in q.
        else:
            q = p

    return q


def _q_builder_default(ft, fieldname, unop, binop_default, unop_default):
    """The default query builder.

    Used for Card.name, Card.types, Card.rules, Card.flavour,
    Card.rulings and Card.cmc.

    """
    if 'word' in ft.keys():
        p = Q(**{fieldname + UNOPS[unop]: ft.word})
    elif 'literal' in ft.keys():
        # Use case sensitive contains instead of icontains.
        if UNOPS[unop] == '__icontains':
            lookup = '__contains'
        else:
            lookup = UNOPS[unop]
        p = Q(**{fieldname + lookup: ft.literal})
    elif 'regex' in ft.keys():
        p = Q(**{fieldname + '__regex': ft.regex})
    else:
        # Neither binop, unop, word, literal nor regex are keys in ft.
        # Therefore ft has to be a nested expression.
        p = _build_q_expr(ft, fieldname, _q_builder_default,
                          binop_default, unop_default)
    return p


def _q_builder_format(ft, fieldname, unop, binop_default,
                           unop_default):
    """Build a Q object to filter formats."""
    if 'word' in ft.keys():
        if ft.word.lower() not in ['vintage', 'legacy', 'extended',
                           'standard', 'classic', 'commander', 'modern']:
            raise ValueError("Unknown format '{0}'.".format(ft.word))
        p = Q(**{'legal_' + ft.word.lower(): Card.LEGALITY_LEGAL})
    elif 'literal' in ft.keys():
        raise KeyError('literals are not supported by this filter.')
    elif 'regex' in ft.keys():
        raise KeyError('regex are not supported by this filter.')
    else:
        # Neither binop, unop, word, literal nor regex are keys in ft.
        # Therefore ft has to be a nested expression.
        p = _build_q_expr(ft, fieldname, _q_builder_format,
                          binop_default, unop_default)
    return p


def _q_builder_choice(ft, fieldname, unop, binop_default, unop_default):
    """Build a Q object for a CharField with choices.

    Used for Card.editions.rarity and Card.multi_type.
    """
    if 'word' in ft.keys():
        p = Q(**{fieldname + UNOPS[unop]: ft.word})
    elif 'literal' in ft.keys():
        raise KeyError('literal has no meaning for {0}'.format(fieldname))
    elif 'regex' in ft.keys():
        raise KeyError('regex has no meaning for {0}'.format(fieldname))
    else:
        # Neither binop, unop, word, literal nor regex are keys in ft.
        # Therefore ft has to be a nested expression.
        p = _build_q_expr(ft, fieldname, _q_builder_choice,
                          binop_default, unop_default)
    return p


# TODO(benedikt) Fix this function
def _q_builder_mana(ft, fieldname, unop, binop_default, unop_default):
    """Build a Q object to filter mana."""
    if 'word' in ft.keys():
        mana = {}
        (mana['n'], mana['w'], mana['u'], mana['b'], mana['r'],
         mana['g'], mana['c'], s) = Card.parse_mana(ft.word)
        mts = _tokenise_special_mana(s)
        cmc = _guess_cmc(mana['n'], mana['w'], mana['u'], mana['b'],
                         mana['r'], mana['g'], mana['c'], mts)

        p = Q()
        if '>' in unop:
            for mt in mts:
                p = p & Q(mana_special__icontains=mts[mt]*mt)
            for colour in ['n', 'w', 'u', 'b', 'r', 'g', 'c']:
                p = p & Q(**{'mana_' + colour + '__lte': mana[colour]})
        elif '<' in unop:
            for mt in mts:
                p = p & ~Q(mana_special__icontains=(mts[mt]+1)*mt)
            for colour in ['n', 'w', 'u', 'b', 'r', 'g', 'c']:
                p = p & Q(**{'mana_' + colour + '__gte': mana[colour]})
        else:
            p = Q(mana_special=s)
            for colour in ['n', 'w', 'u', 'b', 'r', 'g', 'c']:
                p = p & Q(**{'mana_' + colour: mana[colour]})

        lookup = UNOPS[unop]
        # __icontains is not supported for an IntegerField.
        if lookup == '__icontains':
            lookup = ''
        p = p & Q(**{'cmc' + lookup: cmc})
    elif 'literal' in ft.keys():
        raise KeyError('literals are not supported for filtering mana.')
    elif 'regex' in ft.keys():
        raise KeyError('regex are not supported for filtering mana.')
    else:
        # Neither binop, unop, word, literal nor regex are keys in ft.
        # Therefore ft has to be a nested expression.
        p = _build_q_expr(ft, fieldname, _q_builder_mana,
                          binop_default, unop_default)
    return p


def _q_builder_ptl(ft, fieldname, unop, binop_default, unop_default):
    """Build a Q object to filter power/toughness/loyalty."""
    if 'word' in ft.keys():
        if ft.word in ['cmc', 'power', 'toughness', 'loyalty']:
            lookup = UNOPS[unop]
            # F expressions don't allow __icontains lookups.
            if lookup == '__icontains':
                lookup = ''
            p = Q(**{fieldname + lookup: F(ft.word)})
        else:
            try:
                p = Q(**{fieldname + UNOPS[unop]: int(ft.word)})
            except ValueError:
                p = Q(**{fieldname + '_special' + UNOPS[unop]: ft.word})
    elif 'literal' in ft.keys():
        lookup = UNOPS[unop]
        if lookup == '__icontains':
            lookup = '__contains'
        try:
            p = Q(**{fieldname + lookup: int(ft.literal)})
        except ValueError:
            p = Q(**{fieldname + '_special' + lookup: ft.literal})
    elif 'regex' in ft.keys():
        p = (Q(**{fieldname + '__regex': ft.regex}) |
             Q(**{fieldname + '_special__regex': ft.regex}))
    else:
        # Neither binop, unop, word, literal nor regex are keys in ft.
        # Therefore ft has to be a nested expression.
        p = _build_q_expr(ft, fieldname, _q_builder_ptl,
                          binop_default, unop_default)
    return p


def _q_builder_blocks_sets(ft, fieldname, unop, binop_default,
                           unop_default):
    """Build a Q object to filter blocks and sets."""
    if 'word' in ft.keys():
        p = (Q(**{'editions__mtgset__name' + UNOPS[unop]: ft.word}) |
             Q(**{'editions__mtgset__code' + UNOPS[unop]: ft.word}) |
             Q(**{'editions__mtgset__block__name' + UNOPS[unop]: ft.word}))
    elif 'literal' in ft.keys():
        lookup = UNOPS[unop]
        if lookup == '__icontains':
            lookup = '__contains'
        p = (Q(**{'editions__mtgset__name' + lookup: ft.literal}) |
             Q(**{'editions__mtgset__code' + lookup: ft.literal}) |
             Q(**{'editions__mtgset__block__name' + lookup: ft.literal}))
    elif 'regex' in ft.keys():
        p = (Q(**{'editions__mtgset__name__regex': ft.regex}) |
             Q(**{'editions__mtgset__code__regex': ft.regex}) |
             Q(**{'editions__mtgset__block__name__regex': ft.regex}))
    else:
        # Neither binop, unop, word, literal nor regex are keys in ft.
        # Therefore ft has to be a nested expression.
        p = _build_q_expr(ft, fieldname, _q_builder_blocks_sets,
                          binop_default, unop_default)
    return p


def _tokenise_special_mana(special_mana):
    """Return the different mana symbols and their count.

    This function expects all mana of the same symbol to be in one
    block (as is the standard with MTG):

       good: XX{BP}, {2/W}{2/W}{B/W}X
       bad: X{BP}X, {2/W}X{2/W}{B/W}

    :param str special_mana: A string containing special mana symbols.

    :rtype: dict
    :returns: A dictionary whose keys are a single mana symbols at the
        value of that key is the number of occurances of this mana
        symbol in `special_mana`.

    """
    regex = re.compile(r'(X|\{.*?\})\1*')
    tokens = {}
    while special_mana != '':
        match = regex.search(special_mana)
        if match is None:
            # TODO(benedikt) Better error handling
            break
        tokens[match.group(1)] = match.group(0).count(match.group(1))
        special_mana = special_mana[match.end():]
    return tokens


def _guess_cmc(n, w, u, b, r, g, c, tokens):
    """Guess the converted mana cost."""
    cmc = n + w + u + b + r + g + c
    if tokens is not None and len(tokens) > 0:
        regex = re.compile(r'\d+')
        for token in tokens:
            # - X does not contribute to cmc
            # - {[WUBRGC]P} counts as 1 mana
            # - {\d+/[WUBRGC]} counts as \d+ mana
            # - {[WUBRGC/WUBRGC]} counts as 1 mana
            if token == 'X':
                continue
            match = regex.search(token)
            if match:
                cmc += int(match.group(0))*tokens[token]
            else:
                cmc += tokens[token]
    return cmc


def _filter_by_field(queryset, fstr, fieldname, q_builder,
                     binop_default='&', unop_default=''):
    """Filter cards by field."""
    if fstr is None or fstr == '':
        return queryset, None
    ftokens, error = _tokenise_filter_string(fstr)
    if error is not None:
        return queryset, error
    try:
        q = _build_q_expr(ftokens, fieldname, q_builder,
                          binop_default, unop_default)
    except (ValueError, KeyError):
        return queryset, 'has-warning'
    try:
        filtered = queryset.filter(q)
    except (ValueError, DataError):
        return queryset, 'has-error'
    return filtered, None


def filter_cards_by_name(queryset, fstr):
    """Filter cards by name."""
    return _filter_by_field(queryset, fstr, 'name',
                            _q_builder_default)


def filter_cards_by_types(queryset, fstr):
    """Filter cards by type."""
    return _filter_by_field(queryset, fstr, 'types',
                            _q_builder_default)


def filter_cards_by_rules(queryset, fstr):
    """Filter cards by rules text."""
    return _filter_by_field(queryset, fstr, 'rules',
                            _q_builder_default)


def filter_cards_by_flavour(queryset, fstr):
    """Filter cards by flavour text."""
    return _filter_by_field(queryset, fstr, 'flavour',
                            _q_builder_default)


def filter_cards_by_rulings(queryset, fstr):
    """Filter cards by rulings text."""
    return _filter_by_field(queryset, fstr, 'rulings__ruling',
                            _q_builder_default)


def filter_cards_by_cmc(queryset, fstr):
    """Filter cards by converted mana cost."""
    return _filter_by_field(queryset, fstr, 'cmc', _q_builder_default)


def filter_cards_by_multi_type(queryset, fstr):
    """Filter cards by multy type."""
    return _filter_by_field(queryset, fstr, 'multi_type',
                            _q_builder_choice, binop_default='|',
                            unop_default='=')


def filter_cards_by_mana(queryset, fstr):
    """Filter cards by mana."""
    return _filter_by_field(queryset, fstr, None, _q_builder_mana,
                            unop_default='=')

    # n, w, u, b, r, g, c, s = Card.parse_mana(mana)
    # tokens = _tokenise_special_mana(s)
    # cmc = _guess_cmc(n, w, u, b, r, g, c, tokens)
    # q = Q()
    # if '>' in op:
    #     for token in tokens:
    #         q = q & Q(mana_special__icontains=tokens[token]*token)
    # elif '<' in op:
    #     for token in tokens:
    #         q = q & ~Q(mana_special__icontains=(tokens[token]+1)*token)

    # if op == '=':
    #     return queryset.filter(mana_n=n, mana_w=w, mana_u=u, mana_b=b,
    #                            mana_r=r, mana_g=g, mana_c=c, mana_special=s), None
    # if op == '>=':
    #     return queryset.filter(q, mana_n__gte=n, mana_w__gte=w, mana_u__gte=u,
    #                            mana_b__gte=b, mana_r__gte=r, mana_g__gte=g,
    #                            mana_c__gte=c, cmc__gte=cmc), None
    # if op == '<=':
    #     # return queryset.filter(q, mana_n__lte=n, mana_w__lte=w, mana_u__lte=u,
    #     #                        mana_b__lte=b, mana_r__lte=r, mana_g__lte=g,
    #     #                        mana_c__lte=c, cmc__lte=cmc)
    #     return (queryset.filter(q).filter(mana_n__lte=n).filter(mana_w__lte=w)
    #             .filter(mana_u__lte=u).filter(mana_b__lte=b)
    #             .filter(mana_r__lte=r).filter(mana_g__lte=g)
    #             .filter(mana_c__lte=c).filter(cmc__lte=cmc)), None
    # if op == '>':
    #     return queryset.filter(q, mana_n__gte=n, mana_w__gte=w, mana_u__gte=u,
    #                            mana_b__gte=b, mana_r__gte=r, mana_g__gte=g,
    #                            mana_c__gte=c, cmc__gt=cmc), None
    # if op == '<':
    #     return queryset.filter(q, mana_n__lte=n, mana_w__lte=w, mana_u__lte=u,
    #                            mana_b__lte=b, mana_r__lte=r, mana_g__lte=g,
    #                            mana_c__lte=c, cmc__lt=cmc), None
    # raise ValueError("Unknown operator '{0}'.".format(op))


def filter_cards_by_power(queryset, fstr):
    """Filter cards by power."""
    return _filter_by_field(queryset, fstr, 'power', _q_builder_ptl)


def filter_cards_by_toughness(queryset, fstr):
    """Filter cards by toughness."""
    return _filter_by_field(queryset, fstr, 'toughness', _q_builder_ptl)


def filter_cards_by_loyalty(queryset, fstr):
    """Filter cards by loyalty."""
    return _filter_by_field(queryset, fstr, 'loyalty', _q_builder_ptl)


def filter_cards_by_blocks_sets(queryset, fstr):
    """Filter cards by sets."""
    return _filter_by_field(queryset, fstr, None,
                            _q_builder_blocks_sets, binop_default='|')


def filter_cards_by_format(queryset, fstr):
    """Filter cards by format."""
    return _filter_by_field(queryset, fstr, None, _q_builder_format,
                            binop_default='|', unop_default='=')


def filter_cards_by_artist(queryset, fstr):
    """Filter cards by artist."""
    return _filter_by_field(queryset, fstr,
                            'editions__artist__name',
                            _q_builder_default)


def filter_cards_by_rarity(queryset, fstr):
    """Filter cards by rarity."""
    if fstr is None or fstr == '':
        return queryset, None
    ftokens, error = _tokenise_filter_string(fstr)
    if error is not None:
        return queryset, error
    # In _q_builder_choice literal and regex inputs raise a KeyError
    # since they don't really work on a CharField of length one.
    try:
        q_atoms = list(_build_q_atom(
            ftokens, 'editions__rarity', _q_builder_choice,
            binop_default='|', unop_default='='))
    except (KeyError, ValueError):
        return queryset, 'has-warning'

    filtered = queryset
    q = Q()
    # If we combine two Q objects with & the result will only match a
    # card which field matches both expressions.  Since a single
    # rarity field on a CardEdition can't match two different
    # rarities, but a card can have different editions with different
    # rarities, we have to apply one Q object after the other (when
    # trying to combine them with &).  This way the previous filtered
    # cards are filtered further.  Combinations with | are handled as
    # usual.
    for binop, p in q_atoms:
        if binop == '&':
            try:
                filtered = filtered.filter(q)
            except (ValueError, DataError):
                return queryset, 'has-error'
            q = Q()

        if q:
            q = q | p
        else:
            q = p
    try:
        filtered = filtered.filter(q)
    except (ValueError, DataError):
        return queryset, 'has-error'
    return filtered, None
