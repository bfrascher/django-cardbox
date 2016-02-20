# coding: utf-8

import datetime
import pytest

from django.contrib.auth.models import User

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

from cardbox.utils.db import (
    insert_blocks_sets_cards_from_parser,
)



class MockParser:
    blocks = [
        Block(name='Test block', category=Block.CATEGORY_NONE),
    ]

    sets = [
        Set(code='ORI', name='Magic Origins',
            release_date=datetime.date(2015, 7, 17)),
        Set(code='DKA', name='Dark Ascension',
            release_date=datetime.date(2012, 2, 3)),
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


@pytest.mark.django_db
class PrepareCollections:
    user = [
        User(username='number one'),
        User(username='darling'),
    ]
    collections = [
        (
            'number one',
            Collection(name='First collection', date_created=datetime.date(1, 1, 1)),
        ),
        (
            'darling',
            Collection(name='Bestest', date_created=datetime.date(1, 1, 1)),
        ),
    ]

    entries = {}
    entries['First collection'] = [
        ('ORI', 60, 'a', 5, 2),
        ('ORI', 80, '', 3, 0),
        ('DKA', 53, '', 0, 2),
        ('ORI', 262, '', 5, 0),
        ('ORI', 264, '', 2, 0),
    ]
    entries['Bestest'] = [
        ('ORI', 60, 'b', 2, 7),
        ('ORI', 80, '', 8, 2),
        ('DKA', 53, '', 3, 77),
        ('ORI', 262, '', 2, 0),
        ('ORI', 264, '', 0, 1),
    ]

    def create_collections():
        """Prepare some collections and collection entries."""
        insert_blocks_sets_cards_from_parser(parser=MockParser)
        for user in PrepareCollections.user:
            user.save()

        for username, collection in PrepareCollections.collections:
            user = User.objects.get(username=username)
            collection.owner = user
            collection.save()

            for (code, number, number_suffix, count,
                 foil_count) in PrepareCollections.entries[collection.name]:
                edition = CardEdition.objects.get(
                    mtgset__code=code, number=number,
                    number_suffix=number_suffix)
                entry = CollectionEntry(collection=collection, edition=edition,
                                        count=count, foil_count=foil_count)
                entry.save()



class TestCard:
    @pytest.mark.parametrize("mana,mana_n,mana_w,mana_u,mana_b,mana_r,mana_g,mana_c,mana_special", [
        ('10RG', 10, 0, 0, 0, 1, 1, 0, ''),
        ('UWWGgg', 0, 2, 1, 0, 0, 3, 0, ''),
        ('3XCCBW', 3, 1, 0, 1, 0, 0, 2, 'X'),
        ('{BP}{2/W}2U', 2, 0, 1, 0, 0, 0, 0, '{BP}{2/W}'),
    ])
    def test_parse_mana(self, mana, mana_n, mana_w, mana_u, mana_b,
                        mana_r, mana_g, mana_c, mana_special):
        n, w, u, b, r, g, c, special = Card.parse_mana(mana)
        assert mana_n == n
        assert mana_w == w
        assert mana_u == u
        assert mana_b == b
        assert mana_r == r
        assert mana_g == g
        assert mana_c == c
        assert mana_special == special

    @pytest.mark.parametrize("mana,mana_n,mana_w,mana_u,mana_b,mana_r,mana_g,mana_c,mana_special", [
        ('10RG', 10, 0, 0, 0, 1, 1, 0, ''),
        ('WWUGGG', 0, 2, 1, 0, 0, 3, 0, ''),
        ('3WBCCX', 3, 1, 0, 1, 0, 0, 2, 'X'),
        ('2U{BP}{2/W}', 2, 0, 1, 0, 0, 0, 0, '{BP}{2/W}'),
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

    @pytest.mark.django_db
    @pytest.mark.parametrize("cardname,code,number,number_suffix", [
        ('Tower Geist', 'ORI', 80, ''),
        ('No card', 'DKA', 3457, 'no'),
        ('Swamp', 'ORI', 264, ''),
    ])
    def test_get_newest_edition(self, cardname, code, number, number_suffix):
        insert_blocks_sets_cards_from_parser(parser=MockParser)
        card = Card.objects.get(name=cardname)
        edition = CardEdition.objects.get(mtgset__code=code, number=number,
                                          number_suffix=number_suffix)
        assert edition == card.get_newest_edition()

    @pytest.mark.django_db
    @pytest.mark.parametrize("url,cardname", [
        ('cardbox/images/cards/ORI/60b.jpg', 'Jace, Telepath Unbound'),
        ('cardbox/images/cards/ORI/80.jpg', 'Tower Geist'),
        ('cardbox/images/cards/DKA/3457no.jpg', 'No card'),
    ])
    def test_get_image_url(self, url, cardname):
        insert_blocks_sets_cards_from_parser(parser=MockParser)
        card = Card.objects.get(name=cardname)
        assert url == card.get_image_url()

    @pytest.mark.django_db
    @pytest.mark.parametrize("collectionname,cardname,count,fcount", [
        ('First collection', "Jace, Vryn's Prodigy", 5, 2),
        ('First collection', "Tower Geist", 3, 2),
        ('First collection', "Swamp", 7, 0),
        ('Bestest', "Jace, Telepath Unbound", 2, 7),
        ('Bestest', "Tower Geist", 11, 79),
        ('Bestest', "Swamp", 2, 1),
    ])
    def test_get_count_in_collection(self, collectionname, cardname,
                                     count, fcount):
        PrepareCollections.create_collections()

        card = Card.objects.get(name=cardname)
        collection = Collection.objects.get(name=collectionname)
        c, fc = card.get_count_in_collection(collection)
        assert c == count
        assert fc == fcount


class TestCardEdition:
    """All tests for methods of :cls:`cardbox.models.CardEdition`."""
    @pytest.mark.parametrize("number_str,number,number_suffix", [
        ('435c', 435, 'c'),
        ('54', 54, ''),
        pytest.mark.xfail(('3abc', 3, 'c')),
    ])
    def test_parse_number(self, number_str, number, number_suffix):
        n, ns = CardEdition.parse_number(number_str)
        assert n == number
        assert ns == number_suffix
