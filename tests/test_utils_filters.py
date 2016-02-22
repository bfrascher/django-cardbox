import pytest

from django.db.models import Q

from cardbox.models import (
    Artist,
    Block,
    Set,
    Card,
    CardEdition,
)

from cardbox.utils.db import (
    insert_blocks_sets_cards_from_parser,
)

from cardbox.utils.filters import (
    _tokenise_filter_string,
    _build_q_atom,
    _build_q_expr,
    _tokenise_special_mana,
    _guess_cmc,
    _q_builder_default,
    _q_builder_choice,
    filter_cards_by_mana,
)


class MockParser:
    blocks = [
        Block(name='Mana block', category=Block.CATEGORY_MTGO),
    ]

    sets = {}
    sets['Mana block'] = [
        Set(code='MS', name='Mana set'),
    ]

    setentries = {}
    setentries['MS'] = [
        (
            CardEdition(number=1, number_suffix='',
                        rarity=CardEdition.RARITY_UNCOMMON),
            Card(name='Mana card 1', types='Mana test', cmc=8),
            Artist(first_name='Some', last_name='Artist'),
            [],
            '3WUBRG',
        ),
        (
            CardEdition(number=2, number_suffix='',
                        rarity=CardEdition.RARITY_UNCOMMON),
            Card(name='Mana card 2', types='Mana test', cmc=4),
            Artist(first_name='Some', last_name='Artist'),
            [],
            'XX{2/W}{BP}{BP}',
        ),
        (
            CardEdition(number=3, number_suffix='',
                        rarity=CardEdition.RARITY_UNCOMMON),
            Card(name='Mana card 3', types='Mana test', cmc=3),
            Artist(first_name='Some', last_name='Artist'),
            [],
            'XX{2/W}{BP}',
        ),
        (
            CardEdition(number=4, number_suffix='',
                        rarity=CardEdition.RARITY_UNCOMMON),
            Card(name='Mana card 4', types='Mana test', cmc=5),
            Artist(first_name='Some', last_name='Artist'),
            [],
            '1UBBB',
        ),
    ]

    def parse_blocks_sets():
        for block in MockParser.blocks:
            yield block, MockParser.sets[block.name]

    def parse_cards_by_set(setcode):
        for edition, card, artist, rulings, mana in MockParser.setentries[setcode]:
            card.set_mana(mana)
            yield edition, card, artist, rulings


@pytest.mark.parametrize("fstr,fieldname,unop,binop_default,unop_default,q_e", [
    ('Sphinx & ~ ~(>=Pro "Sphinx of the")', 'name', None, '&', '', Q(name__icontains='Sphinx') & (Q(name__gte='Pro') & Q(name__contains='Sphinx of the'))),
    (r"='Sphinx\'s Revelation' | ~Sphinx", 'name', None, '&', '', Q(name="Sphinx's Revelation") | ~Q(name__icontains='Sphinx')),
    (r'=Instant = Sorcery | (Legendary & (Artifact | Creature))', 'types', None, '|', '', Q(types='Instant') | Q(types='Sorcery') | (Q(types__icontains='Legendary') & (Q(types__icontains='Artifact') | Q(types__icontains='Creature')))),
    ('>=2 <4', 'cmc', None, '&', '', Q(cmc__gte='2') & Q(cmc__lt='4')),
    ('(Devoid ingest) | (exile & Planeswalker)', 'rules', None, '&', '', (Q(rules__icontains='Devoid') & Q(rules__icontains='ingest')) | (Q(rules__icontains='exile') & Q(rules__icontains='Planeswalker'))),
])
def test__q_builder_default(fstr, fieldname, unop, binop_default,
                            unop_default, q_e):
    ftokens, error = _tokenise_filter_string(fstr)
    print(ftokens)
    assert error is None
    q = _q_builder_default(ftokens, fieldname, unop, binop_default,
                           unop_default)
    print(q)
    print(q_e)
    assert str(q) == str(q_e)


@pytest.mark.parametrize("fstr,fieldname,unop,binop_default,unop_default,q_e", [
    ('=M', 'editions__rarity', None, '&', '=', Q(editions__rarity='M')),
])
def test__q_builder_choice(fstr, fieldname, unop, binop_default,
                           unop_default, q_e):
    ftokens, error = _tokenise_filter_string(fstr)
    assert error is None
    q = _q_builder_choice(ftokens, fieldname, unop, binop_default,
                          unop_default)
    print(q)
    print(q_e)
    assert str(q) == str(q_e)


@pytest.mark.parametrize("mana,tokens", [
    ('XX{BP}', {'X': 2, '{BP}': 1}),
    ('{2/U}{2/W}{2/W}{BP}XXX{5/BBB}', {'{2/U}': 1, '{2/W}': 2, '{BP}': 1, 'X': 3, '{5/BBB}': 1}),
])
def test__tokenise_special_mana(mana, tokens):
    t = _tokenise_special_mana(mana)
    assert t == tokens


@pytest.mark.parametrize("mana,cmc", [
    ('3WUCC', 7),
    ('{2/U}XXX', 2),
    ('{BP}{BP}', 2),
    ('4WW{2/G}XXXXX{R/21}', 29),
])
def test__guess_cmc(mana, cmc):
    n, w, u, b, r, g, c, s = Card.parse_mana(mana)
    tokens = _tokenise_special_mana(s)
    assert _guess_cmc(n, w, u , b, r, g, c, tokens) == cmc


# @pytest.mark.django_db
# @pytest.mark.parametrize("mana,op,count", [
#     ('1UB', '>=', 2),
#     ('XX{2/W}{BP}', '=', 1),
#     ('2{BP}{BP}', '<=', 2),
#     ('2{BP}{BP}', '<', 1),
#     ('XX{2/W}{BP}', '>=', 2),
#     ('XX{2/W}{BP}', '>', 1),
# ])
# def test_filter_cards_by_mana(mana, op, count):
#     insert_blocks_sets_cards_from_parser(parser=MockParser)
#     queryset = filter_cards_by_mana(Card.objects, mana, op)
#     assert queryset.count() == count
