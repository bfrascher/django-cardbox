from django.contrib import admin

from cardbox.models import (
    Artist,
    Ruling,
    Block,
    Set,
    Card,
    CardEdition,
    Collection,
    CollectionEntry,
)


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'category',)
    fieldsets = (
        (None, {
            'fields': ('category', 'name',),
        }),
    )


@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    search_fields = ('name', '^code',)
    list_display = ('name', 'code', 'release_date', 'block',)
    list_filter = ('block',)


@admin.register(Ruling)
class RulingAdmin(admin.ModelAdmin):
    search_fields = ('ruling',)
    list_display = ('date', 'ruling',)


class CardEditionInline(admin.TabularInline):
    model = CardEdition
    extra = 1
    fieldsets = (
        ('Set', {
            'fields': ('mtgset', 'number', 'number_suffix', 'rarity', 'artist'),
        }),
    )


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    inlines = (CardEditionInline,)
    fieldsets = (
        (None, {
            'fields': ('multiverseid',),
        }),
        ('Card', {
            'fields': ('name', 'types', 'rules', 'flavour',),
        }),
        ('Mana', {
            'fields': (('mana_n', 'mana_w', 'mana_u', 'mana_b', 'mana_r',
                        'mana_g', 'mana_c',), ('mana_special', 'cmc',),),
        }),
        ('Stats', {
            'fields': (('power', 'toughness', 'loyalty',),
                       ('power_special', 'toughness_special',
                        'loyalty_special',),),
        }),
        ('Multi Card', {
            'classes': ('collapse',),
            'fields': ('multi_type','multi_cards',),
        }),
        ('Legality', {
            'classes': ('collapse',),
            'fields': (('legal_vintage', 'legal_legacy', 'legal_extended',
                        'legal_standard', 'legal_classic', 'legal_commander',
                        'legal_modern'),),
        }),
        ('Rulings', {
            'classes': ('collapse',),
            'fields': ('rulings',),
        }),
    )
    filter_horizontal = ('rulings', 'multi_cards',)
    list_display = ('name', 'types', 'cmc', 'power', 'toughness',)
    list_filter = ('multi_type', 'sets',)
    search_fields = ('name', 'types',)


class CollectionEntryInline(admin.TabularInline):
    model = CollectionEntry
    extra = 1
    fieldsets = (
        ('Collection Entry', {
            'fields': ('count', 'foil_count', 'edition',),
        }),
    )


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'owner', 'date_created',),
        }),
        ('Share', {
            'classes': ('collapse',),
            'fields': ('viewers', 'editors',),
        }),
    )
    filter_horizontal = ('viewers', 'editors',)
    list_display = ('name', 'owner', 'date_created',)
