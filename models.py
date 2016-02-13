import re

from django.contrib.auth.models import User
from django.db import models


class Artist(models.Model):
    """Simple model for an artist.  Referenced in `cardbox.models.MTGCard`"""
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=100)

    class Meta:
        ordering = ['last_name', 'first_name']
        unique_together = ('first_name', 'last_name')

    def __str__(self):
        return '{0} {1}'.format(self.first_name, self.last_name)


class MTGRuling(models.Model):
    """Model for rulings that affect certain `cardbox.models.MTGCard`s."""
    ruling = models.TextField(unique=True)
    date = models.DateField("date of the ruling")

    def __str__(self):
        return '{0}: {1}'.format(self.date, self.ruling)


class MTGBlock(models.Model):
    """Model for a block in Magic The Gathering.  Used to group
    `cardbox.models.MTGSet`.

    """
    name = models.CharField(max_length=100, unique=True)

    CATEGORY_EXPANSION = 'E'
    CATEGORY_CORE_SET = 'C'
    CATEGORY_MTGO = 'O'
    CATEGORY_SPECIAL_SET = 'S'
    CATEGORY_PROMO_CARD = 'P'
    CATEGORIES = (
        (CATEGORY_EXPANSION, 'Expansion'),
        (CATEGORY_CORE_SET, 'Core Set'),
        (CATEGORY_MTGO, 'MTGO'),
        (CATEGORY_SPECIAL_SET, 'Special Set'),
        (CATEGORY_PROMO_CARD, 'Promo Card'),
    )
    category = models.CharField(max_length=1, choices=CATEGORIES,
                                default=CATEGORY_EXPANSION)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class MTGSet(models.Model):
    """Model for a Magic The Gathering set/expansion.  Used to group
    `tcc.models.MTGCard`.

    """
    block = models.ForeignKey(MTGBlock, on_delete=models.CASCADE)
    code = models.CharField("short form", max_length=10, primary_key=True)
    name = models.CharField("full name", max_length=100, unique=True)
    release_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['-release_date']

    def __str__(self):
        return self.name


