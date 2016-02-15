import datetime
import pytest

from mtgcardbox.models import (
    Artist,
    Ruling,
    Block,
    Set,
    Card,
    CardEdition,
)

from mtgcardbox.utils.db import (
    insert_artist,
    insert_ruling,
    insert_block,
    insert_set,
    insert_card,
    insert_card_edition,
    insert_blocks_sets_from_parser,
    insert_cards_by_set_from_parser,
    insert_cards_from_parser,
)


class MockParser:
    blocks = [
        Block(name='The first block', category=Block.CATEGORY_MTGO),
        Block(name='second block', category=Block.CATEGORY_SPECIAL_SET),
        Block(name='final Block', category=Block.CATEGORY_CORE_SET),
    ]

    sets = {}
    sets['The first block'] = [
        Set(code='SMS', name='Some set'),
        Set(code='SIFB', name='set in first block'),
    ]
    sets['second block'] = [
        Set(code='SBS', name='second block set'),
    ]
    sets['final Block'] = [
        Set(code='FBS', name='final block set'),
    ]

    setentries = {}
    setentries['SMS'] = [
        (
            CardEdition(number=5, number_suffix='a',
                        rarity=CardEdition.RARITY_RARE),
            Card(name='Song (Song/Ice/Fire)', types='Sorcery',
                 multi_type=Card.MULTI_SPLIT),
            Artist(first_name='George R. R.', last_name='Martin'),
            [
                Ruling(ruling='Lannisters lose!', date=datetime.date(1, 1, 1)),
                Ruling(ruling='Starks rule!', date=datetime.date(2, 1, 1)),
            ]
        ),
        (
            CardEdition(number=5, number_suffix='b',
                        rarity=CardEdition.RARITY_RARE),
            Card(name='Ice (Song/Ice/Fire)', types='Sorcery',
                 multi_type=Card.MULTI_SPLIT),
            Artist(first_name='George R. R.', last_name='Martin'),
            [
                Ruling(ruling='Lannisters lose!', date=datetime.date(1, 1, 1)),
                Ruling(ruling='Starks rule!', date=datetime.date(2, 1, 1)),
            ]
        ),
        (
            CardEdition(number=5, number_suffix='c',
                        rarity=CardEdition.RARITY_RARE),
            Card(name='Fire (Song/Ice/Fire)', types='Sorcery',
                 multi_type=Card.MULTI_SPLIT),
            Artist(first_name='George R. R.', last_name='Martin'),
            [
                Ruling(ruling='Lannisters lose!', date=datetime.date(1, 1, 1)),
                Ruling(ruling='Starks rule!', date=datetime.date(2, 1, 1)),
            ]
        ),
        (
            CardEdition(number=13, number_suffix='a',
                        rarity=CardEdition.RARITY_RARE),
            Card(name='Wheel (Wheel/Time)', types='Legendary Creature',
                 multi_type=Card.MULTI_FLIP),
            Artist(first_name='Robert', last_name='Jordan'),
            []
        ),
        (
            CardEdition(number=13, number_suffix='b',
                        rarity=CardEdition.RARITY_RARE),
            Card(name='Time (Wheel/Time)', types='Legendary Creature',
                 multi_type=Card.MULTI_FLIP),
            Artist(first_name='Brandon', last_name='Sanderson'),
            []
        ),
    ]
    setentries['SIFB'] = [
        (
            CardEdition(number=1, number_suffix='',
                        rarity=CardEdition.RARITY_COMMON),
            Card(name='Card with multiple editions', types='Reprint'),
            Artist(first_name='Model', last_name='Artist'),
            [
                Ruling(ruling='This card has multiple editions.',
                       date=datetime.date(1, 1, 1)),
                Ruling(ruling='No really, check it out.',
                       date=datetime.date(1, 1, 2)),
            ]
        ),
    ]
    setentries['SBS'] = [
        (
            CardEdition(number=1, number_suffix='',
                        rarity=CardEdition.RARITY_COMMON),
            Card(name='Card with multiple editions', types='Reprint'),
            Artist(first_name='Lone', last_name='Artist'),
            []
        ),
    ]
    setentries['FBS'] = [
        (
            CardEdition(number=3, number_suffix='',
                        rarity=CardEdition.RARITY_UNCOMMON),
            Card(name='Card with multiple editions', types='Reprint'),
            Artist(first_name='Model', last_name='Artist'),
            []
        ),
    ]

    def parse_blocks_sets():
        for block in MockParser.blocks:
            yield block, MockParser.sets[block.name]

    def parse_cards_by_set(setcode):
        for edition, card, artist, rulings in MockParser.setentries[setcode]:
            yield edition, card, artist, rulings


