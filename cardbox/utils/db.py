import logging

from collections import namedtuple

from cardbox.models import (
    Artist,
    Ruling,
    Block,
    Set,
    Card,
    CardEdition,
#    Collection,
#    CollectionEntry,
)

from cardbox.utils.parser import (
    MCIParser,
)


logger = logging.getLogger(__name__)


def insert_artist(artist, update=False):
    """Create/update a single artist."""
    try:
        a = Artist.objects.get(last_name=artist.last_name,
                               first_name=artist.first_name)
        if update:
            logger.info("Updating artist '{0}'.".format(a))
            # a.save()
        else:
            logger.info("Skipping existing artist '{0}'.".format(a))

        artist = a
    except Artist.DoesNotExist:
        logger.info("Creating new artist '{0}'.".format(artist))
        artist.save()

    return artist


def insert_ruling(ruling, update=False):
    """Create/update a single ruling."""
    try:
        r = Ruling.objects.get(ruling=ruling.ruling)

        if update:
            r.date = ruling.date

            logger.info("Updating ruling '{0}'.".format(r))
            r.save()
        else:
            logger.info("Skipping existing ruling '{0}'.".format(r))

        ruling = r
    except Ruling.DoesNotExist:
        logger.info("Creating new ruling '{0}'.".format(ruling))
        ruling.save()

    return ruling


def insert_block(block, update=False):
    """Create/update a single block."""
    try:
        b = Block.objects.get(name=block.name)
        if update:
            b.category = block.category
            logger.info("Updating block '{0}'.".format(b))
            b.save()
        else:
            logger.info("Skipping existing block '{0}'.".format(b))

        block = b
    except Block.DoesNotExist:
        logger.info("Creating new block '{0}'.".format(block))
        block.save()
    return block


def insert_set(block, set_, update=False):
    """Create/update a single set.

    :type block: `cardbox.models.Block`
    :param block: A valid block from the database.

    :type set_: `cardbox.models.Set`
    :param set_: The set to create or update.

    """
    try:
        s = Set.objects.get(code=set_.code)
        if update:
            s.release_date = set_.release_date
            s.name = set_.name
            s.block = block

            logger.info("Updating set '{0}'.".format(s))
            s.save()
        else:
            logger.info("Skipping existing set '{0}'."
                        .format(s))

        set_ = s
    except Set.DoesNotExist:
        set_.block = block
        logger.info("Creating new set '{0}' in block '{1}'."
                    .format(set_, block))
        set_.save()
    return set_


def insert_card(card, update=False):
    """Create/update a single card.

    :type card: `cardbox.models.Card`
    :param set_: The card to create/update.

    :rtype: `cardbox.models.Card`
    :returns: The created/updated card with a valid id.

    """
    try:
        c = Card.objects.get(name=card.name)
        if update:
            c.name = card.name
            c.types = card.types
            c.rules = card.rules
            c.flavour = card.flavour
            c.power = card.power
            c.power_special = card.power_special
            c.toughness = card.toughness
            c.toughness_special = card.toughness_special
            c.loyalty = card.loyalty
            c.loyalty_special = card.loyalty_special
            c.mana_n = card.mana_n
            c.mana_w = card.mana_w
            c.mana_u = card.mana_u
            c.mana_b = card.mana_b
            c.mana_r = card.mana_r
            c.mana_g = card.mana_g
            c.mana_special = card.mana_special
            c.cmc = card.cmc
            c.multi_type = card.multi_type
            c.legal_vintage = card.legal_vintage
            c.legal_legacy = card.legal_legacy
            c.legal_extended = card.legal_extended
            c.legal_standard = card.legal_standard
            c.legal_classic = card.legal_classic
            c.legal_commander = card.legal_commander
            c.legal_modern = card.legal_modern

            logger.info("Updating card '{0}'.".format(c))
            c.save()
        else:
            logger.info("Skipping existing card '{0}'.".format(c))

        card = c
    except Card.DoesNotExist:
        logger.info("Creating new card '{0}'."
                    .format(card))
        card.save()
    return card


def insert_card_edition(set_, card, artist, edition, update=False):
    """Create/update a single card edition."""
    try:
        e = CardEdition.objects.get(number=edition.number,
                                    number_suffix=edition.number_suffix,
                                    mtgset_id=set_.id)
        if update:
            e.card = card
            e.artist = artist
            e.rarity = edition.rarity

            logger.info("Updating edition '{0}'.".format(e))
            e.save()
        else:
            logger.info("Skipping existing edition '{0}'.".format(e))

        edition = e
    except CardEdition.DoesNotExist:
        edition.mtgset = set_
        edition.card = card
        edition.artist = artist
        logger.info("Creating new edition '{0}'.".format(edition))
        edition.save()

    return edition


def insert_blocks_sets_from_parser(parser=MCIParser, update=False):
    """Create/update all blocks and sets.

    Existing blocks and sets will be skipped.

    """
    for block, sets in parser.parse_blocks_sets():
        block = insert_block(block, update)
        for set_ in sets:
            insert_set(block, set_, update)


def insert_cards_by_set_from_parser(set_, parser=MCIParser, update=False):
    """Create/update all  cards from all sets.

    Existing cards will be updated or skipped.

    """
    ECPair = namedtuple('ECPair', 'edition card')
    multi_pairs = []
    for edition, card, artist, rulings in parser.parse_cards_by_set(set_.code):
        artist = insert_artist(artist, update)
        card = insert_card(card, update)
        edition = insert_card_edition(set_, card, artist, edition,
                                      update)
        for ruling in rulings:
            ruling = insert_ruling(ruling, update)
            # Rulings already added to the card will be ignored.
            card.rulings.add(ruling)

        # All multi cards belonging together have the same edition
        # number (as we are only looking at one set).
        if (len(multi_pairs) > 0 and
            (multi_pairs[0].edition.number != edition.number)):
            multi_pairs = []
        if card.multi_type != Card.MULTI_NONE:
            for pair in multi_pairs:
                pair.card.multi_cards.add(card)
                card.multi_cards.add(pair.card)
            multi_pairs.append(ECPair(edition, card))


def insert_cards_from_parser(parser=MCIParser, update=False):
    sets = Set.objects.all()
    for set_ in sets:
        insert_cards_by_set_from_parser(set_, parser, update)


def insert_blocks_sets_cards_from_parser(parser=MCIParser, update=False):
    insert_blocks_sets_from_parser(parser, update)
    insert_cards_from_parser(parser, update)