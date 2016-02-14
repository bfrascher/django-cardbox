from django.contrib import admin

from mtgcardbox.models import (
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
    list_display = ('last_name', 'first_name',)
    search_fields = ('^last_name', '^first_name',)


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


@admin.register(Ruling)
class RulingAdmin(admin.ModelAdmin):
    search_fields = ('ruling',)
    list_display = ('date', 'ruling',)


class CardEditionInline(admin.TabularInline):
    model = CardEdition
    extra = 1
    fieldsets = (
        ('Set', {
            'fields': ('mtgset', 'number', 'number_suffix',),
        }),
        ('Artist', {
            'fields': ('artist',),
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
        ('Rarity', {
            'fields': ('rarity',),
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
        ('Artist', {
            'fields': ('artist',),
        }),
    )
    filter_horizontal = ('rulings',)
    list_display = ('name', 'types', 'cmc', 'power', 'toughness', 'rarity',)
    list_filter = ('rarity', 'multi_type', 'sets',)
    search_fields = ('name', 'types',)


class CollectionEntryInline(admin.TabularInline):
    model = CollectionEntry
    extra = 1
    fieldsets = (
        ('Collection Entry', {
            'fields': ('count', 'foil_count', 'card',),
        }),
    )


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    inlines = (CollectionEntryInline,)
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