@pytest.mark.django_db
class TestInsertArtist:
    """All tests for :func:`mtgcardbox.utils.db.insert_artist`."""
    artists = [
        Artist(first_name='', last_name='NoFirstName'),
        Artist(first_name='Test', last_name='Testerson'),
        Artist(first_name='John TwoNames', last_name='Doe')
    ]

    @pytest.mark.parametrize('artist', artists)
    def test_insert_artist(self, artist):
        """Test inserting an artist."""
        a = insert_artist(artist)
        assert a.id is not None

    # Currently there is no point to further test insert_artist, as
    # it's too simple.

    # @pytest.mark.parametrize('artist', artists)
    # def test_skip_artist(self, artist):
    #     """Test skipping an existing artist."""
    #     artist.save()
    #     assert artist.id is not None

    # @pytest.mark.parametrize('artist', artists)
    # def test_update_artist(self, artist):
    #     """Test updating an existing artist."""
    #     artist.save()
    #     assert artist.id is not None


@pytest.mark.django_db
class TestInsertRuling:
    """All tests for :func:`mtgcardbox.utils.db.insert_ruling`."""
    rulings = [
        Ruling(ruling='Some things.', date=datetime.date(2015, 1, 1)),
        Ruling(ruling='You win!', date=datetime.date(1999, 5, 27)),
        Ruling(ruling='Some more text here.', date=datetime.date(2009, 11, 2)),
    ]

    @pytest.mark.parametrize('ruling', rulings)
    def test_insert_ruling(self, ruling):
        """Test inserting a ruling."""
        r = insert_ruling(ruling)
        assert r.id is not None

    @pytest.mark.parametrize('ruling', rulings)
    def test_skip_ruling(self, ruling):
        """Test skipping an existing ruling."""
        ruling.save()
        assert ruling.id is not None
        new_ruling = Ruling(ruling=ruling.ruling,
                            date=datetime.date(1, 1, 1))
        r = insert_ruling(new_ruling, update=False)
        assert r.id == ruling.id
        assert r.date == ruling.date
        assert r.ruling == ruling.ruling

    @pytest.mark.parametrize('ruling', rulings)
    def test_update_ruling(self, ruling):
        """Test updating an existing ruling."""
        ruling.save()
        assert ruling.id is not None
        new_ruling = Ruling(ruling=ruling.ruling,
                            date=datetime.date(1, 1, 1))
        r = insert_ruling(new_ruling, update=True)
        assert r.id == ruling.id
        assert r.date == new_ruling.date
        assert r.ruling == ruling.ruling


@pytest.mark.django_db
class TestInsertBlock:
    """All tests for :func:`mtgcardbox.utils.db.insert_block`."""
    blocks = [
        Block(name='First Block', category=Block.CATEGORY_NONE),
        Block(name='A block with five words', category=Block.CATEGORY_MTGO),
        Block(name='Shorty', category=Block.CATEGORY_SPECIAL_SET),
    ]

    @pytest.mark.parametrize('block', blocks)
    def test_insert_block(self, block):
        """Test inserting a block."""
        b = insert_block(block)
        assert b.id is not None

    @pytest.mark.parametrize('block', blocks)
    def test_skip_block(self, block):
        """Test skipping an existing block."""
        block.save()
        assert block.id is not None
        new_block = Block(name=block.name, category=Block.CATEGORY_CORE_SET)
        b = insert_block(new_block, update=False)
        assert b.id == block.id
        assert b.category == block.category
        assert b.name == block.name

    @pytest.mark.parametrize('block', blocks)
    def test_update_block(self, block):
        """Test updating an existing block."""
        block.save()
        assert block.id is not None
        new_block = Block(name=block.name, category=Block.CATEGORY_CORE_SET)
        b = insert_block(new_block, update=True)
        assert b.id == block.id
        assert b.category == new_block.category
        assert b.name == block.name