class MTGCard(models.Model):
    """Model for a card in Magic The Gathering."""
    multiverseid = models.PositiveIntegerField(null=True, blank=True)

    # === set ========================================================
    sets = models.ManyToManyField(MTGSet, through='MTGCardEdition')

    # === card text ==================================================
    name = models.CharField(max_length=100)
    types = models.CharField(max_length=200)
    rules = models.TextField(blank=True)
    flavour = models.TextField(blank=True)

    # === stats ======================================================
    power = models.PositiveSmallIntegerField(default=None, null=True,
                                             blank=True)
    power_special = models.CharField(max_length=10, blank=True, default='')
    toughness = models.PositiveSmallIntegerField(default=None, null=True,
                                                 blank=True)
    toughness_special = models.CharField(max_length=10, blank=True,
                                         default='')
    loyalty = models.PositiveSmallIntegerField(default=None, null=True,
                                               blank=True)
    loyalty_special = models.CharField(max_length=10, blank=True, default='')

    # === mana =======================================================
    mana_n = models.PositiveSmallIntegerField("neutral mana", default=None,
                                              null=True, blank=True)
    mana_w = models.PositiveSmallIntegerField("white mana", default=None,
                                              null=True, blank=True)
    mana_u = models.PositiveSmallIntegerField("blue mana", default=None,
                                              null=True, blank=True)
    mana_b = models.PositiveSmallIntegerField("black mana", default=None,
                                              null=True, blank=True)
    mana_r = models.PositiveSmallIntegerField("red mana", default=None,
                                              null=True, blank=True)
    mana_g = models.PositiveSmallIntegerField("green mana", default=None,
                                              null=True, blank=True)
    mana_c = models.PositiveSmallIntegerField("colorless mana", default=None,
                                              null=True, blank=True)
    mana_special = models.CharField("special mana", max_length=50, blank=True)
    cmc = models.PositiveSmallIntegerField("converted mana cost", default=None,
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

    # === dual card ==================================================
    DUAL_NONE = ''
    DUAL_SPLIT = 'S'
    DUAL_FLIP = 'F'
    DUAL_TYPES = (
        (DUAL_NONE, 'not a dual card'),
        (DUAL_SPLIT, 'split-card'),
        (DUAL_FLIP, 'flip-card'),
    )
    dual_type = models.CharField(max_length=1, choices=DUAL_TYPES,
                                 default=DUAL_NONE, blank=True)
    dual_card = models.OneToOneField('self', on_delete=models.SET_NULL,
                                     default=None, null=True, blank=True,
                                     related_name='other_part')

    # === rulings ====================================================
    rulings = models.ManyToManyField(MTGRuling, blank=True)

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
        return len(color_str) if color_str else None

    @staticmethod
    def parse_mana(mana):
        mana = mana.upper()

        # Extract special mana first.
        list_special = re.findall(r'(\{.*?\}|X+)', mana)
        mana_special = ''.join(list_special)

        # Remove special strings, so we don't accidentally parse it later.
        for s in list_special:
            mana = mana.replace(s, '')

        print(mana)

        mana_n_str = re.search(r'\d+', mana)
        mana_n = int(mana_n_str.group()) if mana_n_str else None

        mana_w = MTGCard._count_mana(r'W+', mana)
        mana_u = MTGCard._count_mana(r'U+', mana)
        mana_b = MTGCard._count_mana(r'B+', mana)
        mana_r = MTGCard._count_mana(r'R+', mana)
        mana_g = MTGCard._count_mana(r'G+', mana)
        mana_c = MTGCard._count_mana(r'C+', mana)

        return (mana_n, mana_w, mana_u, mana_b, mana_r,
                mana_g, mana_c, mana_special)

    def set_mana(self, mana):
        if mana is None:
            return
        (n, w, u, b, r, g, c, special) = MTGCard.parse_mana(mana)
        self.mana_n = n
        self.mana_w = w
        self.mana_u = u
        self.mana_b = b
        self.mana_r = r
        self.mana_g = g
        self.mana_c = c
        self.mana_special = special

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


class MTGCardEdition(models.Model):
    """Model linking `cardbox.models.MTGCard` with
    `cardbox.models.MTGSet`.

    """
    number = models.PositiveSmallIntegerField()
    number_suffix = models.CharField(max_length=10, blank=True)
    mtgset = models.ForeignKey(MTGSet, on_delete=models.CASCADE)
    card = models.ForeignKey(MTGCard, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL,
                               null=True, blank=True)

    def __str__(self):
        if self.card:
            return '{0}{1} {0} in {1}'.format(self.number,
                                              self.number_suffix,
                                              self.card.name,
                                              self.mtgset.name)


class MTGCollection(models.Model):
    """Model of a shareable collection of `cardbox.models.MTGCard`s."""
    name = models.CharField(max_length=100)
    cards = models.ManyToManyField(MTGCard, through='MTGCollectionEntry',
                                   blank=True)
    date_created = models.DateField()

    # === user =======================================================
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    viewers = models.ManyToManyField(User, blank=True,
                                     related_name='viewable_mtgcollections')
    editors = models.ManyToManyField(User, blank=True,
                                     related_name='editable_mtgcollections')

    class Meta:
        ordering = ['date_created']

    def __str__(self):
        return self.name


class MTGCollectionEntry(models.Model):
    """Model a single card entry of a `cardbox.models.MTGCollection`."""
    collection = models.ForeignKey(MTGCollection, on_delete=models.CASCADE)
    card = models.ForeignKey(MTGCard, on_delete=models.CASCADE)
    count = models.PositiveSmallIntegerField("number of copies in the "
                                             "collection", default=1)
    foil_count = models.PositiveSmallIntegerField("number of foiled "
                                                  "copies in the collection.",
                                                  default=0)

    def __str__(self):
        return '{0} in {1}'.format(self.card.name, self.collection.name)
