# django-cardbox -- A collection manager for Magic: The Gathering
# Copyright (C) 2016 Benedikt Rascher-Friesenhausen
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import datetime
import re

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum


class Artist(models.Model):
    """Simple model for an artist.  Referenced in `cardbox.models.Card`"""
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Ruling(models.Model):
    """Model for rulings that affect certain `cardbox.models.Card`s."""
    ruling = models.TextField(unique=True)
    date = models.DateField("date of the ruling")

    def __str__(self):
        return '{0}: {1}'.format(self.date, self.ruling)


class Block(models.Model):
    """Model for a block in Magic The Gathering.  Used to group
    `cardbox.models.Set`.

    """
    name = models.CharField(max_length=100, unique=True)

    CATEGORY_NONE = ''
    CATEGORY_EXPANSION = 'E'
    CATEGORY_CORE_SET = 'C'
    CATEGORY_MTGO = 'M'
    CATEGORY_SPECIAL_SET = 'S'
    CATEGORY_PROMO_CARD = 'P'
    CATEGORIES = (
        (CATEGORY_NONE, 'unknown'),
        (CATEGORY_EXPANSION, 'Expansions'),
        (CATEGORY_CORE_SET, 'Core Sets'),
        (CATEGORY_MTGO, 'MTGO'),
        (CATEGORY_SPECIAL_SET, 'Special Sets'),
        (CATEGORY_PROMO_CARD, 'Promo Cards'),
    )
    category = models.CharField(max_length=1, choices=CATEGORIES,
                                default=CATEGORY_EXPANSION)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Set(models.Model):
    """Model for a Magic The Gathering set/expansion.  Used to group
    `cardbox.models.Card`.

    """
    block = models.ForeignKey(Block, on_delete=models.CASCADE)
    code = models.CharField("short form", max_length=10, unique=True)
    name = models.CharField("full name", max_length=100, unique=True)
    release_date = models.DateField(blank=True, default=datetime.date(1, 1, 1))

    class Meta:
        ordering = ['-release_date']

    def __str__(self):
        return self.name


