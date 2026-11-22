from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    World,
    Faction, Character, ArtifactCategory, Artifact,
    AbilitySystem, Realm, SkillLevel, Skill,
    Creature, FragmentWorld, HistoricalEvent,
    Relationship, LorePage,
    OriginLaw, Anomaly,
)
from .serializers import (
    WorldSerializer,
    FactionSerializer, CharacterSerializer, ArtifactCategorySerializer,
    ArtifactSerializer, AbilitySystemSerializer, RealmSerializer,
    SkillLevelSerializer, SkillSerializer, CreatureSerializer,
    FragmentWorldSerializer, HistoricalEventSerializer,
    RelationshipSerializer, LorePageSerializer,
    OriginLawSerializer, AnomalySerializer,
)


# ============================================================
# Mixin: 支持 ?world=slug 按大世界 slug 过滤
# 前端统一发送 ?world=<slug>，后端自动 filter(world__slug=<slug>)
# 子类无需在 filterset_fields 中包含 'world'
# ============================================================
class WorldSlugFilterMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        world_slug = self.request.query_params.get('world')
        if world_slug:
            queryset = queryset.filter(world__slug=world_slug)
        return queryset


@api_view(['GET'])
def global_search(request):
    """跨模块搜索 API（按大世界 slug 过滤）"""
    query = request.GET.get('q', '').strip()
    if not query:
        return Response({'results': []})

    world_slug = request.GET.get('world')
    results = []

    # 搜索角色
    char_qs = Character.objects.filter(
        Q(name__icontains=query) | Q(aliases__icontains=query)
    )
    if world_slug:
        char_qs = char_qs.filter(world__slug=world_slug)
    for char in char_qs[:5]:
        results.append({
            'type': 'character', 'id': char.id, 'name': char.name,
            'subtitle': char.aliases or '', 'url': f'/characters/{char.id}'
        })

    # 搜索族群
    faction_qs = Faction.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query) | Q(leader__icontains=query)
    )
    if world_slug:
        faction_qs = faction_qs.filter(world__slug=world_slug)
    for faction in faction_qs[:5]:
        results.append({
            'type': 'faction', 'id': faction.id, 'name': faction.name,
            'subtitle': faction.leader or '', 'url': f'/factions/{faction.id}'
        })

    # 搜索宝物
    artifact_qs = Artifact.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query)
    )
    if world_slug:
        artifact_qs = artifact_qs.filter(world__slug=world_slug)
    for artifact in artifact_qs[:5]:
        results.append({
            'type': 'artifact', 'id': artifact.id, 'name': artifact.name,
            'subtitle': artifact.origin or '', 'url': f'/artifacts/{artifact.id}'
        })

    # 搜索碎片世界
    fw_qs = FragmentWorld.objects.filter(
        Q(name__icontains=query) | Q(dominant_law__icontains=query)
    )
    if world_slug:
        fw_qs = fw_qs.filter(world__slug=world_slug)
    for world in fw_qs[:5]:
        results.append({
            'type': 'fragment-world', 'id': world.id, 'name': world.name,
            'subtitle': world.dominant_law or '', 'url': f'/fragment-worlds/{world.id}'
        })

    # 搜索异兽
    creature_qs = Creature.objects.filter(
        Q(name__icontains=query) | Q(species__icontains=query)
    )
    if world_slug:
        creature_qs = creature_qs.filter(world__slug=world_slug)
    for creature in creature_qs[:5]:
        results.append({
            'type': 'creature', 'id': creature.id, 'name': creature.name,
            'subtitle': creature.species or '', 'url': f'/creatures/{creature.id}'
        })

    # 搜索本源法则
    law_qs = OriginLaw.objects.filter(
        Q(name__icontains=query) | Q(core_definition__icontains=query)
    )
    if world_slug:
        law_qs = law_qs.filter(world__slug=world_slug)
    for law in law_qs[:5]:
        results.append({
            'type': 'origin-law', 'id': law.id, 'name': law.name,
            'subtitle': law.get_tier_display() or '', 'url': f'/origin-laws/{law.id}'
        })

    # 搜索异常物
    anomaly_qs = Anomaly.objects.filter(
        Q(name__icontains=query) | Q(ability__icontains=query)
    )
    if world_slug:
        anomaly_qs = anomaly_qs.filter(world__slug=world_slug)
    for anomaly in anomaly_qs[:5]:
        results.append({
            'type': 'anomaly', 'id': anomaly.id, 'name': anomaly.name,
            'subtitle': f'{anomaly.danger_level}级 {anomaly.law_attribute}', 'url': f'/anomalies/{anomaly.id}'
        })

    return Response({'results': results})


