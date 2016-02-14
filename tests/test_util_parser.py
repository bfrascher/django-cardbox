# coding: utf-8
import datetime
import pytest

from bs4 import BeautifulSoup
from django.test import TestCase

from mtgcardbox.models import (
    Artist,
    Ruling,
    Block,
    Set,
    Card,
    CardEdition,
)

from mtgcardbox.utils.parser import (
    MCIParser,
)

@pytest.fixture(scope='module')
def blockset():
    blocks = []
    sets = []
    for b, s in MCIParser.parse_all_blocks_sets():
        blocks.append(b)
        sets += s
    return blocks, sets


class TestMCIParser:
    @staticmethod
    def _get_index_by_name(blocksetlist, name):
        """Get the index of a block or set in blocksets by name."""
        for i, b in enumerate(blocksetlist):
            if b.name == name:
                return i
        return None

    def test_parse_blocks(self, blockset):
        blocks, _ = blockset

        i = TestMCIParser._get_index_by_name(
            blocks, 'Battle for Zendikar')
        assert blocks[i].name == 'Battle for Zendikar'
        assert blocks[i].category == Block.CATEGORY_EXPANSION

        i = TestMCIParser._get_index_by_name(
            blocks, 'Magic Online')
        assert blocks[i].category == Block.CATEGORY_MTGO

    def test_parse_sets_en(self, blockset):
        blocks, sets = blockset

        i = TestMCIParser._get_index_by_name(
            sets, 'Oath of the Gatewatch')
        j = TestMCIParser._get_index_by_name(
            blocks, 'Battle for Zendikar')
        assert sets[i].name == 'Oath of the Gatewatch'
        assert sets[i].code == 'OGW'
        assert sets[i].block == blocks[j]

        i = TestMCIParser._get_index_by_name(
                sets, 'Gatecrash')
        assert sets[i].code == 'GTC'

        i = TestMCIParser._get_index_by_name(
            sets, 'Modern Masters')
        j = TestMCIParser._get_index_by_name(
            blocks, 'Reprint Sets')
        assert sets[i].code == 'MMA'
        assert sets[i].block == blocks[j]

    @pytest.mark.parametrize("text,types_e,power_e,toughness_e,loyalty_e,mana_e,cmc_e", [
        ('Sorcery, 4G (5)', 'Sorcery', None, None, None, '4G', 5),
        ('Instant,\n        1W', 'Instant', None, None, None, '1W', None),
        ('Creature — Efreet Shaman 0/5,\n       2R (3)      \n', 'Creature — Efreet Shaman', 0, 5, None, '2R', 3),
        ('Creature — Elemental Spellshaper      1/3,   \n\n\n  (3)', 'Creature — Elemental Spellshaper', 1, 3, None, None, 3),
        ('Legendary Land\n     ', 'Legendary Land', None, None, None, None, None),
        ('Sorcery,  \n    XUUU (3)', 'Sorcery', None, None, None, 'XUUU', 3),
        ('Planeswalker — Bolas (Loyalty: 5), 4UBBR (8)', 'Planeswalker — Bolas', None, None, 5, '4UBBR', 8)
    ])
    def test__parse_types_stats(self, text, types_e, power_e, toughness_e,
                                loyalty_e, mana_e, cmc_e):
        html = '<p>{0}</p>'.format(text)
        p = BeautifulSoup(html, 'html.parser')
        types, po, to, lo, mana, cmc = MCIParser._parse_types_stats(p)
        try:
            power = int(po)
        except ValueError:
            power = po
        except TypeError:
            power = None
        try:
            toughness = int(to)
        except ValueError:
            toughness = to
        except TypeError:
            toughness = None
        try:
            loyalty = int(lo)
        except ValueError:
            loyalty = lo
        except TypeError:
            loyalty = None
            assert (types == types_e) if types_e is not None else (types is None)
            assert (power == power_e) if power_e is not None else (power is None)
            assert (toughness == toughness_e) if toughness_e is not None else (toughness is None)
            assert (loyalty == loyalty_e) if loyalty_e is not None else (loyalty is None)
            assert (mana == mana_e) if mana_e is not None else (mana is None)
            assert (cmc == cmc_e) if cmc_e is not None else (cmc is None)

    # Template for testing parsing a whole card.
    # def test_parse_card_(self):
    #     card, artist, rulings = MCIParser.parse_card('', '')

    #     # === card =========================================================
    #     assert card.multiverseid ==

    #     assert card.name == ""
    #     assert card.types == ''
    #     assert card.rules == """"""
    #     assert card.flavour == """"""

    #     assert card.power is None
    #     assert card.power_special == ''
    #     assert card.toughness is None
    #     assert card.toughness_special == ''
    #     assert card.loyalty is None
    #     assert card.loyalty_special == ''

    #     assert card.mana_n is None
    #     assert card.mana_w is None
    #     assert card.mana_u is None
    #     assert card.mana_b is None
    #     assert card.mana_r is None
    #     assert card.mana_g is None
    #     assert card.mana_c is None
    #     assert card.mana_special == ''
    #     assert card.cmc is None

    #     assert card.multi_type == Card.MULTI_NONE

    #     assert card.legal_vintage == Card.LEGALITY_LEGAL
    #     assert card.legal_legacy == Card.LEGALITY_LEGAL
    #     assert card.legal_extended == Card.LEGALITY_LEGAL
    #     assert card.legal_standard == Card.LEGALITY_LEGAL
    #     assert card.legal_classic == Card.LEGALITY_LEGAL
    #     assert card.legal_commander == Card.LEGALITY_LEGAL
    #     assert card.legal_modern == Card.LEGALITY_LEGAL

    #     # === artist =======================================================
    #     assert artist.first_name == ''
    #     assert artist.last_name == ''

    #     # === rulings ======================================================
    #     assert len(rulings) ==
    #     assert rulings[0].date == datetime.date()
    #     assert rulings[0].ruling == ""
    #     assert rulings[1].ruling == ""
    #     assert rulings[].date == datetime.date()
    #     assert rulings[].ruling == ""

    def test_parse_card_jace_vryns_prodigy(self):
        card, artist, rulings = MCIParser.parse_card('ori', '60a')
        dual_card, *_ = MCIParser.parse_card('ori', '60b')

        # === card =========================================================
        assert card.multiverseid == 398434

        assert card.name == "Jace, Vryn's Prodigy"
        assert card.types == 'Legendary Creature — Human Wizard'
        assert card.rules == "{T}: Draw a card, then discard a card. If there are five or more cards in your graveyard, exile Jace, Vryn's Prodigy, then return him to the battlefield transformed under his owner's control."
        assert card.flavour == "\"People's thoughts just come to me. Sometimes I don't know if it's them or me thinking.\""

        assert card.power == 0
        assert card.power_special == ''
        assert card.toughness == 2
        assert card.toughness_special == ''
        assert card.loyalty is None
        assert card.loyalty_special == ''

        assert card.mana_n == 1
        assert card.mana_w is None
        assert card.mana_u == 1
        assert card.mana_b is None
        assert card.mana_r is None
        assert card.mana_g is None
        assert card.mana_c is None
        assert card.mana_special == ''
        assert card.cmc == 2

        assert card.multi_type == Card.MULTI_FLIP

        assert card.legal_vintage == Card.LEGALITY_LEGAL
        assert card.legal_legacy == Card.LEGALITY_LEGAL
        assert card.legal_extended == Card.LEGALITY_NONE
        assert card.legal_standard == Card.LEGALITY_LEGAL
        assert card.legal_classic == Card.LEGALITY_NONE
        assert card.legal_commander == Card.LEGALITY_LEGAL
        assert card.legal_modern == Card.LEGALITY_LEGAL

        # === dual card ====================================================
        assert dual_card.multiverseid == 398435

        assert dual_card.name == "Jace, Telepath Unbound"
        assert dual_card.types == 'Planeswalker — Jace'
        assert dual_card.rules == """+1: Up to one target creature gets -2/-0 until your next turn.

−3: You may cast target instant or sorcery card from your graveyard this turn. If that card would be put into a graveyard this turn, exile it instead.

−9: You get an emblem with "Whenever you cast a spell, target opponent puts the top five cards of his or her library into his or her graveyard."""
        assert dual_card.flavour == ''

        assert dual_card.power is None
        assert dual_card.power_special == ''
        assert dual_card.toughness is None
        assert dual_card.toughness_special == ''
        assert dual_card.loyalty == 5
        assert dual_card.loyalty_special == ''

        assert dual_card.mana_n is None
        assert dual_card.mana_w is None
        assert dual_card.mana_u is None
        assert dual_card.mana_b is None
        assert dual_card.mana_r is None
        assert dual_card.mana_g is None
        assert dual_card.mana_c is None
        assert dual_card.mana_special == ''
        assert dual_card.cmc is None

        assert dual_card.multi_type == Card.MULTI_FLIP

        assert dual_card.legal_vintage == Card.LEGALITY_LEGAL
        assert dual_card.legal_legacy == Card.LEGALITY_LEGAL
        assert dual_card.legal_extended == Card.LEGALITY_NONE
        assert dual_card.legal_standard == Card.LEGALITY_LEGAL
        assert dual_card.legal_classic == Card.LEGALITY_NONE
        assert dual_card.legal_commander == Card.LEGALITY_LEGAL
        assert dual_card.legal_modern == Card.LEGALITY_LEGAL

        # === artist =======================================================
        assert artist.first_name == 'Jaime'
        assert artist.last_name == 'Jones'

        # === rulings ======================================================
        assert len(rulings) == 11
        assert rulings[0].date == datetime.date(2015, 6, 22)
        assert rulings[0].ruling == "The activated ability of Jace, Vryn’s Prodigy checks to see if there are five or more cards in your graveyard after you discard a card. Putting a fifth card into your graveyard at other times won’t cause Jace to be exiled, nor will Jace entering the battlefield while there are five or more cards in your graveyard."
        assert rulings[1].ruling == "Each face of a double-faced card has its own set of characteristics: name, types, subtypes, power and toughness, loyalty, abilities, and so on. While a double-faced card is on the battlefield, consider only the characteristics of the face that’s currently up. The other set of characteristics is ignored. While a double-faced card isn’t on the battlefield, consider only the characteristics of its front face."
        assert rulings[10].ruling == "If a double-faced card is manifested, it will be put onto the battlefield face down (this is also true if it’s put onto the battlefield face down some other way). Note that “face down” is not synonymous with “with its back face up.” A manifested double-faced card is a 2/2 creature with no name, mana cost, creature types, or abilities. While face down, it can’t transform. If the front face of a manifested double-faced card is a creature card, you can turn it face up by paying its mana cost. If you do, its front face will be up. A double-faced card on the battlefield can’t be turned face down."

    def test_parse_card_alive_well(self):
        card, artist, rulings = MCIParser.parse_card('dgm', '121a')
        dual_card, *_ = MCIParser.parse_card('dgm', '121b')

        # === card =========================================================
        assert card.multiverseid == 369041

        assert card.name == "Alive (Alive/Well)"
        assert card.types == 'Sorcery'
        assert card.rules == """Put a 3/3 green Centaur creature token onto the battlefield.

Fuse (You may cast one or both halves of this card from your hand.)"""
        assert card.flavour == ''

        assert card.power is None
        assert card.power_special == ''
        assert card.toughness is None
        assert card.toughness_special == ''
        assert card.loyalty is None
        assert card.loyalty_special == ''

        assert card.mana_n == 3
        assert card.mana_w is None
        assert card.mana_u is None
        assert card.mana_b is None
        assert card.mana_r is None
        assert card.mana_g == 1
        assert card.mana_c is None
        assert card.mana_special == ''
        assert card.cmc == 4

        assert card.multi_type == Card.MULTI_SPLIT

        assert card.legal_vintage == Card.LEGALITY_LEGAL
        assert card.legal_legacy == Card.LEGALITY_LEGAL
        assert card.legal_extended == Card.LEGALITY_LEGAL
        assert card.legal_standard == Card.LEGALITY_NONE
        assert card.legal_classic == Card.LEGALITY_LEGAL
        assert card.legal_commander == Card.LEGALITY_LEGAL
        assert card.legal_modern == Card.LEGALITY_LEGAL

        # === dual card ====================================================
        assert dual_card.multiverseid == 369041

        assert dual_card.name == "Well (Alive/Well)"
        assert dual_card.types == 'Sorcery'
        assert dual_card.rules == """You gain 2 life for each creature you control.

Fuse (You may cast one or both halves of this card from your hand.)"""
        assert dual_card.flavour == ''

        assert dual_card.power is None
        assert dual_card.power_special == ''
        assert dual_card.toughness is None
        assert dual_card.toughness_special == ''
        assert dual_card.loyalty is None
        assert dual_card.loyalty_special == ''

        assert dual_card.mana_n is None
        assert dual_card.mana_w == 1
        assert dual_card.mana_u is None
        assert dual_card.mana_b is None
        assert dual_card.mana_r is None
        assert dual_card.mana_g is None
        assert dual_card.mana_c is None
        assert dual_card.mana_special == ''
        assert dual_card.cmc == 1

        assert dual_card.multi_type == Card.MULTI_SPLIT

        assert dual_card.legal_vintage == Card.LEGALITY_LEGAL
        assert dual_card.legal_legacy == Card.LEGALITY_LEGAL
        assert dual_card.legal_extended == Card.LEGALITY_LEGAL
        assert dual_card.legal_standard == Card.LEGALITY_NONE
        assert dual_card.legal_classic == Card.LEGALITY_LEGAL
        assert dual_card.legal_commander == Card.LEGALITY_LEGAL
        assert dual_card.legal_modern == Card.LEGALITY_LEGAL

        # === artist =======================================================
        assert artist.first_name == 'Nils'
        assert artist.last_name == 'Hamm'

        # === rulings ======================================================
        assert len(rulings) == 12
        assert rulings[0].date == datetime.date(2013, 4, 15)
        assert rulings[0].ruling == "If you're casting a split card with fuse from any zone other than your hand, you can't cast both halves. You'll only be able to cast one half or the other."
        assert rulings[2].ruling == "You can choose the same object as the target of each half of a fused split spell, if appropriate."
        assert rulings[10].date == datetime.date(2013, 4, 15)
        assert rulings[11].ruling == "If you cast Alive/Well as a fused split spell, the Centaur creature token will count toward the amount of life you gain."

    def test_parse_card_afflicted_deserted(self):
        card, artist, rulings = MCIParser.parse_card('dka', '81a')
        dual_card, *_ = MCIParser.parse_card('dka', '81b')

        # === card =========================================================
        assert card.multiverseid == 262675

        assert card.name == "Afflicted Deserter"
        assert card.types == 'Creature — Human Werewolf'
        assert card.rules == 'At the beginning of each upkeep, if no spells were cast last turn, transform Afflicted Deserter.'
        assert card.flavour == "The rising of the first full moon eliminated any doubt as to the horrible truth lurking within."

        assert card.power == 3
        assert card.power_special == ''
        assert card.toughness == 2
        assert card.toughness_special == ''
        assert card.loyalty is None
        assert card.loyalty_special == ''

        assert card.mana_n == 3
        assert card.mana_w is None
        assert card.mana_u is None
        assert card.mana_b is None
        assert card.mana_r == 1
        assert card.mana_g is None
        assert card.mana_c is None
        assert card.mana_special == ''
        assert card.cmc == 4

        assert card.multi_type == Card.MULTI_FLIP

        assert card.legal_vintage == Card.LEGALITY_LEGAL
        assert card.legal_legacy == Card.LEGALITY_LEGAL
        assert card.legal_extended == Card.LEGALITY_LEGAL
        assert card.legal_standard == Card.LEGALITY_NONE
        assert card.legal_classic == Card.LEGALITY_LEGAL
        assert card.legal_commander == Card.LEGALITY_LEGAL
        assert card.legal_modern == Card.LEGALITY_LEGAL

        # === dual card ====================================================
        assert dual_card.multiverseid == 262698

        assert dual_card.name == "Werewolf Ransacker"
        assert dual_card.types == 'Creature — Werewolf'
        assert dual_card.rules == """Whenever this creature transforms into Werewolf Ransacker, you may destroy target artifact. If that artifact is put into a graveyard this way, Werewolf Ransacker deals 3 damage to that artifact's controller.

At the beginning of each upkeep, if a player cast two or more spells last turn, transform Werewolf Ransacker."""
        assert dual_card.flavour == ''

        assert dual_card.power == 5
        assert dual_card.power_special == ''
        assert dual_card.toughness == 4
        assert dual_card.toughness_special == ''
        assert dual_card.loyalty is None
        assert dual_card.loyalty_special == ''

        assert dual_card.mana_n is None
        assert dual_card.mana_w is None
        assert dual_card.mana_u is None
        assert dual_card.mana_b is None
        assert dual_card.mana_r is None
        assert dual_card.mana_g is None
        assert dual_card.mana_c is None
        assert dual_card.mana_special == ''
        assert dual_card.cmc is None

        assert dual_card.multi_type == Card.MULTI_FLIP

        assert dual_card.legal_vintage == Card.LEGALITY_LEGAL
        assert dual_card.legal_legacy == Card.LEGALITY_LEGAL
        assert dual_card.legal_extended == Card.LEGALITY_LEGAL
        assert dual_card.legal_standard == Card.LEGALITY_NONE
        assert dual_card.legal_classic == Card.LEGALITY_LEGAL
        assert dual_card.legal_commander == Card.LEGALITY_LEGAL
        assert dual_card.legal_modern == Card.LEGALITY_LEGAL

        # === artist =======================================================
        assert artist.first_name == 'David'
        assert artist.last_name == 'Palumbo'

        # === rulings ======================================================
        assert len(rulings) == 4
        assert rulings[0].date == datetime.date(2011, 1, 22)
        assert rulings[0].ruling == "You choose the target artifact when Werewolf Ransacker's first triggered ability goes on the stack. You choose whether or not to destroy the artifact when that ability resolves."
        assert rulings[1].ruling == "An artifact token that's destroyed is put into its owner's graveyard before it ceases to exist. If a token is destroyed by Werewolf Ransacker ability, Werewolf Ransacker deals damage to that token's controller."
        assert rulings[3].date == datetime.date(2013, 7, 1)
        assert rulings[3].ruling == "If the targeted artifact has indestructible or regenerates (or you choose not to destroy it), Werewolf Ransacker doesn't deal damage to that artifact's controller. Similarly, if the targeted artifact is destroyed but a replacement effect moves it to a different zone instead of its owner's graveyard, Werewolf Ransacker doesn't deal damage to that artifact's controller."

    def test_parse_card_advice_form_the_fae(self):
        card, artist, rulings = MCIParser.parse_card('shm', '28')

        # === card =========================================================
        assert card.multiverseid == 154408

        assert card.name == "Advice from the Fae"
        assert card.types == 'Sorcery'
        assert card.rules == """({2/U} can be paid with any two mana or with {U}. This card's converted mana cost is 6.)

Look at the top five cards of your library. If you control more creatures than each other player, put two of those cards into your hand. Otherwise, put one of them into your hand. Then put the rest on the bottom of your library in any order."""
        assert card.flavour == """"""

        assert card.power is None
        assert card.power_special == ''
        assert card.toughness is None
        assert card.toughness_special == ''
        assert card.loyalty is None
        assert card.loyalty_special == ''

        assert card.mana_n is None
        assert card.mana_w is None
        assert card.mana_u is None
        assert card.mana_b is None
        assert card.mana_r is None
        assert card.mana_g is None
        assert card.mana_c is None
        assert card.mana_special == '{2/U}{2/U}{2/U}'
        assert card.cmc == 6

        assert card.multi_type == Card.MULTI_NONE

        assert card.legal_vintage == Card.LEGALITY_LEGAL
        assert card.legal_legacy == Card.LEGALITY_LEGAL
        assert card.legal_extended == Card.LEGALITY_NONE
        assert card.legal_standard == Card.LEGALITY_NONE
        assert card.legal_classic == Card.LEGALITY_LEGAL
        assert card.legal_commander == Card.LEGALITY_LEGAL
        assert card.legal_modern == Card.LEGALITY_LEGAL

        # === artist =======================================================
        assert artist.first_name == ''
        assert artist.last_name == 'Chippy'

        # === rulings ======================================================
        assert len(rulings) == 5
        assert rulings[0].date == datetime.date(2008, 5, 1)
        assert rulings[0].ruling == "If an effect reduces the cost to cast a spell by an amount of generic mana, it applies to a monocolored hybrid spell only if you've chosen a method of paying for it that includes generic mana."
        assert rulings[1].ruling == "A card with a monocolored hybrid mana symbol in its mana cost is each of the colors that appears in its mana cost, regardless of what mana was spent to cast it. Thus, Advice from the Fae is blue, even if you spend six black mana to cast it."
        assert rulings[4].date == datetime.date(2008, 5, 1)
        assert rulings[4].ruling == "In a multiplayer game, compare the number of creatures you control with the number of creatures each other player controls. If any single player controls at least as many creatures as you, you get to put only one card into your hand."

    def test_parse_card_dismember(self):
        card, artist, rulings = MCIParser.parse_card('mm2', '79')

        # === card =========================================================
        assert card.multiverseid == 397830

        assert card.name == "Dismember"
        assert card.types == 'Instant'
        assert card.rules == """({BP} can be paid with either {B} or 2 life.)

Target creature gets -5/-5 until end of turn."""
        assert card.flavour == """"You serve Phyrexia. Your pieces would better serve Phyrexia elsewhere."
—Azax-Azog, the Demon Thane"""

        assert card.power is None
        assert card.power_special == ''
        assert card.toughness is None
        assert card.toughness_special == ''
        assert card.loyalty is None
        assert card.loyalty_special == ''

        assert card.mana_n == 1
        assert card.mana_w is None
        assert card.mana_u is None
        assert card.mana_b is None
        assert card.mana_r is None
        assert card.mana_g is None
        assert card.mana_c is None
        assert card.mana_special == '{BP}{BP}'
        assert card.cmc == 3

        assert card.multi_type == Card.MULTI_NONE

        assert card.legal_vintage == Card.LEGALITY_LEGAL
        assert card.legal_legacy == Card.LEGALITY_LEGAL
        assert card.legal_extended == Card.LEGALITY_LEGAL
        assert card.legal_standard == Card.LEGALITY_NONE
        assert card.legal_classic == Card.LEGALITY_LEGAL
        assert card.legal_commander == Card.LEGALITY_LEGAL
        assert card.legal_modern == Card.LEGALITY_LEGAL

        # === artist =======================================================
        assert artist.first_name == 'Terese'
        assert artist.last_name == 'Nielsen'

        # === rulings ======================================================
        assert len(rulings) == 5
        assert rulings[0].date == datetime.date(2011, 6, 1)
        assert rulings[0].ruling == "A card with Phyrexian mana symbols in its mana cost is each color that appears in that mana cost, regardless of how that cost may have been paid."
        assert rulings[1].ruling == "To calculate the converted mana cost of a card with Phyrexian mana symbols in its cost, count each Phyrexian mana symbol as 1."
        assert rulings[4].date == datetime.date(2011, 6, 1)
        assert rulings[4].ruling == "Phyrexian mana is not a new color. Players can't add Phyrexian mana to their mana pools."

    def test_parse_card_jagged_scar_archers(self):
        card = Card(rarity=Card.RARITY_UNCOMMON)
        card, artist, rulings = MCIParser.parse_card('dpa', '72', card=card)

        # === card =========================================================
        assert card.multiverseid == 0
        assert card.rarity == Card.RARITY_UNCOMMON

        assert card.name == "Jagged-Scar Archers"
        assert card.types == 'Creature — Elf Archer'
        assert card.rules == """Jagged-Scar Archers's power and toughness are each equal to the number of Elves you control.

{T}: Jagged-Scar Archers deals damage equal to its power to target creature with flying."""
        assert card.flavour == """"""

        assert card.power is None
        assert card.power_special == '*'
        assert card.toughness is None
        assert card.toughness_special == '*'
        assert card.loyalty is None
        assert card.loyalty_special == ''

        assert card.mana_n == 1
        assert card.mana_w is None
        assert card.mana_u is None
        assert card.mana_b is None
        assert card.mana_r is None
        assert card.mana_g == 2
        assert card.mana_c is None
        assert card.mana_special == ''
        assert card.cmc == 3

        assert card.multi_type == Card.MULTI_NONE

        assert card.legal_vintage == Card.LEGALITY_LEGAL
        assert card.legal_legacy == Card.LEGALITY_LEGAL
        assert card.legal_extended == Card.LEGALITY_NONE
        assert card.legal_standard == Card.LEGALITY_NONE
        assert card.legal_classic == Card.LEGALITY_LEGAL
        assert card.legal_commander == Card.LEGALITY_LEGAL
        assert card.legal_modern == Card.LEGALITY_LEGAL

        # === artist =======================================================
        assert artist.first_name == ''
        assert artist.last_name == 'Parente'

        # === rulings ======================================================
        assert len(rulings) == 0

    def test_parse_card_allosaurus_rider(self):
        card, artist, rulings = MCIParser.parse_card('ddaevg', '2')

        # === card =========================================================
        assert card.multiverseid == 393942

        assert card.name == "Allosaurus Rider"
        assert card.types == 'Creature — Elf Warrior'
        assert card.rules == """You may exile two green cards from your hand rather than pay Allosaurus Rider's mana cost.

Allosaurus Rider's power and toughness are each equal to 1 plus the number of lands you control."""
        assert card.flavour == """"""

        assert card.power is None
        assert card.power_special == '1+*'
        assert card.toughness is None
        assert card.toughness_special == '1+*'
        assert card.loyalty is None
        assert card.loyalty_special == ''

        assert card.mana_n == 5
        assert card.mana_w is None
        assert card.mana_u is None
        assert card.mana_b is None
        assert card.mana_r is None
        assert card.mana_g == 2
        assert card.mana_c is None
        assert card.mana_special == ''
        assert card.cmc == 7

        assert card.multi_type == Card.MULTI_NONE

        assert card.legal_vintage == Card.LEGALITY_LEGAL
        assert card.legal_legacy == Card.LEGALITY_LEGAL
        assert card.legal_extended == Card.LEGALITY_NONE
        assert card.legal_standard == Card.LEGALITY_NONE
        assert card.legal_classic == Card.LEGALITY_LEGAL
        assert card.legal_commander == Card.LEGALITY_LEGAL
        assert card.legal_modern == Card.LEGALITY_LEGAL

        # === artist =======================================================
        assert artist.first_name == 'Daren'
        assert artist.last_name == 'Bader'

        # === rulings ======================================================
        assert len(rulings) == 4
        assert rulings[0].date == datetime.date(2006, 7, 15)
        assert rulings[0].ruling == "Paying the alternative cost doesn't change when you can cast the spell. A creature spell you cast this way, for example, can still only be cast during your main phase while the stack is empty."
        assert rulings[1].ruling == "You may pay the alternative cost rather than the card's mana cost. Any additional costs are paid as normal."
        assert rulings[3].date == datetime.date(2006, 7, 15)
        assert rulings[3].ruling == "You can't exile a card from your hand to pay for itself. At the time you would pay costs, that card is on the stack, not in your hand."

    def test_parse_set_ogw(self):
        test_cards = {}
        test_cards[0] = {'name': "Deceiver of Form",
                         'rarity': Card.RARITY_RARE,
                         'number': 1,
                         'number_suffix': ''}
        test_cards[3] = {'name': "Kozilek, the Great Distortion",
                         'rarity': Card.RARITY_MYTHIC_RARE,
                         'number': 4,
                         'number_suffix': ''}
        test_cards[5] = {'name': "Matter Reshaper",
                         'rarity': Card.RARITY_RARE,
                         'number': 6,
                         'number_suffix': ''}
        test_cards[44] = {'name': "Gravity Negator",
                          'rarity': Card.RARITY_COMMON,
                          'number': 45,
                          'number_suffix': ''}
        max_index = 44

        for i, (edition, card, *_) in enumerate(MCIParser.parse_cards_by_set('ogw')):
            if i not in test_cards:
                continue
            assert card.name == test_cards[i]['name']
            assert card.rarity == test_cards[i]['rarity']
            assert edition.number == test_cards[i]['number']
            assert edition.number_suffix == test_cards[i]['number_suffix']
            # Speed up the process a little bit by not loading all cards.
            if i >= max_index:
                break

    def test_parse_set_pro(self):
        test_cards = {}
        test_cards[0] = {'name': "Eternal Dragon",
                         'rarity': Card.RARITY_SPECIAL,
                         'number': 1,
                         'number_suffix': ''}
        test_cards[1] = {'name': "Mirari's Wake",
                         'rarity': Card.RARITY_SPECIAL,
                         'number': 2,
                         'number_suffix': ''}
        test_cards[2] = {'name': "Treva, the Renewer",
                         'rarity': Card.RARITY_SPECIAL,
                         'number': 3,
                         'number_suffix': ''}
        test_cards[3] = {'name': "Avatar of Woe",
                         'rarity': Card.RARITY_SPECIAL,
                         'number': 4,
                         'number_suffix': ''}
        test_cards[4] = {'name': "Ajani Goldmane",
                         'rarity': Card.RARITY_SPECIAL,
                         'number': 5,
                         'number_suffix': ''}
        max_index = 4

        for i, (edition, card, *_) in enumerate(MCIParser.parse_cards_by_set('pro')):
            if i not in test_cards:
                continue
            assert card.name == test_cards[i]['name']
            assert card.rarity == test_cards[i]['rarity']
            assert edition.number == test_cards[i]['number']
            assert edition.number_suffix == test_cards[i]['number_suffix']
            # Speed up the process a little bit by not loading all cards.
            if i >= max_index:
                break

    def test_parse_set_ddm(self):
        test_cards = {}
        test_cards[0] = {'name': "Jace, Architect of Thought",
                         'rarity': Card.RARITY_MYTHIC_RARE,
                         'number': 1,
                         'number_suffix': ''}
        test_cards[11] = {'name': "Æther Adept",
                          'rarity': Card.RARITY_COMMON,
                          'number': 12,
                          'number_suffix': ''}
        test_cards[34] = {'name': "Dread Statuary",
                          'rarity': Card.RARITY_UNCOMMON,
                          'number': 35,
                          'number_suffix': ''}
        test_cards[38] = {'name': "Island",
                          'rarity': Card.RARITY_LAND,
                          'number': 39,
                          'number_suffix': ''}
        max_index = 38

        for i, (edition, card, *_) in enumerate(MCIParser.parse_cards_by_set('ddm')):
            if i not in test_cards:
                continue
            assert card.name == test_cards[i]['name']
            assert card.rarity == test_cards[i]['rarity']
            assert edition.number == test_cards[i]['number']
            assert edition.number_suffix == test_cards[i]['number_suffix']
            # Speed up the process a little bit by not loading all cards.
            if i >= max_index:
                break

    def test_parse_set_ddj(self):
        test_cards = {}
        test_cards[0] = {'name': "Niv-Mizzet, the Firemind",
                         'rarity': Card.RARITY_MYTHIC_RARE,
                         'number': 1,
                         'number_suffix': ''}
        test_cards[16] = {'name': "Izzet Signet",
                          'rarity': Card.RARITY_COMMON,
                          'number': 17,
                          'number_suffix': ''}
        test_cards[31] = {'name': "Fire (Fire/Ice)",
                          'rarity': Card.RARITY_UNCOMMON,
                          'number': 32,
                          'number_suffix': 'a'}
        test_cards[32] = {'name': "Forgotten Cave",
                          'rarity': Card.RARITY_COMMON,
                          'number': 33,
                          'number_suffix': ''}
        max_index = 32

        for i, (edition, card, *_) in enumerate(MCIParser.parse_cards_by_set('ddj')):
            if i not in test_cards:
                continue
            assert card.name == test_cards[i]['name']
            assert card.rarity == test_cards[i]['rarity']
            assert edition.number == test_cards[i]['number']
            assert edition.number_suffix == test_cards[i]['number_suffix']
            # Speed up the process a little bit by not loading all cards.
            if i >= max_index:
                break