class Card(models.Model):
    """Model for a card in Magic The Gathering."""
    multiverseid = models.PositiveIntegerField(null=True, blank=True)

    # === set ========================================================
    sets = models.ManyToManyField(Set, through='CardEdition')

    # === card text ==================================================
    name = models.CharField(max_length=200, unique=True)
    types = models.CharField(max_length=200)
    rules = models.TextField(blank=True)
    flavour = models.TextField(blank=True)

    # === stats ======================================================
    power = models.PositiveIntegerField(default=None, null=True,
                                        blank=True)
    power_special = models.CharField(max_length=10, blank=True, default='')
    toughness = models.PositiveIntegerField(default=None, null=True,
                                            blank=True)
    toughness_special = models.CharField(max_length=10, blank=True,
                                         default='')
    loyalty = models.PositiveIntegerField(default=None, null=True,
                                          blank=True)
    loyalty_special = models.CharField(max_length=10, blank=True, default='')

    # === mana =======================================================
    mana_n = models.PositiveIntegerField("neutral mana", default=0,
                                         blank=True)
    mana_w = models.PositiveIntegerField("white mana", default=0,
                                         blank=True)
    mana_u = models.PositiveIntegerField("blue mana", default=0,
                                         blank=True)
    mana_b = models.PositiveIntegerField("black mana", default=0,
                                         blank=True)
    mana_r = models.PositiveIntegerField("red mana", default=0,
                                         blank=True)
    mana_g = models.PositiveIntegerField("green mana", default=0,
                                         blank=True)
    mana_c = models.PositiveIntegerField("colorless mana", default=0,
                                         blank=True)
    mana_special = models.CharField("special mana", max_length=50, blank=True)
    cmc = models.PositiveIntegerField("converted mana cost", default=None,
                                      null=True, blank=True)

    # === multi card ==================================================
    MULTI_NONE = ''
    MULTI_SPLIT = 'S'
    MULTI_FLIP = 'F'
    MULTI_TYPES = (
        (MULTI_NONE, 'not a multi card'),
        (MULTI_SPLIT, 'split-card'),
        (MULTI_FLIP, 'flip-card'),
    )
    multi_type = models.CharField(max_length=1, choices=MULTI_TYPES,
                                  default=MULTI_NONE, blank=True)
    multi_cards = models.ManyToManyField('self', blank=True,
                                         related_name='other_parts')

    # === rulings ====================================================
    rulings = models.ManyToManyField(Ruling, blank=True)

    # === legality ===================================================
    LEGALITY_NONE = ''
    LEGALITY_LEGAL = 'L'
    LEGALITY_RESTRICTED = 'R'
    LEGALITY_BANNED = 'B'
    LEGALITIES = (
        (LEGALITY_NONE, 'unknown'),
        (LEGALITY_LEGAL, 'legal'),
        (LEGALITY_RESTRICTED, 'restricted'),
        (LEGALITY_BANNED, 'banned'),
    )
    legal_vintage = models.CharField(max_length=1, choices=LEGALITIES,
                                     default=LEGALITY_NONE, blank=True)
    legal_legacy = models.CharField(max_length=1, choices=LEGALITIES,
                                    default=LEGALITY_NONE, blank=True)
    legal_extended = models.CharField(max_length=1, choices=LEGALITIES,
                                      default=LEGALITY_NONE, blank=True)
    legal_standard = models.CharField(max_length=1, choices=LEGALITIES,
                                      default=LEGALITY_NONE, blank=True)
    legal_classic = models.CharField(max_length=1, choices=LEGALITIES,
                                     default=LEGALITY_NONE, blank=True)
    legal_commander = models.CharField(max_length=1, choices=LEGALITIES,
                                       default=LEGALITY_NONE, blank=True)
    legal_modern = models.CharField(max_length=1, choices=LEGALITIES,
                                    default=LEGALITY_NONE, blank=True)

    # === META =======================================================
    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @staticmethod
    def _count_mana(regex, mana):
        color_str = ''.join(re.findall(regex, mana))
        return len(color_str)

    @staticmethod
    def parse_mana(mana):
        mana = mana.upper()

        # Extract special mana first.
        list_special = re.findall(r'(\{.*?\}|X+)', mana)
        mana_special = ''.join(list_special)

        # Remove special strings, so we don't accidentally parse them later.
        for s in list_special:
            mana = mana.replace(s, '')

        mana_n_str = re.search(r'\d+', mana)
        mana_n = int(mana_n_str.group(0)) if mana_n_str else 0

        mana_w = Card._count_mana(r'W+', mana)
        mana_u = Card._count_mana(r'U+', mana)
        mana_b = Card._count_mana(r'B+', mana)
        mana_r = Card._count_mana(r'R+', mana)
        mana_g = Card._count_mana(r'G+', mana)
        mana_c = Card._count_mana(r'C+', mana)

        return (mana_n, mana_w, mana_u, mana_b, mana_r,
                mana_g, mana_c, mana_special)

    def set_mana(self, mana):
        if mana is None:
            return
        (n, w, u, b, r, g, c, special) = Card.parse_mana(mana)
        self.mana_n = n
        self.mana_w = w
        self.mana_u = u
        self.mana_b = b
        self.mana_r = r
        self.mana_g = g
        self.mana_c = c
        self.mana_special = special

    def get_mana(self):
        """Return the mana cost of this card as a string."""
        mana = str(self.mana_n) if self.mana_n != 0 else ''
        mana += self.mana_w*'W'
        mana += self.mana_b*'B'
        mana += self.mana_u*'U'
        mana += self.mana_r*'R'
        mana += self.mana_g*'G'
        mana += self.mana_c*'C'
        mana += self.mana_special
        return mana

    def get_ptl(self):
        """Return power/toughness/loyalty as a string."""
        ptl = ''
        p = str(self.power) if self.power is not None else ''
        p += self.power_special
        t = str(self.toughness) if self.toughness is not None else ''
        t += self.toughness_special
        if p != '' or t != '':
            ptl += '{0}/{1}'.format(p, t)

        if self.loyalty is not None or self.loyalty_special != '':
            l = str(self.loyalty) if self.loyalty is not None else ''
            l += self.loyalty_special
            spacing = '' if ptl == '' else ' '
            ptl += '{0}(Loyalty: {1})'.format(spacing, l)

        return ptl

    def set_power(self, power):
        try:
            self.power = int(power) if power else None
        except ValueError:
            self.power_special = power

    def set_toughness(self, toughness):
        try:
            self.toughness = int(toughness) if toughness else None
        except ValueError:
            self.toughness_special = toughness

    def set_loyalty(self, loyalty):
        try:
            self.loyalty = int(loyalty) if loyalty else None
        except ValueError:
            self.loyalty_special = loyalty

    def get_newest_edition(self):
        return self.editions.select_related('mtgset').order_by('-mtgset__release_date')[0]

    def get_image_url(self):
        """Return URL to the newest image of this card.

        The URL is designed to be used with `static` in templates.

        """
        edition = self.get_newest_edition()
        return 'cardbox/images/cards/{0}/{1}{2}.jpg'.format(
            edition.mtgset.code.upper(),
            edition.number, edition.number_suffix)

    def get_count_in_collection(self, collection):
        """Return the number of copies in the collection.

        :rtype int:
        :returns: The count and foiled count (in this order) of this
            card in `collection` over all editions.

        """
        sum = (CollectionEntry.objects.filter(
            collection=collection, edition__card=self)
               .aggregate(count=Sum('count'), foil_count=Sum('foil_count')))
        # The values should always be a number since the output could
        # be shown to the user.
        if sum['count'] is None:
            sum['count'] = 0
        if sum['foil_count'] is None:
            sum['foil_count'] = 0
        return sum['count'], sum['foil_count']

    def get_legality(self):
        legality = {}
        legality['legal'] = []
        legality['restricted'] = []
        legality['banned'] = []
        formats = {
            'Vintage': self.legal_vintage,
            'Legacy': self.legal_legacy,
            'Extended': self.legal_extended,
            'Standard': self.legal_standard,
            'Classic': self.legal_classic,
            'Commander': self.legal_commander,
            'Modern': self.legal_modern,
        }
        for f in formats:
            if formats[f] == self.LEGALITY_LEGAL:
                legality['legal'].append(f)
            elif formats[f] == self.LEGALITY_RESTRICTED:
                legality['restricted'].append(f)
            elif formats[f] == self.LEGALITY_BANNED:
                legality['banned'].append(f)
        return legality


