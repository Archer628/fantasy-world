from django.contrib import admin
from .models import (
    World,
    Faction, Character, ArtifactCategory, Artifact,
    AbilitySystem, Realm, SkillLevel, Skill,
    Creature, FragmentWorld, HistoricalEvent,
    Relationship, LorePage,
    OriginLaw, Anomaly,
)


@admin.register(World)
class WorldAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'subtitle', 'is_active', 'order')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('is_active',)


@admin.register(Faction)
class FactionAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'type', 'parent_faction', 'population', 'leader')
    list_filter = ('level', 'type')
    search_fields = ('name', 'leader', 'territory')
    prepopulated_fields = {}


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ('name', 'faction', 'realm_tier', 'realm_order', 'status')
    list_filter = ('realm_tier', 'status', 'faction')
    search_fields = ('name', 'aliases')
    filter_horizontal = ('abilities', 'weapons', 'artifacts')


@admin.register(ArtifactCategory)
class ArtifactCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'rarity_level')
    list_filter = ('rarity_level',)
    search_fields = ('name',)


@admin.register(Artifact)
class ArtifactAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'rarity_level', 'owner', 'location')
    list_filter = ('rarity_level', 'category')
    search_fields = ('name', 'origin', 'effects')


@admin.register(AbilitySystem)
class AbilitySystemAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'description')


@admin.register(Realm)
class RealmAdmin(admin.ModelAdmin):
    list_display = ('name', 'tier', 'level_order', 'system')
    list_filter = ('tier', 'system')
    search_fields = ('name',)
    ordering = ('tier', 'level_order')


@admin.register(SkillLevel)
class SkillLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'level_order', 'system')
    list_filter = ('system',)
    search_fields = ('name',)
    ordering = ('level_order',)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'cooldown')
    list_filter = ('level',)
    search_fields = ('name', 'description')


@admin.register(Creature)
class CreatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'danger_level', 'habitat')
    list_filter = ('danger_level',)
    search_fields = ('name', 'species')


@admin.register(FragmentWorld)
class FragmentWorldAdmin(admin.ModelAdmin):
    list_display = ('name', 'number_id', 'dominant_law', 'danger_level', 'max_faction')
    list_filter = ('danger_level',)
    search_fields = ('name', 'dominant_law', 'max_faction')
    ordering = ('number_id',)


@admin.register(HistoricalEvent)
class HistoricalEventAdmin(admin.ModelAdmin):
    list_display = ('name', 'era', 'date_description')
    list_filter = ('era',)
    search_fields = ('name', 'description')
    filter_horizontal = ('involved_factions', 'involved_characters')


@admin.register(Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    list_display = ('from_character', 'relation_type', 'to_character')
    list_filter = ('relation_type',)
    search_fields = ('from_character__name', 'to_character__name', 'description')


@admin.register(LorePage)
class LorePageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'category', 'order')
    list_filter = ('category',)
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('related_terms',)


@admin.register(OriginLaw)
class OriginLawAdmin(admin.ModelAdmin):
    list_display = ('name', 'tier', 'order')
    list_filter = ('tier',)
    search_fields = ('name', 'core_definition', 'ability_directions')
    ordering = ('order',)


@admin.register(Anomaly)
class AnomalyAdmin(admin.ModelAdmin):
    list_display = ('name', 'danger_level', 'law_attribute', 'function_type')
    list_filter = ('danger_level', 'function_type')
    search_fields = ('name', 'ability', 'appearance')
