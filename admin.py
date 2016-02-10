from django.contrib import admin

from .models import (
    Artist,
    MTGBlock,
    MTGSet,
    MTGCard,
    MTGRuling,
    MTGCollection,
#    MTGCollectionEntry,
)


# Register your models here.
admin.site.register(Artist)
admin.site.register(MTGBlock)
admin.site.register(MTGSet)
admin.site.register(MTGCard)
admin.site.register(MTGRuling)
admin.site.register(MTGCollection)
