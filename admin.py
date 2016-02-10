from django.contrib import admin

from .models import (
    Artist,
    MTGBlock,
    MTGSet,
    MTGCard,
    MTGToken,
    MTGRuling,
    MTGCollection,
)


@admin.register(MTGCard)
class MTGCardAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Set', {
            'fields': ('multiverseid', ('mtgset', 'set_number',
                                        'set_number_suffix'))
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
    filter_horizontal = ['rulings']
    list_display = ('name', 'types', 'cmc', 'power', 'toughness', 'rarity',
                    'mtgset')
    list_filter = ('rarity', 'mtgset', 'dual_type',
                   'legal_standard', 'legal_modern')
    search_fields = ('name', 'types')


@admin.register(MTGCollection)
class MTGCollectionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'owner', 'date_created'),
        }),
        ('Share', {
            'classes': ('collapse',),
            'fields': ('viewers', 'editors',)
        }),
        ('Basic Lands', {
            'classes': ('collapse',),
            'fields': (('lands_plains', 'lands_island', 'lands_swamp',
                        'lands_mountain', 'lands_forest', 'lands_wastes'),),
        }),
    )
    filter_horizontal = ('viewers', 'editors',)
    list_display = ('name', 'owner', 'date_created')


# Register your models here.
admin.site.register(Artist)
admin.site.register(MTGBlock)
admin.site.register(MTGSet)
# admin.site.register(MTGCard)
admin.site.register(MTGRuling)
# admin.site.register(MTGCollection)
admin.site.register(MTGToken)