class CardEdition(models.Model):
    """Model linking `cardbox.models.Card` with
    `cardbox.models.Set`.

    """
    number = models.PositiveIntegerField()
    number_suffix = models.CharField(max_length=10, blank=True)
    mtgset = models.ForeignKey(Set, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE,
                             related_name='editions')
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL,
                               null=True, blank=True)

    # === rarity =====================================================
    RARITY_NONE = ''
    RARITY_MYTHIC_RARE = 'M'
    RARITY_RARE = 'R'
    RARITY_UNCOMMON = 'U'
    RARITY_COMMON = 'C'
    RARITY_SPECIAL = 'S'
    RARITY_LAND = 'L'
    RARITY_TOKEN = 'T'
    RARITY_EMBLEM = 'E'
    RARITY_OTHER = 'O'
    RARITIES = (
        (RARITY_NONE, 'No rarity'),
        (RARITY_MYTHIC_RARE, 'Mythic Rare'),
        (RARITY_RARE, 'Rare'),
        (RARITY_UNCOMMON, 'Uncommon'),
        (RARITY_COMMON, 'Common'),
        (RARITY_SPECIAL, 'Special'),
        (RARITY_LAND, 'Land'),
        (RARITY_TOKEN, 'Token'),
        (RARITY_EMBLEM, 'Emblem'),
        (RARITY_OTHER, 'Other'),
    )
    rarity = models.CharField(max_length=1, choices=RARITIES,
                              default=RARITY_COMMON)

    class Meta:
        unique_together = ('number', 'number_suffix', 'mtgset',)
        ordering = ('-mtgset__release_date',)

    def __str__(self):
        if self.card:
            return '{0}{1} {2} in {3}'.format(self.number,
                                              self.number_suffix,
                                              self.card.name,
                                              self.mtgset.name)

    @staticmethod
    def parse_number(number_str):
        if number_str is None:
            return None, ''
        number_suffix = ''
        try:
            number = int(number_str)
        except ValueError:
            number = int(number_str[:-1])
            number_suffix = number_str[-1]

        return number, number_suffix

    def set_number(self, number_str):
        number, number_suffix = CardEdition.parse_number(number_str)
        self.number = number
        self.number_suffix = number_suffix


class Collection(models.Model):
    """Model of a shareable collection of `cardbox.models.Card`s."""
    name = models.CharField(max_length=100)
    editions = models.ManyToManyField(CardEdition,
                                      through='CollectionEntry',
                                      blank=True)
    date_created = models.DateField()

    # === user =======================================================
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    viewers = models.ManyToManyField(User, blank=True,
                                     related_name='viewable_collections')
    editors = models.ManyToManyField(User, blank=True,
                                     related_name='editable_collections')

    class Meta:
        ordering = ['date_created']

    def __str__(self):
        return self.name


class CollectionEntry(models.Model):
    """Model a single card entry of a `cardbox.models.Collection`."""
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    edition = models.ForeignKey(CardEdition, on_delete=models.CASCADE)
    count = models.PositiveIntegerField("number of copies in the "
                                        "collection", default=1)
    foil_count = models.PositiveIntegerField("number of foiled "
                                             "copies in the collection.",
                                             default=0)

    class Meta:
        unique_together = ('collection', 'edition')

    def __str__(self):
        return '{0} in {1}'.format(self.edition, self.collection.name)
