from django.contrib import admin

from .models import (
    Artist,
    MTGRuling,
    MTGBlock,
    MTGSet,
    MTGCard,
    MTGCardEdition,
    MTGCollection,
    MTGCollectionEntry,
)


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name')
    search_fields = ('^last_name', '^first_name')


@admin.register(MTGBlock)
class MTGBlockAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'category')
    fieldsets = (
        (None, {
            'fields': ('category', 'name',),
        }),
    )


@admin.register(MTGSet)
class MTGSetAdmin(admin.ModelAdmin):
    search_fields = ('name', '^code')
    list_display = ('name', 'code', 'release_date', 'block')


@admin.register(MTGRuling)
class MRGRulingAdmin(admin.ModelAdmin):
    search_fields = ('ruling',)
    list_display = ('date', 'ruling',)


class MTGCardEditionInline(admin.TabularInline):
    model = MTGCardEdition
    extra = 1
    fieldsets = (
        ('Set', {
            'fields': ('mtgset', 'number', 'number_suffix',),
        }),
    )


@admin.register(MTGCard)
class MTGCardAdmin(admin.ModelAdmin):
    inlines = (MTGCardEditionInline,)
    fieldsets = (
        (None, {
            'fields': ('multiverseid',),
        }),
        ('Card', {
            'fields': ('name', 'types', 'rules', 'flavour')
        }),
        ('Mana', {
            'fields': (('mana_n', 'mana_w', 'mana_u', 'mana_b', 'mana_r',
                       'mana_g', 'mana_c'), ('mana_special', 'cmc'))
        }),
        ('Stats', {
            'fields': (('power', 'toughness', 'loyalty'),
                       ('power_special', 'toughness_special',
                       'loyalty_special'))
        }),
        ('Rarity', {
            'fields': ['rarity']
        }),
        ('Dual Card', {
            'classes': ('collapse',),
            'fields': [('dual_type', 'dual_card')]
        }),
        ('Legality', {
            'classes': ('collapse',),
            'fields': [('legal_vintage', 'legal_legacy', 'legal_extended',
                        'legal_standard', 'legal_classic', 'legal_commander',
                        'legal_modern')]
        }),
        ('Rulings', {
            'classes': ('collapse',),
            'fields': ['rulings']
        }),
        ('Artist', {
            'fields': ['artist']
        }),
    )
    filter_horizontal = ('rulings',)
    list_display = ('name', 'types', 'cmc', 'power', 'toughness', 'rarity',)
    list_filter = ('rarity', 'dual_type', 'sets',)
    search_fields = ('name', 'types',)


class MTGCollectionEntryInline(admin.TabularInline):
    model = MTGCollectionEntry
    extra = 1
    fieldsets = (
        ('Collection Entry', {
            'fields': ('count', 'foil_count', 'card'),
        }),
    )


@admin.register(MTGCollection)
class MTGCollectionAdmin(admin.ModelAdmin):
    inlines = (MTGCollectionEntryInline,)
    fieldsets = (
        (None, {
            'fields': ('name', 'owner', 'date_created'),
        }),
        ('Share', {
            'classes': ('collapse',),
            'fields': ('viewers', 'editors',)
        }),
    )
    filter_horizontal = ('viewers', 'editors',)
    list_display = ('name', 'owner', 'date_created')
