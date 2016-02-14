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
)


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

    @pytest.mark.parametrize('artist', artists)
    def test_skip_artist(self, artist):
        """Test skipping an existing artist."""
        artist.save()
        assert artist.id is not None
        new_artist = Artist(last_name=artist.last_name,
                            first_name='SomeThingDifferent')
        a = insert_artist(new_artist, update=False)
        assert a.id == artist.id
        assert a.first_name == artist.first_name

    @pytest.mark.parametrize('artist', artists)
    def test_update_artist(self, artist):
        """Test updating an existing artist."""
        artist.save()
        assert artist.id is not None
        new_artist = Artist(last_name=artist.last_name,
                            first_name='SomeThingDifferent')
        a = insert_artist(new_artist, update=True)
        assert a.id == artist.id
        assert a.first_name == new_artist.first_name


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
        assert s.code == set_.code

    @pytest.mark.parametrize('block,set_', blocksets)
    def test_skip_set(self, block,set_):
        """Test skipping an existing set."""
        pass

    @pytest.mark.parametrize('block,set_', blocksets)
    def test_update_set(self, block, set_):
        """Test updating an existing set."""
        pass


@pytest.mark.django_db
class TestInsertCard:
    """All tests for :func:`mtgcardbox.utils.db.insert_card`."""
    cards = [
        Card(),
        Card(),
        Card(),
    ]

    @pytest.mark.parametrize('card', cards)
    def test_insert_card(self, card):
        """Test inserting a card."""
        pass

    @pytest.mark.parametrize('card', cards)
    def test_skip_card(self, card):
        """Test skipping an existing card."""
        pass

    @pytest.mark.parametrize('card', cards)
    def test_update_card(self, card):
        """Test updating an existing card."""
        pass


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
