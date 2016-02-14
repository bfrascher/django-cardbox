import logging

from mtgcardbox.models import (
    Artist,
    Ruling,
    Block,
    Set,
    Card,
    CardEdition,
    Collection,
    CollectionEntry,
)

from mtgcardbox.utils.parser import (
    BlockSetParser,
    CardParser,
)


logger = logging.getLogger(__name__)


def update_mtg_block(block):
    """Create/update a single  block.

    :raises Block.MultipleObjectsReturned: if more than one entry
    already exists with `block.name` and `block.category`.

    """
    try:
        b = Block.objects.get(name=block.name, category=block.category)
        block = b
        logger.info("Skipping existing Block '{0}'."
                    .format(b.name))
    except Block.DoesNotExist:
        logger.info("Creating new Block '{0}'.".format(block.name))
        block.save()
    return block


def update_mtg_set(block, mtgset):
    """Create/update a single  set.

    :raises Set.MultipleObjectsReturned: if more than one entry
    already exists with `mtgset.name` and `mtgset.code`.

    """
    try:
        s = Set.objects.get(code=mtgset.code, name=mtgset.name)
        if mtgset.release_date != s.release_date:
            logger.info("Updating Set '{0}'."
                        .format(mtgset))
            s.release_date = mtgset.release_date
            s.save()
        else:
            logger.info("Skipping existing Set '{0}'."
                        .format(mtgset))
    except Set.DoesNotExist:
        logger.info("Creating new Set '{0}' in Block '{1}'."
                    .format(mtgset, block))
        mtgset.block = block
        mtgset.save()
    return mtgset


def update_all_mtg_blocks_sets():
    """Create/update all  blocks and sets.

    Existing blocks and sets will be skipped.

    """
    engine = BlockSetParser.MCIEngine
    for block, sets in engine.parse():
        try:
            block = update_mtg_block(block)
        except Block.MultipleObjectsReturned:
            logger.error("There are multiple Blocks for '{0}'!"
                         .format(block))
            # TODO(benedikt) Throw exception here.
            continue

        for mtgset in sets:
            try:
                update_mtg_set(block, mtgset)
            except Set.MutltipleObjectsReturned:
                logger.error("There are multiple Sets for '{0}'!"
                             .format(mtgset))
                # TODO(benedikt) Throw exception here
                continue


def update_mtg_card(mtgset, card, rulings):
    try:
        c = Card.objects.get(name=card.name, rarity=card.rarity)

    except Card.DoesNotExist:
        logger.info("Creating new Card '{0}' in Set '{1}'"
                    .format(card, mtgset))


def update_all_mtg_cards_by_set():
    """Create/update all  cards from all sets.

    Existing cards will be updated or skipped.

    """
    engine = CardParser.MCIEngine
    mtgsets = Set.objects.all()

    for mtgset in mtgsets:
        for edition, card, dual_edition, dual_card, artist, rulings in engine.parse_set(mtgset.code):
            # Order of processing: rulings -> artist -> card -> edition -> dual_card -> dual_edition
            try:
                update_mtg_card(mtgset, edition, card, dual_edition,
                                dual_card, artist, rulings)
            except Card.MultipleObjectsReturned:
                logger.error("Multiple entries for Card '{0}'!".format(card))
                continue
