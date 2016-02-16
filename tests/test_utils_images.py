# coding: utf-8

import os
import pytest

from mtgcardbox.models import (
    Artist,
    Block,
    Set,
    Card,
    CardEdition,
)

from mtgcardbox.utils.db import (
    insert_blocks_sets_cards_from_parser,
)

from mtgcardbox.utils.images import (
    MCIDownloader,
)


class MockParser:
    blocks = [
        Block(name='Test block', category=Block.CATEGORY_NONE),
    ]

    sets = [
        Set(code='ORI', name='Magic Origins'),
        Set(code='DKA', name='Dark Ascension'),
    ]

    setentries = {}
    setentries['ORI'] = [
        (
            CardEdition(number=80, number_suffix='',
                        rarity=CardEdition.RARITY_UNCOMMON),
            Card(name='Tower Geist', types='Creature — Spirit'),
            Artist(first_name='', last_name='Izzy'),
            [],
        ),
        (
            CardEdition(number=60, number_suffix='a',
                        rarity=CardEdition.RARITY_MYTHIC_RARE),
            Card(name="Jace, Vryn's Prodigy",
                 types='Legendary Creature — Human Wizard',
                 multi_type=Card.MULTI_FLIP),
            Artist(first_name='Jaime', last_name='Jones'),
            [],
        ),
        (
            CardEdition(number=60, number_suffix='b',
                        rarity=CardEdition.RARITY_MYTHIC_RARE),
            Card(name='Fire (Song/Ice/Fire)', types='Planeswalker — Jace',
                 multi_type=Card.MULTI_FLIP),
            Artist(first_name='Jaime', last_name='Jones'),
            [],
        ),
        (
            CardEdition(number=261, number_suffix='',
                        rarity=CardEdition.RARITY_LAND),
            Card(name='Swamp', types='Basic Land — Swamp'),
            Artist(first_name='Larry', last_name='Elmore'),
            []
        ),
        (
            CardEdition(number=262, number_suffix='',
                        rarity=CardEdition.RARITY_LAND),
            Card(name='Swamp', types='Basic Land — Swamp'),
            Artist(first_name='Dan', last_name='Frazier'),
            []
        ),
        (
            CardEdition(number=264, number_suffix='',
                        rarity=CardEdition.RARITY_LAND),
            Card(name='Swamp', types='Basic Land — Swamp'),
            Artist(first_name='Jung', last_name='Park'),
            []
        ),
    ]
    setentries['DKA'] = [
        (
            CardEdition(number=53, number_suffix='',
                        rarity=CardEdition.RARITY_UNCOMMON),
            Card(name='Tower Geist', types='Creature — Spirit'),
            Artist(first_name='', last_name='Izzy'),
            [],
        ),
    ]

    def parse_blocks_sets():
        for block in MockParser.blocks:
            yield block, MockParser.sets

    def parse_cards_by_set(setcode):
        for edition, card, artist, rulings in MockParser.setentries[setcode]:
            yield edition, card, artist, rulings


@pytest.mark.django_db
class TestMCIDownloader_GetCardEditionImages:
    """Tests for
    :func:`mtgcardbox.utils.images.MCIDownloader.get_card_edition_images`.

    """
    def test_multi_jace(self, tmpdir):
        insert_blocks_sets_cards_from_parser(parser=MockParser)
        MCIDownloader.get_card_edition_images(str(tmpdir))

        assert os.path.isdir(str(tmpdir.join('ORI')))
        assert os.path.isfile(str(tmpdir.join('ORI', '60a.jpg')))
        assert os.path.isfile(str(tmpdir.join('ORI', '60b.jpg')))

    def test_multi_edition_tower_geist(self, tmpdir):
        insert_blocks_sets_cards_from_parser(parser=MockParser)
        MCIDownloader.get_card_edition_images(str(tmpdir))

        assert os.path.isdir(str(tmpdir.join('ORI')))
        assert os.path.isfile(str(tmpdir.join('ORI', '80.jpg')))
        assert os.path.isdir(str(tmpdir.join('DKA')))
        assert os.path.isfile(str(tmpdir.join('DKA', '53.jpg')))

    def test_multi_edition_swamp(self, tmpdir):
        insert_blocks_sets_cards_from_parser(parser=MockParser)
        MCIDownloader.get_card_edition_images(str(tmpdir))

        assert os.path.isdir(str(tmpdir.join('ORI')))
        assert os.path.isfile(str(tmpdir.join('ORI', '261.jpg')))
        assert os.path.isfile(str(tmpdir.join('ORI', '262.jpg')))
        assert os.path.isfile(str(tmpdir.join('ORI', '264.jpg')))