@api_view(['GET'])
def world_stats(request):
    """世界观统计数据 API（按大世界 slug 过滤）"""
    world_slug = request.GET.get('world')
    filter_kwargs = {}
    if world_slug:
        filter_kwargs['world__slug'] = world_slug
    stats = {
        'factions': Faction.objects.filter(**filter_kwargs).count(),
        'characters': Character.objects.filter(**filter_kwargs).count(),
        'artifacts': Artifact.objects.filter(**filter_kwargs).count(),
        'fragment_worlds': FragmentWorld.objects.filter(**filter_kwargs).count(),
        'creatures': Creature.objects.filter(**filter_kwargs).count(),
        'realms': Realm.objects.filter(**filter_kwargs).count(),
        'skills': Skill.objects.filter(**filter_kwargs).count(),
        'historical_events': HistoricalEvent.objects.filter(**filter_kwargs).count(),
        'lore_pages': LorePage.objects.filter(**filter_kwargs).count(),
        'origin_laws': OriginLaw.objects.filter(**filter_kwargs).count(),
        'anomalies': Anomaly.objects.filter(**filter_kwargs).count(),
    }
    return Response(stats)


class WorldViewSet(viewsets.ModelViewSet):
    queryset = World.objects.all()
    serializer_class = WorldSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']
    lookup_field = 'slug'


class FactionViewSet(WorldSlugFilterMixin, viewsets.ModelViewSet):
    queryset = Faction.objects.all()
    serializer_class = FactionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['level', 'type', 'parent_faction']
    search_fields = ['name', 'description', 'leader']


class CharacterViewSet(WorldSlugFilterMixin, viewsets.ModelViewSet):
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['faction', 'realm_tier', 'status']
    search_fields = ['name', 'aliases']


class ArtifactCategoryViewSet(WorldSlugFilterMixin, viewsets.ModelViewSet):
    queryset = ArtifactCategory.objects.all()
    serializer_class = ArtifactCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['rarity_level']
    search_fields = ['name']


class ArtifactViewSet(WorldSlugFilterMixin, viewsets.ModelViewSet):
    queryset = Artifact.objects.all()
    serializer_class = ArtifactSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'owner', 'rarity_level']
    search_fields = ['name', 'description', 'origin']


class AbilitySystemViewSet(WorldSlugFilterMixin, viewsets.ModelViewSet):
    queryset = AbilitySystem.objects.all()
    serializer_class = AbilitySystemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = []
    search_fields = ['name', 'description']


class RealmViewSet(WorldSlugFilterMixin, viewsets.ModelViewSet):
    queryset = Realm.objects.all()
    serializer_class = RealmSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tier', 'system']
    search_fields = ['name']


class SkillLevelViewSet(WorldSlugFilterMixin, viewsets.ModelViewSet):
    queryset = SkillLevel.objects.all()
    serializer_class = SkillLevelSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['system']
    search_fields = ['name']


class SkillViewSet(WorldSlugFilterMixin, viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['level']
    search_fields = ['name', 'description']


class CreatureViewSet(WorldSlugFilterMixin, viewsets.ModelViewSet):
    queryset = Creature.objects.all()
    serializer_class = CreatureSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['danger_level', 'habitat']
    search_fields = ['name', 'species']


class FragmentWorldViewSet(WorldSlugFilterMixin, viewsets.ModelViewSet):
    queryset = FragmentWorld.objects.all()
    serializer_class = FragmentWorldSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['danger_level', 'number_id']
    search_fields = ['name', 'dominant_law']


class HistoricalEventViewSet(WorldSlugFilterMixin, viewsets.ModelViewSet):
    queryset = HistoricalEvent.objects.all()
    serializer_class = HistoricalEventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['era']
    search_fields = ['name', 'description']


class RelationshipViewSet(viewsets.ModelViewSet):
    """关系网络：无 world 外键，通过 from_character 的 world 过滤"""
    queryset = Relationship.objects.all()
    serializer_class = RelationshipSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['from_character', 'to_character', 'relation_type']
    search_fields = ['description']

    def get_queryset(self):
        queryset = super().get_queryset()
        world_slug = self.request.query_params.get('world')
        if world_slug:
            queryset = queryset.filter(from_character__world__slug=world_slug)
        return queryset


class LorePageViewSet(WorldSlugFilterMixin, viewsets.ModelViewSet):
    queryset = LorePage.objects.all()
    serializer_class = LorePageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']
    search_fields = ['title', 'slug']
    lookup_field = 'slug'


class OriginLawViewSet(WorldSlugFilterMixin, viewsets.ModelViewSet):
    queryset = OriginLaw.objects.all()
    serializer_class = OriginLawSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tier']
    search_fields = ['name', 'core_definition', 'ability_directions']


class AnomalyViewSet(WorldSlugFilterMixin, viewsets.ModelViewSet):
    queryset = Anomaly.objects.all()
    serializer_class = AnomalySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['danger_level', 'function_type', 'law_attribute']
    search_fields = ['name', 'ability', 'appearance']
