from django.db import models


class Artist(models.Model):
    """Simple model for an artist.  Referenced in `tccm.models.MTGCard`"""
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=100)


class MTGBlock(models.Model):
    """Model for a block in Magic The Gathering.  Used to group
    `tccm.models.MTGSet`.

    """
    name = models.CharField(max_length=100)


class MTGSet(models.Model):
    """Model for a Magic The Gathering set/expansion.  Used to group
    `tcc.models.MTGCard`.

    """
    block_id = models.ForeignKey(MTGBlock, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)


class MTGCard(models.Model):
    """Model for a card in Magic The Gathering."""
    pass


class MTGRulings(models.Model):
    """Model for rulings that affect certain `tccm.models.MTGCard`s."""
    pass


class MTGCollection(models.Model):
    """Model of a shareable collection of `tccm.models.MTGCard`s."""
    pass


class MTGCollectionEntry(models.Model):
    """Model of a single entry of a `tccm.models.MTGCollection`."""
