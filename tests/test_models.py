# coding: utf-8

import pytest

from cardbox.models import (
    Artist,
    Ruling,
    Block,
    Set,
    Card,
    CardEdition,
    Collection,
    CollectionEntry,
)


class MockParser:
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
            Card(name='Jace, Telepath Unbound', types='Planeswalker — Jace',
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
        (
            CardEdition(number=3457, number_suffix='no',
                        rarity=CardEdition.RARITY_SPECIAL),
            Card(name='No card', types='None'),
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


class TestCard:
    @pytest.mark.parametrize("mana,mana_n,mana_w,mana_u,mana_b,mana_r,mana_g,mana_c,mana_special", [
        ('10RG', 10, None, None, None, 1, 1, None, ''),
        ('UWWGgg', None, 2, 1, None, None, 3, None, ''),
        ('3XCCBW', 3, 1, None, 1, None, None, 2, 'X'),
        ('{BP}{2/W}2U', 2, None, 1, None, None, None, None, '{BP}{2/W}'),
    ])
    def test_parse_mana(self, mana, mana_n, mana_w, mana_u, mana_b,
                        mana_r, mana_g, mana_c, mana_special):
        n, w, u, b, r, g, c, special = Card.parse_mana(mana)
        assert (mana_n == n) if mana_n else (n is None)
        assert (mana_w == w) if mana_w else (w is None)
        assert (mana_u == u) if mana_u else (u is None)
        assert (mana_b == b) if mana_b else (b is None)
        assert (mana_r == r) if mana_r else (r is None)
        assert (mana_g == g) if mana_g else (g is None)
        assert (mana_c == c) if mana_c else (c is None)
        assert mana_special == special

    @pytest.mark.parametrize("mana,mana_n,mana_w,mana_u,mana_b,mana_r,mana_g,mana_c,mana_special", [
        ('10RG', 10, None, None, None, 1, 1, None, ''),
        ('WWUGGG', None, 2, 1, None, None, 3, None, ''),
        ('3WBCCX', 3, 1, None, 1, None, None, 2, 'X'),
        ('2U{BP}{2/W}', 2, None, 1, None, None, None, None, '{BP}{2/W}'),
    ])
    def test_get_mana(self, mana, mana_n, mana_w, mana_u, mana_b,
                      mana_r, mana_g, mana_c, mana_special):
        card = Card(mana_n=mana_n, mana_w=mana_w, mana_u=mana_u, mana_b=mana_b,
                    mana_r=mana_r, mana_g=mana_g, mana_c=mana_c,
                    mana_special=mana_special)
        assert card.get_mana() == mana

    @pytest.mark.parametrize("ptl,p,ps,t,ts,l,ls", [
        ('*/3', None, '*', 3, '', None, ''),
        ('(Loyalty: 7)', None, '', None, '', 7, ''),
        ('*/2*', None, '*', None, '2*', None, ''),
        ('4/5 (Loyalty: *)', 4, '', 5, '', None, '*'),
        ('4*/8', 4, '*', 8, '', None, ''),
        ('(Loyalty: 2*)', None, '', None, '', 2, '*'),
    ])
    def test_get_ptl(self, ptl, p, ps, t, ts, l, ls):
        card = Card(power=p, power_special=ps,
                    toughness=t, toughness_special=ts,
                    loyalty=l, loyalty_special=ls)
        assert card.get_ptl() == ptl

    def test_get_newest_edition(self):
        pass

    def test_get_image_url(self):
        pass

    def test_get_count_in_collection(self):
        pass