@pytest.mark.django_db
class TestInsertSet:
    """All tests for :func:`mtgcardbox.utils.db.insert_set`."""
    blocksets = [
        (Block(name='A block', category=Block.CATEGORY_EXPANSION),
         Set(code='A', name='A set', release_date=datetime.date(1587, 3, 8))),
        (Block(name='block AB', category=Block.CATEGORY_PROMO_CARD),
         Set(code='AB', name='set AB', release_date=datetime.date(2017, 5, 18))),
        (Block(name='MTG Testblock', category=Block.CATEGORY_SPECIAL_SET),
         Set(code='ACODE', name='MTG Testset')),
    ]

    @pytest.mark.parametrize('block,set_', blocksets)
    def test_insert_set(self, block, set_):
        """Test inserting a set."""
        block.save()
        assert block.id is not None
        s = insert_set(block, set_)
        assert s.id is not None

    @pytest.mark.parametrize('block,set_', blocksets)
    def test_skip_set(self, block, set_):
        """Test skipping an existing set."""
        block.save()
        assert block.id is not None
        set_ = insert_set(block, set_)
        assert set_.id is not None

        b = Block(name='New block', category=Block.CATEGORY_MTGO)
        b.save()
        assert b.id is not None

        new_set = Set(code=set_.code, name='New set',
                      release_date=datetime.date(1, 1, 1))
        s = insert_set(b, new_set, update=False)

        assert s.id == set_.id
        assert s.code == set_.code
        assert s.block.id == block.id
        assert s.name == set_.name
        assert s.release_date == set_.release_date

    @pytest.mark.parametrize('block,set_', blocksets)
    def test_update_set(self, block, set_):
        """Test updating an existing set."""
        block.save()
        assert block.id is not None
        set_ = insert_set(block, set_)
        assert set_.id is not None

        b = Block(name='New block', category=Block.CATEGORY_MTGO)
        b.save()
        assert b.id is not None

        new_set = Set(code=set_.code, name='New set',
                      release_date=datetime.date(1, 1, 1))
        s = insert_set(b, new_set, update=True)

        assert s.id == set_.id
        assert s.code == set_.code
        assert s.block.id == b.id
        assert s.name == new_set.name
        assert s.release_date == new_set.release_date


@pytest.mark.django_db
class TestInsertCard:
    """All tests for :func:`mtgcardbox.utils.db.insert_card`."""
    cards = [
        Card(name='First card', types='Token'),
        Card(name='Second card', types='Basic Land'),
        Card(name='Third card', types='Instant'),
    ]

    @pytest.mark.parametrize('card', cards)
    def test_insert_card(self, card):
        """Test inserting a card."""
        c = insert_card(card)
        assert c.id is not None

    @pytest.mark.parametrize('card', cards)
    def test_skip_card(self, card):
        """Test skipping an existing card."""
        card.save()
        assert card.id is not None

        new_card = Card(name=card.name, types='New', cmc=5,
                        legal_classic=Card.LEGALITY_BANNED)
        c = insert_card(new_card, update=False)
        assert c.id == card.id
        assert c.name == card.name
        assert c.types == card.types
        assert c.cmc == card.cmc
        assert c.legal_classic == card.legal_classic

    @pytest.mark.parametrize('card', cards)
    def test_update_card(self, card):
        """Test updating an existing card."""
        card.save()
        assert card.id is not None

        new_card = Card(name=card.name, types='New', cmc=5,
                        legal_classic=Card.LEGALITY_BANNED)
        c = insert_card(new_card, update=True)
        assert c.id == card.id
        assert c.name == card.name
        assert c.types == new_card.types
        assert c.cmc == new_card.cmc
        assert c.legal_classic == new_card.legal_classic


# TODO(benedikt) Implement
@pytest.mark.django_db
class TestInsertCardEdition:
    """All tests for :func:`mtgcardbox.utils.db.insert_card_edition`."""
    editions = [
        CardEdition(),
        CardEdition(),
        CardEdition(),
    ]

    @pytest.mark.parametrize('edition', editions)
    def test_insert_card_edition(self, edition):
        """Test inserting a edition."""
        pass

    @pytest.mark.parametrize('edition', editions)
    def test_skip_card_edition(self, edition):
        """Test skipping an existing edition."""
        pass

    @pytest.mark.parametrize('edition', editions)
    def test_update_card_edition(self, edition):
        """Test updating an existing edition."""
        pass


@pytest.mark.django_db
class TestInsertBlocksSetsFromParser:
    """All tests for
    :func:`mtgcardbox.utils.db.insert_blocks_sets_from_parser`.

    """
    def test_with_mock_parser(self):
        """Test that blocks and sets are associated right."""
        insert_blocks_sets_from_parser(parser=MockParser)
        block = Block.objects.get(name='The first block')
        assert block.category == MockParser.blocks[0].category

        set_ = Set.objects.get(code='SMS')
        assert set_.name == 'Some set'
        assert set_.block_id == block.id

        set_ = Set.objects.get(code='FBS')
        assert set_.name == 'final block set'
        assert set_.block_id is not None
        assert set_.block_id != block.id


