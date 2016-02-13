import logging

from cardbox.models import (
    Artist,
    MTGRuling,
    MTGBlock,
    MTGSet,
    MTGCard,
    MTGCardEdition,
    MTGCollection,
    MTGCollectionEntry,
)

from cardbox.utils.parser import (
    MTGBlockSetParser,
    MTGCardParser,
)


logger = logging.getLogger(__name__)


def update_mtg_block(block):
    """Create/update a single MTG block.

    :raises MTGBlock.MultipleObjectsReturned: if more than one entry
    already exists with `block.name` and `block.category`.

    """
    try:
        b = MTGBlock.objects.get(name=block.name, category=block.category)
        block = b
        logger.info("Skipping existing MTGBlock '{0}'."
                    .format(b.name))
    except MTGBlock.DoesNotExist:
        logger.info("Creating new MTGBlock '{0}'.".format(block.name))
        block.save()
    return block


def update_mtg_set(block, mtgset):
    """Create/update a single MTG set.

    :raises MTGSet.MultipleObjectsReturned: if more than one entry
    already exists with `mtgset.name` and `mtgset.code`.

    """
    try:
        s = MTGSet.objects.get(code=mtgset.code, name=mtgset.name)
        if mtgset.release_date != s.release_date:
            logger.info("Updating MTGSet '{0}'."
                        .format(mtgset))
            s.release_date = mtgset.release_date
            s.save()
        else:
            logger.info("Skipping existing MTGSet '{0}'."
                        .format(mtgset))
    except MTGSet.DoesNotExist:
        logger.info("Creating new MTGSet '{0}' in MTGBlock '{1}'."
                    .format(mtgset, block))
        mtgset.block = block
        mtgset.save()
    return mtgset


def update_all_mtg_blocks_sets():
    """Create/update all MTG blocks and sets.

    Existing blocks and sets will be skipped.

    """
    engine = MTGBlockSetParser.MCIEngine
    for block, sets in engine.parse():
        try:
            block = update_mtg_block(block)
        except MTGBlock.MultipleObjectsReturned:
            logger.error("There are multiple MTGBlocks for '{0}'!"
                         .format(block))
            # TODO(benedikt) Throw exception here.
            continue

        for mtgset in sets:
            try:
                update_mtg_set(block, mtgset)
            except MTGSet.MutltipleObjectsReturned:
                logger.error("There are multiple MTGSets for '{0}'!"
                             .format(mtgset))
                # TODO(benedikt) Throw exception here
                continue


def update_mtg_card(mtgset, card, rulings):
    try:
        c = MTGCard.objects.get(name=card.name, rarity=card.rarity)

    except MTGCard.DoesNotExist:
        logger.info("Creating new MTGCard '{0}' in MTGSet '{1}'"
                    .format(card, mtgset))


def update_all_mtg_cards_by_set():
    """Create/update all MTG cards from all sets.

    Existing cards will be updated or skipped.

    """
    engine = MTGCardParser.MCIEngine
    mtgsets = MTGSet.objects.all()

    for mtgset in mtgsets:
        for edition, card, dual_edition, dual_card, artist, rulings in engine.parse_set(mtgset.code):
            # Order of processing: rulings -> artist -> card -> edition -> dual_card -> dual_edition
            try:
                update_mtg_card(mtgset, edition, card, dual_edition,
                                dual_card, artist, rulings)
            except MTGCard.MultipleObjectsReturned:
                logger.error("Multiple entries for MTGCard '{0}'!".format(card))
                continue
