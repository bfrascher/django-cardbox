import os
import pytest

from django.db import connection

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
    _tokenise_special_mana,
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
            Card(name='Mana card 2', types='Mana test', cmc=6),
            Artist(first_name='Some', last_name='Artist'),
            [],
            'XX{2/W}{BP}{BP}',
        ),
        (
            CardEdition(number=3, number_suffix='',
                        rarity=CardEdition.RARITY_UNCOMMON),
            Card(name='Mana card 3', types='Mana test', cmc=5),
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


@pytest.mark.parametrize("mana,tokens", [
    ('XX{BP}', {'X': 2, '{BP}': 1}),
    ('{2/U}{2/W}{2/W}{BP}XXX{5/BBB}', {'{2/U}': 1, '{2/W}': 2, '{BP}': 1, 'X': 3, '{5/BBB}': 1}),
])
def test__tokenise_special_mana(mana, tokens):
    t = _tokenise_special_mana(mana)
    assert t == tokens


@pytest.mark.django_db
@pytest.mark.parametrize("mana,cmc,op,count", [
    ('1UB', 3, '>=', 2),
    ('XX{2/W}{BP}', 5, '=', 1),
    ('{BP}{BP}', 2, '<=', 2),
    ('{BP}{BP}', 6, '<', 1),
    ('XX{2/W}{BP}', 5, '>=', 2),
    ('XX{2/W}{BP}', 5, '>', 1),
])
def test_filter_cards_by_mana(mana, cmc, op, count):
    insert_blocks_sets_cards_from_parser(parser=MockParser)
    print(Card.objects.all().count())
    queryset = filter_cards_by_mana(Card.objects, mana, cmc, op)
    assert queryset.count() == count