@pytest.mark.django_db
class TestInsertCardsBySetFromParser:
    """All tests for
    :func:`mtgcardbox.utils.db.insert_cards_by_set_from_parser`.

    """
    def test_multi_cards(self):
        """Test that multi cards are associated right."""
        insert_blocks_sets_from_parser(parser=MockParser)
        set_ = Set.objects.get(code='SMS')
        insert_cards_by_set_from_parser(set_, parser=MockParser)

        card_song = Card.objects.get(name='Song (Song/Ice/Fire)')
        card_ice = Card.objects.get(name='Ice (Song/Ice/Fire)')
        card_fire = Card.objects.get(name='Fire (Song/Ice/Fire)')
        card_wheel = Card.objects.get(name='Wheel (Wheel/Time)')
        card_time = Card.objects.get(name='Time (Wheel/Time)')

        assert len(card_song.multi_cards.all()) == 2
        assert len(card_ice.multi_cards.all()) == 2
        assert len(card_fire.multi_cards.all()) == 2
        assert len(card_wheel.multi_cards.all()) == 1
        assert len(card_time.multi_cards.all()) == 1

    def test_rulings(self):
        """Test that the rulings are reused."""
        insert_blocks_sets_from_parser(parser=MockParser)
        set_ = Set.objects.get(code='SMS')
        insert_cards_by_set_from_parser(set_, parser=MockParser)

        card_song = Card.objects.get(name='Song (Song/Ice/Fire)')
        card_ice = Card.objects.get(name='Ice (Song/Ice/Fire)')
        card_fire = Card.objects.get(name='Fire (Song/Ice/Fire)')

        assert len(Ruling.objects.all()) == 2
        assert len(card_song.rulings.all()) == 2
        assert len(card_ice.rulings.all()) == 2
        assert len(card_fire.rulings.all()) == 2

    def test_artists(self):
        """Test that artists are reused."""
        insert_blocks_sets_from_parser(parser=MockParser)
        set_ = Set.objects.get(code='SMS')
        insert_cards_by_set_from_parser(set_, parser=MockParser)

        card_song = Card.objects.get(name='Song (Song/Ice/Fire)')
        card_fire = Card.objects.get(name='Fire (Song/Ice/Fire)')

        assert (card_song.editions.all()[0].artist.id ==
                card_fire.editions.all()[0].artist.id)

    def test_editions(self):
        """Test that editions are added correctly."""
        insert_blocks_sets_from_parser(parser=MockParser)
        set_ = Set.objects.get(code='FBS')
        insert_cards_by_set_from_parser(set_, parser=MockParser)

        card = Card.objects.get(name='Card with multiple editions')
        assert len(card.editions.all()) == 1
        assert len(card.rulings.all()) == 0
        assert card.editions.all()[0].rarity == CardEdition.RARITY_UNCOMMON

        set_ = Set.objects.get(code='SIFB')
        insert_cards_by_set_from_parser(set_, parser=MockParser)
        set_ = Set.objects.get(code='SBS')
        insert_cards_by_set_from_parser(set_, parser=MockParser)

        card.refresh_from_db()
        assert len(card.editions.all()) == 3
        assert len(card.rulings.all()) == 2
        assert (card.editions.get(mtgset_id=set_.id).rarity ==
                CardEdition.RARITY_COMMON)

    def test_with_mci_parser(self):
        insert_blocks_sets_from_parser()
        set_ = Set.objects.get(code='DDJ')
        insert_cards_by_set_from_parser(set_)

        card_life = Card.objects.get(name='Life (Life/Death)')
        card_death = Card.objects.get(name='Death (Life/Death)')
        assert card_life.multi_cards.all()[0].id == card_death.id
        assert card_death.multi_cards.all()[0].id == card_life.id
        assert card_life.editions.get(mtgset_id=set_.id).number == 77

        card_island = Card.objects.get(name='Island')
        assert len(card_island.editions.all()) == 4

        card_doomgape = Card.objects.get(name='Doomgape')
        assert card_doomgape.mana_special == '{B/G}{B/G}{B/G}'


@pytest.mark.django_db
class TestInsertCardsFromParser:
    """All tests for
    :func:`mtgcardbox.utils.db.insert_cards_from_parser`.

    """
    def test_with_mock_parser(self):
        """Test that the sets are read from the database correctly."""
        insert_blocks_sets_from_parser(parser=MockParser)
        insert_cards_from_parser(parser=MockParser)

        card_ice = Card.objects.get(name='Ice (Song/Ice/Fire)')
        card_mult = Card.objects.get(name='Card with multiple editions')

        assert len(card_ice.editions.all()) == 1
        assert len(card_mult.editions.all()) == 3
