# coding: utf-8
import pytest

from django.test import TestCase

from cardbox.models import (
    Artist,
    MTGRuling,
    MTGBlock,
    MTGSet,
    MTGCard,
    MTGCardEdition,
)

from cardbox.util.parser import (
    MTGBlockSetParser,
    MTGCardParser,
    MTGTokenParser,
)

@pytest.fixture(scope='module')
def blockset_en():
    blocks = []
    sets = []
    for b, s in MTGBlockSetParser.parse(lang='en'):
        blocks.append(b)
        sets += s
    return (blocks, sets)


@pytest.fixture(scope='module')
def blockset_de():
    blocks = []
    sets = []
    for b, s in MTGBlockSetParser.parse(lang='de'):
        blocks.append(b)
        sets += s
    return (blocks, sets)


class TestMTGBlockSetParser:
    @staticmethod
    def get_index_by_name(blocksetlist, name):
        """Get the index of a block or set in blocksets by name."""
        for i, b in enumerate(blocksetlist):
            if b.name == name:
                return i
        return None

    class TestMagicCardsInfoEngine:
        def test_parse_blocks_en(self, blockset_en):
            blocks, _ = blockset_en

            i = TestMTGBlockSetParser.get_index_by_name(
                blocks, 'Battle for Zendikar')
            assert blocks[i].name == 'Battle for Zendikar'
            assert blocks[i].category == MTGBlock.CATEGORY_EXPANSION

            i = TestMTGBlockSetParser.get_index_by_name(
                blocks, 'Magic Online')
            assert blocks[i].category == MTGBlock.CATEGORY_MTGO

        def test_parse_sets_en(self, blockset_en):
            blocks, sets = blockset_en

            i = TestMTGBlockSetParser.get_index_by_name(
                sets, 'Oath of the Gatewatch')
            j = TestMTGBlockSetParser.get_index_by_name(
                blocks, 'Battle for Zendikar')
            assert sets[i].name == 'Oath of the Gatewatch'
            assert sets[i].code == 'OGW'
            assert sets[i].block == blocks[j]

            i = TestMTGBlockSetParser.get_index_by_name(
                sets, 'Gatecrash')
            assert sets[i].code == 'GTC'

            i = TestMTGBlockSetParser.get_index_by_name(
                sets, 'Modern Masters')
            j = TestMTGBlockSetParser.get_index_by_name(
                blocks, 'Reprint Sets')
            assert sets[i].code == 'MMA'
            assert sets[i].block == blocks[j]

        def test_parse_blocks_de(self, blockset_de):
            blocks, _ = blockset_de

            i = TestMTGBlockSetParser.get_index_by_name(
                blocks, 'Battle for Zendikar')
            assert blocks[i].name == 'Battle for Zendikar'
            assert blocks[i].category == MTGBlock.CATEGORY_EXPANSION

        def test_parse_sets_de(self, blockset_de):
            blocks, sets = blockset_de

            i = TestMTGBlockSetParser.get_index_by_name(
                sets, 'Eid der Wächter')
            j = TestMTGBlockSetParser.get_index_by_name(
                blocks, 'Battle for Zendikar')
            assert sets[i].name == 'Eid der Wächter'
            assert sets[i].code == 'OGW'
            assert sets[i].block == blocks[j]

            i = TestMTGBlockSetParser.get_index_by_name(
                sets, 'Das neue Phyrexia')
            j = TestMTGBlockSetParser.get_index_by_name(
                blocks, 'Scars of Mirrodin')
            assert sets[i].name == 'Das neue Phyrexia'
            assert sets[i].code == 'NPH'
            assert sets[i].block == blocks[j]


class TestMTGCardParser:
    class TestMagicCardsInfoEngine:
        pass
