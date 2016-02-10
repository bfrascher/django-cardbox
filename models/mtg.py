from django.contrib.auth.models import User
from django.db import models


class Artist(models.Model):
    """Simple model for an artist.  Referenced in `tccm.models.MTGCard`"""
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=100)

    class Meta:
        ordering = ['last_name', 'first_name']
        unique_together = ('first_name', 'last_name')

    def __str__(self):
        return '{0} {1}'.format(self.first_name, self.last_name)


class MTGBlock(models.Model):
    """Model for a block in Magic The Gathering.  Used to group
    `tccm.models.MTGSet`.

    """
    name = models.CharField(max_length=100, unique=True)

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
    release_date = models.DateField()

    class Meta:
        ordering = ['-release_date']

    def __str__(self):
        return self.name


class MTGCard(models.Model):
    """Model for a card in Magic The Gathering."""
    # === set ========================================================
    set_code = models.ForeignKey(MTGSet, on_delete=models.CASCADE)
    set_number_suffix = models.CharField(max_length=1, blank=True, default='')
    set_number = models.PositiveSmallIntegerField()

    # === card text ==================================================
    name = models.CharField(max_length=100)
    types = models.CharField(max_length=200)
    rules = models.TextField(blank=True)
    flavour = models.TextField(blank=True)

    # === mana =======================================================
    mana_n = models.PositiveSmallIntegerField("neutral mana", default=0)
    mana_w = models.PositiveSmallIntegerField("white mana", default=0)
    mana_u = models.PositiveSmallIntegerField("blue mana", default=0)
    mana_b = models.PositiveSmallIntegerField("black mana", default=0)
    mana_r = models.PositiveSmallIntegerField("red mana", default=0)
    mana_g = models.PositiveSmallIntegerField("green mana", default=0)
    mana_c = models.PositiveSmallIntegerField("colorless mana", default=0)
    mana_special = models.CharField("special mana", max_length=50, blank=True)
    cmc = models.PositiveSmallIntegerField("converted mana cost", default=0)

    # === stats ======================================================
    power = models.PositiveSmallIntegerField(default=0)
    power_special = models.CharField(max_length=10, blank=True, default='')
    toughness = models.PositiveSmallIntegerField(default=0)
    toughness_special = models.CharField(max_length=10, blank=True,
                                         default='')
    loyalty = models.PositiveSmallIntegerField(default=0)
    loyalty_special = models.CharField(max_length=10, blank=True, default='')

    # === rarity =====================================================
    RARITY_MYTHIC_RARE = 'M'
    RARITY_RARE = 'R'
    RARITY_UNCOMMON = 'U'
    RARITY_COMMON = 'C'
    RARITY_SPECIAL = 'S'
    RARITIES = (
        (RARITY_MYTHIC_RARE, 'Mythic Rare'),
        (RARITY_RARE, 'Rare'),
        (RARITY_UNCOMMON, 'Uncommon'),
        (RARITY_COMMON, 'Common'),
        (RARITY_SPECIAL, 'Special'),
    )
    rarity = models.CharField(max_length=1, choices=RARITIES,
                              default=RARITY_COMMON)

    # === art ========================================================
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True)

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
                                     default=None, null=True, blank=True)

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


class MTGRuling(models.Model):
    """Model for rulings that affect certain `tccm.models.MTGCard`s."""
    cards = models.ManyToManyField(MTGCard)
    ruling = models.TextField(unique=True)
    date = models.DateField("date of the ruling")


class MTGCollection(models.Model):
    """Model of a shareable collection of `tccm.models.MTGCard`s."""
    name = models.CharField(max_length=100)
    cards = models.ManyToManyField(MTGCard, through='MTGCollectionEntry')
    date_created = models.DateField()

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    viewers = models.ManyToManyField(User,
                                     related_name='viewable_mtgcollections')
    editors = models.ManyToManyField(User,
                                     related_name='editable_mtgcollections')

    class Meta:
        ordering = ['date_created']

    def __str__(self):
        return self.name


class MTGCollectionEntry(models.Model):
    """Model of a single entry of a `tccm.models.MTGCollection`."""
    collection = models.ForeignKey(MTGCollection, on_delete=models.CASCADE)
    card = models.ForeignKey(MTGCard, on_delete=models.CASCADE)
    count = models.PositiveSmallIntegerField("number of copies in the "
                                             "collection", default=1)
    foil_count = models.PositiveSmallIntegerField("number of foiled "
                                                  "copies in the collection.",
                                                  default=0)

    def __str__(self):
        return '{0} in {1}'.format(self.card.name, self.collection.name)
