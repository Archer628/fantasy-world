from rest_framework import serializers
from .models import (
    World,
    Faction, Character, ArtifactCategory, Artifact,
    AbilitySystem, Realm, SkillLevel, Skill,
    Creature, FragmentWorld, HistoricalEvent,
    Relationship, LorePage,
    OriginLaw, Anomaly,
)


class WorldSerializer(serializers.ModelSerializer):
    class Meta:
        model = World
        fields = '__all__'


# ============================================================
# Faction 相关嵌套序列化器（轻量版，供 parent / sub_factions / race / faction 字段复用）
# ============================================================
class _FactionSimpleNested(serializers.ModelSerializer):
    """Faction 最简嵌套：用于 FactionSerializer.parent 字段"""
    grade = serializers.CharField(source='level', read_only=True, default='')

    class Meta:
        model = Faction
        fields = ('id', 'name', 'category', 'type', 'grade')


class _FactionSubNested(serializers.ModelSerializer):
    """Faction 子势力嵌套：用于 FactionSerializer.sub_factions 字段"""
    grade = serializers.CharField(source='level', read_only=True, default='')

    class Meta:
        model = Faction
        fields = ('id', 'name', 'category', 'type', 'grade', 'description')


class _FactionWithParentNested(serializers.ModelSerializer):
    """Faction 带 parent_id 嵌套：用于 CharacterSerializer.race / faction 字段"""
    grade = serializers.CharField(source='level', read_only=True, default='')
    parent_id = serializers.IntegerField(source='parent_faction_id', read_only=True, default=None)

    class Meta:
        model = Faction
        fields = ('id', 'name', 'category', 'type', 'grade', 'parent_id')


# ============================================================
# FactionSerializer 主序列化器
# ============================================================
class FactionSerializer(serializers.ModelSerializer):
    parent = _FactionSimpleNested(source='parent_faction', read_only=True, default=None)
    sub_factions = _FactionSubNested(many=True, read_only=True)
    race_members = serializers.SerializerMethodField(read_only=True)
    force_members = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Faction
        fields = '__all__'

    # ---------- 辅助：递归获取自身 + 所有后代 sub_factions 的 id 集合 ----------
    def _collect_descendant_ids(self, faction, acc=None):
        if acc is None:
            acc = set()
        if faction is None or faction.id is None:
            return acc
        if faction.id in acc:  # 防止循环引用
            return acc
        acc.add(faction.id)
        for child in faction.sub_factions.all().only('id'):
            self._collect_descendant_ids(child, acc)
        return acc

    # ---------- race_members：种族（含子种族）的成员列表，最多 50 条，按境界排序 ----------
    def get_race_members(self, obj):
        if obj.category != 'race':
            return []
        ids = self._collect_descendant_ids(obj)
        if not ids:
            return []
        TIER_RANK = {'sage': 4, 'heaven': 3, 'spirit': 2, 'mortal': 1}
        qs = Character.objects.filter(race_id__in=ids).only(
            'id', 'name', 'aliases', 'realm_tier', 'realm_order', 'status'
        )
        chars = list(qs)
        chars.sort(key=lambda c: (
            -TIER_RANK.get(c.realm_tier, 0),
            -(c.realm_order or 0),
        ))
        chars = chars[:50]
        return [
            {
                'id': c.id,
                'name': c.name,
                'aliases': c.aliases or '',
                'realm_tier': c.realm_tier,
                'realm_order': c.realm_order,
                'status': c.status,
            }
            for c in chars
        ]

    # ---------- force_members：势力（含子势力）的成员列表，最多 50 条，按势力身份+境界排序 ----------
    def get_force_members(self, obj):
        if obj.category != 'force':
            return []
        ids = self._collect_descendant_ids(obj)
        if not ids:
            return []
        TIER_RANK = {'sage': 4, 'heaven': 3, 'spirit': 2, 'mortal': 1}
        qs = Character.objects.filter(faction_id__in=ids).only(
            'id', 'name', 'aliases', 'faction_role', 'realm_tier', 'realm_order', 'status'
        )
        chars = list(qs)
        chars.sort(key=lambda c: (
            (c.faction_role or ''),                # 先按势力身份字典序
            -TIER_RANK.get(c.realm_tier, 0),       # 再按境界（高→低）
            -(c.realm_order or 0),                 # 再按境界阶数（高→低）
        ))
        chars = chars[:50]
        return [
            {
                'id': c.id,
                'name': c.name,
                'aliases': c.aliases or '',
                'faction_role': c.faction_role or '',
                'realm_tier': c.realm_tier,
                'realm_order': c.realm_order,
                'status': c.status,
            }
            for c in chars
        ]


class AbilitySystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbilitySystem
        fields = '__all__'


class RealmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Realm
        fields = '__all__'


class SkillLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillLevel
        fields = '__all__'


class ArtifactCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtifactCategory
        fields = '__all__'


class ArtifactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artifact
        fields = '__all__'


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'


# ============================================================
# CharacterSerializer 主序列化器
# ============================================================
class CharacterSerializer(serializers.ModelSerializer):
    # ----- race / faction 嵌套只读输出 -----
    race = _FactionWithParentNested(read_only=True, default=None)
    faction = _FactionWithParentNested(read_only=True, default=None)

    # ----- race_id / faction_id 写入字段（整数，write_only，字段名与模型列一致，故无需 source） -----
    race_id = serializers.IntegerField(write_only=True, required=False)
    faction_id = serializers.IntegerField(write_only=True, required=False)

    # ----- 直接可读字段 -----
    race_name = serializers.CharField(source='race.name', read_only=True, default='')
    faction_name = serializers.CharField(source='faction.name', read_only=True, default='')
    # faction_role / power_progression 作为模型字段已由 __all__ 自动包含，此处无需重复声明
    realm = serializers.CharField(source='get_realm_tier_display', read_only=True, default='')
    realm_level = serializers.IntegerField(source='realm_order', read_only=True, default=0)

    # ----- 能力/武器/宝物嵌套输出（保留原逻辑） -----
    abilities = SkillSerializer(many=True, read_only=True)
    weapons = ArtifactSerializer(many=True, read_only=True)
    artifacts = ArtifactSerializer(many=True, read_only=True)

    class Meta:
        model = Character
        fields = '__all__'


class FragmentWorldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FragmentWorld
        fields = '__all__'


class CreatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Creature
        fields = '__all__'


class HistoricalEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalEvent
        fields = '__all__'


class RelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relationship
        fields = '__all__'


class LorePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LorePage
        fields = '__all__'


class OriginLawSerializer(serializers.ModelSerializer):
    class Meta:
        model = OriginLaw
        fields = '__all__'


class AnomalySerializer(serializers.ModelSerializer):
    class Meta:
        model = Anomaly
        fields = '__all__'
