"""
Django management command: seed_data
注入两个大世界（残响界、深骸）的完整数据

Usage:
    python manage.py seed_data
    python manage.py seed_data --force
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from worldbook.models import (
    World,
    FragmentWorld,
    Faction,
    Character,
    ArtifactCategory,
    Artifact,
    AbilitySystem,
    Realm,
    SkillLevel,
    Skill,
    Creature,
    HistoricalEvent,
    Relationship,
    LorePage,
    OriginLaw,
    Anomaly,
)


# ============================================================
# Models that have a world FK (for clearing)
# ============================================================
WORLD_FK_MODELS = [
    Skill,
    Artifact,
    Creature,
    Realm,
    Character,
    HistoricalEvent,
    LorePage,
    FragmentWorld,
    Faction,
    SkillLevel,
    ArtifactCategory,
    AbilitySystem,
    Anomaly,
    OriginLaw,
]


class Command(BaseCommand):
    help = '注入两个大世界（残响界、深骸）的完整数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制更新已有数据（默认跳过已存在的记录）',
        )

    def handle(self, *args, **options):
        force = options['force']
        stats = {}

        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('  双世界数据注入 - 残响界 + 深骸'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

        with transaction.atomic():
            # 1. Create worlds
            canxiang_world, shenhai_world = self._seed_worlds(stats)

            # 2. Clear 深骸 old data
            self._clear_shenhai_data(shenhai_world)

            # 3. Seed 残响界 data (existing data + world association)
            self._seed_canxiang_all(stats, canxiang_world, force)

            # 4. Seed 深骸 data (new data)
            self._seed_shenhai_all(stats, shenhai_world)

        # Print summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('-' * 60))
        self.stdout.write(self.style.SUCCESS('  数据注入完成 - 统计信息'))
        self.stdout.write(self.style.SUCCESS('-' * 60))

        total_created = 0
        total_updated = 0
        labels = {
            'worlds': '大世界',
            'fragment_worlds': '碎片世界',
            'factions': '族群/势力',
            'characters': '角色',
            'artifact_categories': '宝物种类',
            'artifacts': '宝物',
            'ability_systems': '能力体系',
            'realms': '境界等级',
            'skill_levels': '技能等级',
            'skills': '技能',
            'creatures': '异兽',
            'historical_events': '历史事件',
            'relationships': '关系网络',
            'lore_pages': '设定页面',
            'origin_laws': '本源法则',
            'anomalies': '异常物',
        }
        for key, label in labels.items():
            created, updated, skipped = stats.get(key, (0, 0, 0))
            total_created += created
            total_updated += updated
            if created or updated or skipped:
                self.stdout.write(
                    f'  {label}: '
                    f'{self.style.SUCCESS(str(created) + " 创建")}, '
                    f'{self.style.WARNING(str(updated) + " 更新")}, '
                    f'{skipped} 跳过'
                )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'  共创建 {total_created} 条记录, 更新 {total_updated} 条记录'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _upsert(self, model, stats_key, stats, lookup_fields, defaults, force):
        """
        Generic upsert helper.
        Always updates the 'world' field if provided and different.
        """
        query = Q(**lookup_fields)
        obj = model.objects.filter(query).first()
        if obj:
            # Always ensure world is set (migration from no-world to world)
            world_val = defaults.get('world')
            if world_val is not None and obj.world_id != world_val.id:
                obj.world = world_val
                obj.save(update_fields=['world'])
            if force:
                for k, v in defaults.items():
                    setattr(obj, k, v)
                obj.save()
                self._inc_stats(stats, stats_key, updated=True)
                return obj, False, True
            else:
                self._inc_stats(stats, stats_key, skipped=True)
                return obj, False, False
        else:
            merged = {**lookup_fields, **defaults}
            obj = model(**merged)
            obj.save()
            self._inc_stats(stats, stats_key, created=True)
            return obj, True, False

    def _inc_stats(self, stats, key, created=False, updated=False, skipped=False):
        if key not in stats:
            stats[key] = [0, 0, 0]  # [created, updated, skipped]
        if created:
            stats[key][0] += 1
        if updated:
            stats[key][1] += 1
        if skipped:
            stats[key][2] += 1

    # ------------------------------------------------------------------
    # 0. Create Worlds
    # ------------------------------------------------------------------
    def _seed_worlds(self, stats):
        worlds = [
            {
                'name': '残响界',
                'slug': 'canxiangjie',
                'subtitle': '世界观设定档案库 V3.0',
                'description': '由碎片构成的世界，诸神陨落，万族林立。',
                'tone': '宇宙史诗、宿命压抑',
                'is_active': True,
                'order': 1,
            },
            {
                'name': '深骸',
                'slug': 'shenhai',
                'subtitle': '法则共鸣·碎片纪元',
                'description': '深骸是诞生于宇宙原初混沌的法则聚合型至高生命体。高维概念打击致其碎裂，巨型残躯跃迁撞击地球，撕裂为18块碎片世界。碎片世界总面积约7.65亿km²，总人口约2.5亿。每块碎片被单一或双本源法则深度浸染，地貌生态完全区分。人类作为深骸的共生免疫细胞，在法则共鸣中抗争求存。',
                'tone': '宇宙史诗、宿命压抑、共生博弈、不可名状高维恐怖',
                'is_active': True,
                'order': 2,
            },
        ]
        result = []
        for w in worlds:
            obj, created, updated = self._upsert(
                World, 'worlds', stats,
                {'slug': w['slug']},
                {k: v for k, v in w.items() if k != 'slug'},
                True,  # Always force-update worlds
            )
            result.append(obj)
        return result[0], result[1]

    # ------------------------------------------------------------------
    # Clear 深骸 old data
    # ------------------------------------------------------------------
    def _clear_shenhai_data(self, shenhai_world):
        self.stdout.write(self.style.WARNING('  清除深骸世界旧数据...'))
        for model in WORLD_FK_MODELS:
            count = model.objects.filter(world=shenhai_world).count()
            if count > 0:
                model.objects.filter(world=shenhai_world).delete()
                self.stdout.write(f'    {model.__name__}: 清除 {count} 条')

    # ================================================================
    # 残响界 DATA
    # ================================================================
    def _seed_canxiang_all(self, stats, world, force):
        self.stdout.write(self.style.SUCCESS('  --- 残响界数据注入 ---'))
        self._seed_canxiang_fragment_worlds(stats, world, force)
        self._seed_canxiang_factions(stats, world, force)
        self._seed_canxiang_ability_system(stats, world, force)
        self._seed_canxiang_realms(stats, world, force)
        self._seed_canxiang_skill_levels(stats, world, force)
        self._seed_canxiang_characters(stats, world, force)
        self._seed_canxiang_artifact_categories(stats, world, force)
        self._seed_canxiang_artifacts(stats, world, force)
        self._seed_canxiang_skills(stats, world, force)
        self._seed_canxiang_creatures(stats, world, force)
        self._seed_canxiang_historical_events(stats, world, force)
        self._seed_canxiang_relationships(stats, world, force)
        self._seed_canxiang_lore_pages(stats, world, force)
        self._link_canxiang_character_skills_and_artifacts(stats)

    def _seed_canxiang_fragment_worlds(self, stats, world, force):
        worlds = [
            {'number_id': 1, 'name': '残响界·起源', 'area': '500万km²', 'population': 300000000, 'dominant_law': '时间残响', 'danger_level': 3, 'max_faction': '残响议会', 'faction_level': 'S', 'strongest_power': '神境三阶'},
            {'number_id': 2, 'name': '苍穹之冠', 'area': '300万km²', 'population': 150000000, 'dominant_law': '风之律动', 'danger_level': 2, 'max_faction': '苍穹骑士团', 'faction_level': 'A', 'strongest_power': '灵境九阶'},
            {'number_id': 3, 'name': '深渊裂隙', 'area': '200万km²', 'population': 50000000, 'dominant_law': '暗影吞噬', 'danger_level': 5, 'max_faction': '深渊教团', 'faction_level': 'S', 'strongest_power': '神境一阶'},
            {'number_id': 4, 'name': '翡翠秘境', 'area': '150万km²', 'population': 80000000, 'dominant_law': '生命繁衍', 'danger_level': 2, 'max_faction': '翡翠议会', 'faction_level': 'A', 'strongest_power': '灵境八阶'},
            {'number_id': 5, 'name': '熔岩核心', 'area': '180万km²', 'population': 60000000, 'dominant_law': '火焰锻造', 'danger_level': 4, 'max_faction': '熔炉氏族', 'faction_level': 'B', 'strongest_power': '灵境七阶'},
            {'number_id': 6, 'name': '冰晶荒原', 'area': '400万km²', 'population': 30000000, 'dominant_law': '冰封静止', 'danger_level': 3, 'max_faction': '霜语者同盟', 'faction_level': 'B', 'strongest_power': '灵境六阶'},
            {'number_id': 7, 'name': '雷鸣高原', 'area': '250万km²', 'population': 70000000, 'dominant_law': '雷霆审判', 'danger_level': 3, 'max_faction': '雷神社', 'faction_level': 'A', 'strongest_power': '灵境九阶'},
            {'number_id': 8, 'name': '幻梦之沼', 'area': '100万km²', 'population': 20000000, 'dominant_law': '梦境编织', 'danger_level': 4, 'max_faction': '织梦者', 'faction_level': 'C', 'strongest_power': '灵境五阶'},
            {'number_id': 9, 'name': '星辰废墟', 'area': '350万km²', 'population': 10000000, 'dominant_law': '星光残响', 'danger_level': 5, 'max_faction': '无固定势力', 'faction_level': '无', 'strongest_power': '未知'},
            {'number_id': 10, 'name': '铁血战场', 'area': '220万km²', 'population': 40000000, 'dominant_law': '战争狂热', 'danger_level': 4, 'max_faction': '铁血军团', 'faction_level': 'B', 'strongest_power': '灵境七阶'},
            {'number_id': 11, 'name': '碧波深渊', 'area': '380万km²', 'population': 90000000, 'dominant_law': '水之潮汐', 'danger_level': 3, 'max_faction': '深海王庭', 'faction_level': 'A', 'strongest_power': '灵境八阶'},
            {'number_id': 12, 'name': '黄昏之地', 'area': '160万km²', 'population': 30000000, 'dominant_law': '衰亡法则', 'danger_level': 4, 'max_faction': '黄昏隐修会', 'faction_level': 'C', 'strongest_power': '灵境六阶'},
            {'number_id': 13, 'name': '机械之城', 'area': '120万km²', 'population': 50000000, 'dominant_law': '机械进化', 'danger_level': 2, 'max_faction': '齿轮议会', 'faction_level': 'A', 'strongest_power': '灵境七阶'},
            {'number_id': 14, 'name': '灵魂荒野', 'area': '280万km²', 'population': 20000000, 'dominant_law': '灵魂共振', 'danger_level': 5, 'max_faction': '灵魂牧者', 'faction_level': 'B', 'strongest_power': '灵境八阶'},
            {'number_id': 15, 'name': '破碎王座', 'area': '90万km²', 'population': 10000000, 'dominant_law': '王权残响', 'danger_level': 4, 'max_faction': '王座守卫', 'faction_level': 'C', 'strongest_power': '灵境五阶'},
            {'number_id': 16, 'name': '迷雾森林', 'area': '200万km²', 'population': 40000000, 'dominant_law': '迷惑幻象', 'danger_level': 3, 'max_faction': '迷雾游侠', 'faction_level': 'C', 'strongest_power': '灵境四阶'},
            {'number_id': 17, 'name': '时光遗迹', 'area': '130万km²', 'population': 5000000, 'dominant_law': '时间回溯', 'danger_level': 5, 'max_faction': '时光守望者', 'faction_level': 'E', 'strongest_power': '神境二阶'},
            {'number_id': 18, 'name': '虚空之门', 'area': '50万km²', 'population': 1000000, 'dominant_law': '虚空吞噬', 'danger_level': 5, 'max_faction': '虚空教团', 'faction_level': 'S', 'strongest_power': '神境三阶'},
        ]
        for w in worlds:
            defaults = dict(w)
            defaults['world'] = world
            self._upsert(FragmentWorld, 'fragment_worlds', stats, {'name': w['name']}, defaults, force)

    def _seed_canxiang_factions(self, stats, world, force):
        factions = [
            {'name': '残响议会', 'level': 'S', 'type': 'light', 'territory': '残响界·起源', 'population': 50000000, 'leader': '林雾', 'description': '残响界最强势力，掌控时间残响法则的核心组织。议会由七位神境强者组成，维系着整个碎片世界的秩序。'},
            {'name': '深渊教团', 'level': 'S', 'type': 'dark', 'territory': '深渊裂隙', 'population': 8000000, 'leader': '暗影主宰', 'description': '信奉深渊之力的神秘教团，掌控暗影吞噬法则。在暗处操纵着多个碎片世界的局势。'},
            {'name': '苍穹骑士团', 'level': 'A', 'type': 'light', 'territory': '苍穹之冠', 'population': 20000000, 'leader': '风翔将军', 'description': '以风之律动为核心的骑士团，崇尚自由与正义。成员多为风系异能者。'},
            {'name': '翡翠议会', 'level': 'A', 'type': 'light', 'territory': '翡翠秘境', 'population': 15000000, 'leader': '翡翠贤者', 'description': '掌控生命繁衍法则的议会组织，擅长治愈和生长类异能。守护着翡翠秘境的生态平衡。'},
            {'name': '雷神社', 'level': 'A', 'type': 'light', 'territory': '雷鸣高原', 'population': 12000000, 'leader': '雷鸣大将', 'description': '崇拜雷霆之力的神社组织，成员修炼雷霆审判法则。以武道和雷系异能闻名。'},
            {'name': '熔炉氏族', 'level': 'B', 'type': 'light', 'territory': '熔岩核心', 'population': 8000000, 'leader': '熔炉之主', 'description': '擅长火焰锻造的氏族，打造出无数强力宝物。族中匠师遍布各个碎片世界。'},
            {'name': '齿轮议会', 'level': 'A', 'type': 'light', 'territory': '机械之城', 'population': 10000000, 'leader': '首席工程师', 'description': '以机械进化为核心的研究型议会。掌握着先进的机械技术和异能融合技术。'},
            {'name': '深海王庭', 'level': 'A', 'type': 'light', 'territory': '碧波深渊', 'population': 15000000, 'leader': '深海女王', 'description': '统治碧波深渊的王庭势力，掌控水之潮汐法则。拥有强大的海上力量。'},
            {'name': '铁血军团', 'level': 'B', 'type': 'dark', 'territory': '铁血战场', 'population': 6000000, 'leader': '铁血统帅', 'description': '以战争为生的雇佣军团，活跃于各个碎片世界的战场。信奉战争狂热法则。'},
            {'name': '虚空教团', 'level': 'S', 'type': 'dark', 'territory': '虚空之门', 'population': 500000, 'leader': '虚空之主', 'description': '信奉虚空之力的终极教团，试图打开虚空之门，释放毁灭之力。是残响界最大的威胁。'},
        ]
        for f in factions:
            defaults = {k: v for k, v in f.items() if k != 'name'}
            defaults['world'] = world
            self._upsert(Faction, 'factions', stats, {'name': f['name']}, defaults, force)

    def _seed_canxiang_ability_system(self, stats, world, force):
        systems = [
            {'name': '异能体系', 'description': '残响界的核心力量体系。基于法则共鸣，通过觉醒异能来操控世界法则。分为凡境、灵境、神境三大境界，每境九阶。'},
        ]
        for s in systems:
            defaults = {k: v for k, v in s.items() if k != 'name'}
            defaults['world'] = world
            self._upsert(AbilitySystem, 'ability_systems', stats, {'name': s['name']}, defaults, force)

    def _seed_canxiang_realms(self, stats, world, force):
        system, _ = AbilitySystem.objects.get_or_create(
            name='异能体系',
            defaults={'description': '残响界的核心力量体系。', 'world': world},
        )

        tier_desc = {
            'mortal': {
                'details': {
                    1: '感知法则存在，能隐约感应到法则的气息。',
                    2: '初步接触法则，开始尝试感应法则之力。',
                    3: '初步运用法则，能简单地使用法则之力。',
                    4: '稳步提升中，法则之力的运用更加熟练。',
                    5: '法则运用加深，开始展现一定的战斗能力。',
                    6: '熟练操控法则，能灵活运用法则之力。',
                    7: '对法则有深入理解，可进行复杂操控。',
                    8: '接近凡人极限，法则之力运用纯熟。',
                    9: '达到凡人极限，触及灵境的门槛。',
                },
            },
            'spirit': {
                'details': {
                    1: '踏入灵境，与法则深度共鸣，能操控法则之力。',
                    2: '灵境稳固，法则操控更加自如。',
                    3: '稳定输出，法则之力可稳定释放。',
                    6: '法则具现，能将法则之力具现为实体。',
                    9: '触及法则本质，距离神境仅一步之遥。',
                },
            },
            'divine': {
                'details': {
                    1: '法则化身，自身与法则融为一体。',
                    2: '法则领域，可展开法则领域影响周围。',
                    3: '法则创世，已知最高境界，可改写现实。',
                },
            },
        }

        realms_data = []
        for i in range(1, 10):
            desc = tier_desc['mortal']['details'].get(i, f'凡境第{i}阶。')
            realms_data.append({'name': f'凡境{i}阶', 'tier': 'mortal', 'level_order': i, 'description': desc, 'breakthrough_conditions': '', 'abilities_unlocked': ''})
        for i in range(1, 10):
            desc = tier_desc['spirit']['details'].get(i, f'灵境第{i}阶。')
            realms_data.append({'name': f'灵境{i}阶', 'tier': 'spirit', 'level_order': 9 + i, 'description': desc, 'breakthrough_conditions': '', 'abilities_unlocked': ''})
        for i in range(1, 4):
            desc = tier_desc['divine']['details'].get(i, f'神境第{i}阶。')
            realms_data.append({'name': f'神境{i}阶', 'tier': 'divine', 'level_order': 18 + i, 'description': desc, 'breakthrough_conditions': '', 'abilities_unlocked': ''})

        for r in realms_data:
            defaults = {k: v for k, v in r.items() if k not in ('name', 'level_order', 'tier')}
            defaults['tier'] = r['tier']
            defaults['level_order'] = r['level_order']
            defaults['system'] = system
            defaults['world'] = world
            self._upsert(Realm, 'realms', stats, {'name': r['name']}, defaults, force)

    def _seed_canxiang_skill_levels(self, stats, world, force):
        system, _ = AbilitySystem.objects.get_or_create(
            name='异能体系',
            defaults={'description': '残响界的核心力量体系。', 'world': world},
        )
        levels = [
            {'name': '初级', 'level_order': 1},
            {'name': '中级', 'level_order': 2},
            {'name': '高级', 'level_order': 3},
            {'name': '大师级', 'level_order': 4},
            {'name': '宗师级', 'level_order': 5},
        ]
        for lv in levels:
            defaults = {'level_order': lv['level_order'], 'system': system, 'world': world}
            self._upsert(SkillLevel, 'skill_levels', stats, {'name': lv['name']}, defaults, force)

    def _seed_canxiang_characters(self, stats, world, force):
        characters = [
            {'name': '林雾', 'aliases': '残响之子/时间行者', 'faction_name': '残响议会', 'realm_tier': 'divine', 'realm_order': 3, 'status': 'active', 'bio': '残响界的主角，天生拥有时间残响法则的亲和力。从一个普通少年成长为神境强者，是残响议会的核心人物。', 'personality': '沉稳冷静，内心温柔，面对强敌从不退缩。有着强烈的正义感和责任感。', 'appearance_desc': '黑发黑瞳，身材修长。左眼下方有一道时间法则留下的银色纹路，使用能力时会发出微光。'},
            {'name': '暗影主宰', 'aliases': '深渊之主', 'faction_name': '深渊教团', 'realm_tier': 'divine', 'realm_order': 1, 'status': 'active', 'bio': '深渊教团的创建者与最高领袖，掌控暗影吞噬法则已达数百年。真实身份成谜，据说曾是残响议会的成员。', 'personality': '阴沉狡诈，城府极深。行事不择手段，但有着自己独特的行事准则。', 'appearance_desc': '终身笼罩在黑雾之中，无人见过其真面目。只有一双猩红色的眼睛在黑暗中闪烁。'},
            {'name': '风翔将军', 'aliases': '苍穹之翼', 'faction_name': '苍穹骑士团', 'realm_tier': 'spirit', 'realm_order': 9, 'status': 'active', 'bio': '苍穹骑士团的团长，风之律动法则的顶尖使用者。年轻时曾与林雾并肩作战，是林雾的挚友。', 'personality': '豪爽直率，重情重义。战场上勇猛无畏，平时却平易近人。', 'appearance_desc': '金发碧眼，身披白色铠甲。背后有一对由风之律动凝聚的透明翅膀。'},
            {'name': '翡翠贤者', 'aliases': '生命守望者', 'faction_name': '翡翠议会', 'realm_tier': 'spirit', 'realm_order': 8, 'status': 'active', 'bio': '翡翠议会的领袖，生命繁衍法则的大师。年龄已逾三百岁，但外表依然年轻。是残响界最顶尖的治愈者。', 'personality': '慈祥温和，充满智慧。对万物生灵怀有悲悯之心。', 'appearance_desc': '翠绿色长发，身着翡翠色长袍。周身常伴有花瓣飘落。'},
            {'name': '雷鸣大将', 'aliases': '雷神之刃', 'faction_name': '雷神社', 'realm_tier': 'spirit', 'realm_order': 9, 'status': 'active', 'bio': '雷神社的大将，雷霆审判法则的极致使用者。以一把雷刃横扫雷鸣高原，无人能敌。', 'personality': '严苛刚正，军人作风。对敌人冷酷无情，对部下关怀备至。', 'appearance_desc': '银白色短发，身着紫黑色战甲。手中雷刃时刻散发着电弧。'},
            {'name': '虚空之主', 'aliases': '终焉者', 'faction_name': '虚空教团', 'realm_tier': 'divine', 'realm_order': 3, 'status': 'sealed', 'bio': '虚空教团的神秘领袖，掌控虚空吞噬法则的恐怖存在。曾一度撕裂虚空之门，差点毁灭残响界。被残响议会联合多方势力封印。', 'personality': '疯狂偏执，渴望毁灭一切。认为虚空是万物的终焉。', 'appearance_desc': '身体半透明，仿佛随时会消散在虚空中。双眼是无底的黑色深渊。'},
        ]
        for c in characters:
            faction = Faction.objects.filter(name=c.pop('faction_name')).first()
            defaults = c.copy()
            if faction:
                defaults['faction'] = faction
            defaults['world'] = world
            self._upsert(Character, 'characters', stats, {'name': c['name']}, defaults, force)

    def _seed_canxiang_artifact_categories(self, stats, world, force):
        categories = [
            {'name': '时间法则器', 'description': '蕴含时间残响法则的宝物，可操控时间流速', 'rarity_level': 'SSS'},
            {'name': '深渊神器', 'description': '来自深渊裂隙的暗影之力凝聚而成', 'rarity_level': 'SSS'},
            {'name': '元素结晶', 'description': '各元素法则凝聚的结晶体，可用于强化异能', 'rarity_level': 'S'},
            {'name': '法则碎片', 'description': '破碎世界法则的实体化碎片，极为稀有', 'rarity_level': 'SS'},
            {'name': '灵能武器', 'description': '融入异能的武器，可随使用者成长', 'rarity_level': 'A'},
            {'name': '治愈圣物', 'description': '蕴含生命法则的治愈系宝物', 'rarity_level': 'S'},
            {'name': '雷霆兵器', 'description': '蕴含雷霆审判法则的战斗兵器', 'rarity_level': 'A'},
            {'name': '虚空遗物', 'description': '来自虚空之门的神秘遗物，危险而强大', 'rarity_level': 'SSS'},
        ]
        for cat in categories:
            defaults = {k: v for k, v in cat.items() if k != 'name'}
            defaults['world'] = world
            self._upsert(ArtifactCategory, 'artifact_categories', stats, {'name': cat['name']}, defaults, force)

    def _seed_canxiang_artifacts(self, stats, world, force):
        artifacts = [
            {'name': '残响之钟', 'category_name': '时间法则器', 'rarity_level': 'SSS', 'owner_name': '林雾', 'origin': '残响界·起源', 'description': '传说中由时间法则凝聚而成的神钟。敲响可令方圆百里时间静止，是残响界的至高宝物。', 'effects': '时间静止、时间回溯、法则共鸣'},
            {'name': '深渊之眼', 'category_name': '深渊神器', 'rarity_level': 'SSS', 'owner_name': '暗影主宰', 'origin': '深渊裂隙', 'description': '凝聚深渊之力的眼球状宝物，可洞察一切暗影。凝视者将被深渊意志侵蚀。', 'effects': '暗影洞察、精神侵蚀、深渊召唤'},
            {'name': '苍穹之翼', 'category_name': '灵能武器', 'rarity_level': 'S', 'owner_name': '风翔将军', 'origin': '苍穹之冠', 'description': '由风之律动凝聚的翅膀形武器，可令使用者自由翱翔天际。', 'effects': '飞行、风刃斩击、风之屏障'},
            {'name': '翡翠之心', 'category_name': '治愈圣物', 'rarity_level': 'S', 'owner_name': '翡翠贤者', 'origin': '翡翠秘境', 'description': '蕴含强大生命力的翡翠色宝石，可治愈任何伤势，甚至起死回生。', 'effects': '高级治愈、生命复苏、生态净化'},
            {'name': '雷神之刃', 'category_name': '雷霆兵器', 'rarity_level': 'S', 'owner_name': '雷鸣大将', 'origin': '雷鸣高原', 'description': '蕴含雷霆审判法则的神兵，一刀可劈开山岳。是雷神社的镇社之宝。', 'effects': '雷霆斩击、麻痹效果、雷域展开'},
            {'name': '虚空之钥', 'category_name': '虚空遗物', 'rarity_level': 'SSS', 'owner_name': None, 'origin': '虚空之门', 'description': '可开启虚空之门的钥匙。一旦使用，将释放虚空之力，可能毁灭整个残响界。', 'effects': '虚空之门开启、空间撕裂、虚空吞噬'},
        ]
        for a in artifacts:
            category_name = a.pop('category_name')
            owner_name = a.pop('owner_name')
            category = ArtifactCategory.objects.filter(name=category_name).first()
            owner = Character.objects.filter(name=owner_name).first() if owner_name else None
            defaults = a.copy()
            if category:
                defaults['category'] = category
            defaults['owner'] = owner
            defaults['world'] = world
            self._upsert(Artifact, 'artifacts', stats, {'name': a['name']}, defaults, force)

    def _seed_canxiang_skills(self, stats, world, force):
        skills = [
            {'name': '时间残响', 'level_name': '宗师级', 'description': '林雾的核心技能。令目标区域的时间产生残响，可回溯过去或窥探未来。', 'effects': '时间回溯、未来窥探、时间静止', 'prerequisites': '神境一阶', 'cooldown': '24小时'},
            {'name': '暗影吞噬', 'level_name': '宗师级', 'description': '暗影主宰的终极技能。将一切光明吞噬于暗影之中。', 'effects': '暗影领域、光明吞噬、暗影同化', 'prerequisites': '神境一阶', 'cooldown': '12小时'},
            {'name': '苍穹风暴', 'level_name': '大师级', 'description': '风翔将军的招牌技能。召唤巨大的风暴席卷战场。', 'effects': '范围风刃、风暴眼、风之加速', 'prerequisites': '灵境七阶', 'cooldown': '6小时'},
            {'name': '生命之雨', 'level_name': '大师级', 'description': '翡翠贤者的治愈技能。降下蕴含生命力的雨露。', 'effects': '群体治愈、持续恢复、净化负面', 'prerequisites': '灵境七阶', 'cooldown': '8小时'},
            {'name': '雷霆审判', 'level_name': '大师级', 'description': '雷鸣大将的必杀技。召唤天雷审判敌人。', 'effects': '雷击、麻痹、雷域展开', 'prerequisites': '灵境七阶', 'cooldown': '4小时'},
        ]
        for s in skills:
            level_name = s.pop('level_name')
            level = SkillLevel.objects.filter(name=level_name).first()
            defaults = s.copy()
            if level:
                defaults['level'] = level
            defaults['world'] = world
            self._upsert(Skill, 'skills', stats, {'name': s['name']}, defaults, force)

    def _seed_canxiang_creatures(self, stats, world, force):
        creatures = [
            {'name': '时之龙', 'species': '龙族', 'danger_level': 5, 'habitat_name': '时光遗迹', 'abilities': '时间操控、空间穿越', 'description': '传说中生活在时光遗迹的远古龙族。能操控时间流速，是残响界最危险的异兽之一。'},
            {'name': '深渊巨兽', 'species': '巨兽', 'danger_level': 5, 'habitat_name': '深渊裂隙', 'abilities': '暗影吞噬、体型巨大', 'description': '栖息在深渊裂隙深处的巨型生物。以暗影为食，体型可遮蔽天空。'},
            {'name': '风暴鹰', 'species': '飞禽', 'danger_level': 3, 'habitat_name': '苍穹之冠', 'abilities': '风刃、高速飞行', 'description': '苍穹之冠的标志性生物。飞行速度极快，翅膀可发出风刃攻击。'},
            {'name': '翡翠鹿', 'species': '灵兽', 'danger_level': 1, 'habitat_name': '翡翠秘境', 'abilities': '治愈光环、生命感应', 'description': '翡翠秘境的灵兽。散发治愈光环，是生命繁衍法则的天然载体。'},
            {'name': '雷兽', 'species': '猛兽', 'danger_level': 4, 'habitat_name': '雷鸣高原', 'abilities': '雷电释放、超强防御', 'description': '雷鸣高原的霸主级猛兽。浑身覆盖雷电，防御力极强。'},
            {'name': '虚空行者', 'species': '虚空生物', 'danger_level': 5, 'habitat_name': '虚空之门', 'abilities': '虚空穿梭、存在抹消', 'description': '来自虚空之门的恐怖生物。可以在虚实之间穿梭，攻击会抹消目标的存在。'},
        ]
        for c in creatures:
            habitat_name = c.pop('habitat_name')
            habitat = FragmentWorld.objects.filter(name=habitat_name).first()
            defaults = c.copy()
            if habitat:
                defaults['habitat'] = habitat
            defaults['world'] = world
            self._upsert(Creature, 'creatures', stats, {'name': c['name']}, defaults, force)

    def _seed_canxiang_historical_events(self, stats, world, force):
        events = [
            {'name': '碎片大裂变', 'era': 'era1', 'date_description': '约万年前', 'description': '原始世界因法则冲突而碎裂为十八个碎片世界。这是残响界一切历史的起点。', 'consequences': '世界碎裂、法则分散、各族隔离', 'faction_names': [], 'character_names': []},
            {'name': '法则觉醒', 'era': 'era2', 'date_description': '约八千年前', 'description': '人类开始觉醒异能，学会与法则共鸣。第一个异能体系被建立。', 'consequences': '异能文明兴起、阶级分化', 'faction_names': [], 'character_names': []},
            {'name': '议会建立', 'era': 'era3', 'date_description': '约五千年前', 'description': '残响议会在起源碎片成立，开始统一管理残响界的秩序。', 'consequences': '秩序建立、跨碎片交流恢复', 'faction_names': ['残响议会'], 'character_names': []},
            {'name': '深渊战争', 'era': 'era4', 'date_description': '约一千年前', 'description': '深渊教团大举入侵，多个碎片世界沦陷。残响议会联合各方势力反击。', 'consequences': '多碎片损毁、深渊教团退守', 'faction_names': ['残响议会', '深渊教团'], 'character_names': []},
            {'name': '虚空之灾', 'era': 'era5', 'date_description': '约百年前', 'description': '虚空之主撕裂虚空之门，差点毁灭残响界。林雾联合多方势力将其封印。', 'consequences': '虚空之主封印、虚空之门封锁、林雾觉醒神境', 'faction_names': ['残响议会', '虚空教团', '深渊教团'], 'character_names': ['林雾', '虚空之主']},
        ]
        for e in events:
            faction_names = e.pop('faction_names')
            character_names = e.pop('character_names')
            defaults = {k: v for k, v in e.items() if k != 'name'}
            defaults['world'] = world
            obj, created, updated = self._upsert(HistoricalEvent, 'historical_events', stats, {'name': e['name']}, defaults, force)
            if faction_names:
                factions = Faction.objects.filter(name__in=faction_names)
                if obj.involved_factions.count() != factions.count():
                    obj.involved_factions.set(factions)
            if character_names:
                characters = Character.objects.filter(name__in=character_names)
                if obj.involved_characters.count() != characters.count():
                    obj.involved_characters.set(characters)

    def _seed_canxiang_relationships(self, stats, world, force):
        type_map = {
            '挚友': 'friend', '宿敌': 'enemy', '封印者': 'other',
            '盟友': 'ally', '竞争者': 'rival', '师长': 'master',
        }
        relationships = [
            {'from_name': '林雾', 'to_name': '风翔将军', 'relation_label': '挚友', 'description': '年轻时并肩作战的战友，彼此信任'},
            {'from_name': '林雾', 'to_name': '暗影主宰', 'relation_label': '宿敌', 'description': '光与暗的对立，多次交手'},
            {'from_name': '林雾', 'to_name': '虚空之主', 'relation_label': '封印者', 'description': '林雾主导了封印虚空之主的行动'},
            {'from_name': '暗影主宰', 'to_name': '虚空之主', 'relation_label': '盟友', 'description': '暗中结盟，各怀鬼胎'},
            {'from_name': '风翔将军', 'to_name': '雷鸣大将', 'relation_label': '竞争者', 'description': '武道上的竞争关系，亦敌亦友'},
            {'from_name': '翡翠贤者', 'to_name': '林雾', 'relation_label': '师长', 'description': '曾指导林雾修炼'},
        ]
        for r in relationships:
            from_char = Character.objects.filter(name=r['from_name']).first()
            to_char = Character.objects.filter(name=r['to_name']).first()
            if not from_char or not to_char:
                continue
            rel_type = type_map.get(r['relation_label'], 'other')
            defaults = {'relation_type': rel_type, 'description': r['description']}
            self._upsert(Relationship, 'relationships', stats, {'from_character': from_char, 'to_character': to_char, 'relation_type': rel_type}, defaults, force)

    def _seed_canxiang_lore_pages(self, stats, world, force):
        pages = [
            {'title': '世界总纲', 'slug': 'world-overview', 'category': 'core', 'content': '残响界是由原始世界碎裂而成的十八个碎片世界组成的异世界。每个碎片世界拥有不同的主导法则，孕育了独特的文明与生态。世界运转的核心是法则共鸣——通过觉醒异能来操控世界法则。', 'order': 1},
            {'title': '宇宙规则', 'slug': 'cosmic-rules', 'category': 'core', 'content': '残响界的宇宙规则基于三大法则：时间残响、空间共振、法则共鸣。时间残响是世界的根基，空间共振维系碎片间的平衡，法则共鸣是力量的源泉。', 'order': 2},
            {'title': '异能本质', 'slug': 'ability-essence', 'category': 'power', 'content': '异能的本质是法则共鸣。每个人天生与某种法则有亲和力，通过修炼可以加深共鸣，最终操控法则。觉醒路径分为自然觉醒、仪式觉醒和极端觉醒三种。', 'order': 3},
            {'title': '三级九阶', 'slug': 'three-realm-nine-level', 'category': 'power', 'content': '异能境界分为凡境、灵境、神境三大境界，每境九阶。凡境感知法则，灵境操控法则，神境融入法则。神境三阶为已知最高境界。', 'order': 4},
            {'title': '双层势力', 'slug': 'dual-layer-factions', 'category': 'civilization', 'content': '残响界的势力分为光明与暗网两层。光明势力公开活动，维持秩序；暗网势力隐于暗处，各怀目的。两股力量此消彼长，构成了残响界的政治格局。', 'order': 5},
            {'title': '灾变原因', 'slug': 'cataclysm-cause', 'category': 'history', 'content': '万年前的碎片大裂变是法则冲突导致的。原始世界的法则因某种原因失去平衡，导致世界碎裂。裂变的真正原因至今仍是未解之谜。', 'order': 6},
        ]
        for p in pages:
            defaults = {k: v for k, v in p.items() if k != 'slug'}
            defaults['world'] = world
            self._upsert(LorePage, 'lore_pages', stats, {'slug': p['slug']}, defaults, force)

    def _link_canxiang_character_skills_and_artifacts(self, stats):
        link_map = {
            '林雾': {'skills': ['时间残响'], 'artifacts': ['残响之钟']},
            '暗影主宰': {'skills': ['暗影吞噬'], 'artifacts': ['深渊之眼']},
            '风翔将军': {'skills': ['苍穹风暴'], 'artifacts': ['苍穹之翼']},
            '翡翠贤者': {'skills': ['生命之雨'], 'artifacts': ['翡翠之心']},
            '雷鸣大将': {'skills': ['雷霆审判'], 'artifacts': ['雷神之刃']},
        }
        linked_skills = 0
        linked_artifacts = 0
        for char_name, links in link_map.items():
            char = Character.objects.filter(name=char_name).first()
            if not char:
                continue
            if links.get('skills'):
                skills = Skill.objects.filter(name__in=links['skills'])
                existing = set(char.abilities.values_list('name', flat=True))
                for s in skills:
                    if s.name not in existing:
                        char.abilities.add(s)
                        linked_skills += 1
            if links.get('artifacts'):
                artifacts = Artifact.objects.filter(name__in=links['artifacts'])
                existing = set(char.artifacts.values_list('name', flat=True))
                for a in artifacts:
                    if a.name not in existing:
                        char.artifacts.add(a)
                        linked_artifacts += 1
        if linked_skills or linked_artifacts:
            self.stdout.write(f'  残响界 角色-技能关联: {linked_skills} 条, 角色-宝物关联: {linked_artifacts} 条')

    # ================================================================
    # 深骸 DATA
    # ================================================================
    def _seed_shenhai_all(self, stats, world):
        self.stdout.write(self.style.SUCCESS('  --- 深骸世界数据注入 ---'))
        self._seed_shenhai_fragment_worlds(stats, world)
        self._seed_shenhai_factions(stats, world)
        self._seed_shenhai_ability_system(stats, world)
        self._seed_shenhai_realms(stats, world)
        self._seed_shenhai_skill_levels(stats, world)
        self._seed_shenhai_skills(stats, world)
        self._seed_shenhai_origin_laws(stats, world)
        self._seed_shenhai_artifact_categories(stats, world)
        self._seed_shenhai_artifacts(stats, world)
        self._seed_shenhai_anomalies(stats, world)
        self._seed_shenhai_creatures(stats, world)
        self._seed_shenhai_historical_events(stats, world)
        self._seed_shenhai_lore_pages(stats, world)

    def _seed_shenhai_fragment_worlds(self, stats, world):
        fragments = [
            {'number_id': 1, 'name': '锈蚀荒原', 'area': '7200万 km²', 'population': 12000000, 'dominant_law': '衰变/混沌', 'danger_level': 2, 'max_faction': '钢铁议会', 'faction_level': '帝国级', 'strongest_power': '灵境2阶',
             'description': '灾变前为欧亚大陆东部工业带，如今被厚达数米的锈蚀金属覆盖的工业废墟型大陆。地表遍布废弃机械残骸和倒塌厂房骨架，酸性降水持续腐蚀一切，地下有庞大废弃地铁网络和下水道系统。钢铁议会掌控最完整的工业体系，工业秩序法则使废墟的损坏和衰败遵循规律，可被逆向工程利用。',
             'features': '7个主要区域：锈蚀大平原、废铁山脉、齿轮峡谷、蒸汽沼泽、倒悬铁塔林、锈蚀海岸、旧工厂地下城。衰败法则渗透每一寸土地，催生以锈为食的异兽生态；元素法则以工业元素变体形式存在，工业炼金术发达。文化核心围绕"锈"展开，存在机械改造文化与最初熔炉信仰。'},
            {'number_id': 2, 'name': '深渊海渊', 'area': '4800万 km²', 'population': 3000000, 'dominant_law': '水元素/虚无', 'danger_level': 3, 'max_faction': '深海王庭', 'faction_level': '帝国级', 'strongest_power': '灵境3阶',
             'description': '灾变前为太平洋深海盆地，深海渊型大陆。虚空法则浓度在十八大碎片中首屈一指，表现为吞噬和消逝。深海王庭通过"渊化"仪式让虚空法则改造身体获得水下能力，皇室成员外形已近人与深海古生物的混合体。深渊生物普遍具有超强再生能力和环境适应性，催生独特的深渊生态。',
             'features': '5个主要区域：无光海沟、珊瑚坟场、压力深渊、浮岛海域、海渊裂口。浮岛海域有数千座漂浮在海面上数百至数千米的岛屿；海渊裂口是跨碎片偷渡的主要通道。禁地渊底之门据传通向世界外侧，灾变时被某种存在从此门侵入所致，深海王庭世代守护。'},
            {'number_id': 3, 'name': '翡翠天穹', 'area': '6500万 km²', 'population': 45000000, 'dominant_law': '生命', 'danger_level': 2, 'max_faction': '天穹帝国', 'faction_level': '帝国级', 'strongest_power': '灵境3阶',
             'description': '灾变前为东南亚-南亚大陆架及群岛，浮空大陆型。拥有十八大碎片中最高浓度的生命法则，由十二块陆地板块漂浮在3000-8000米高空组成。天穹帝国是十八大碎片中最强盛的帝国之一。生命法则表现为生命力外溢，可快速治愈伤势、延缓衰老。社会阶层由"居住高度"象征，形成独特的"高度哲学"思想体系。',
             'features': '6个主要区域：浮空大陆群、翡翠高原、云瀑峡谷、天穹树海、风之平原、虹光群岛。大陆底部生长巨型反重力藤，树海中世界树树龄超万年甚至发展出低等意识。空间法则异常使大陆漂浮，虹光群岛的虹光幕具有防护作用。天穹帝国垄断大部分传送技术。'},
            {'number_id': 4, 'name': '永冻寂土', 'area': '2200万 km²', 'population': 2000000, 'dominant_law': '冰元素/时间', 'danger_level': 3, 'max_faction': '霜冻王座', 'faction_level': '王国级', 'strongest_power': '灵境1阶',
             'description': '灾变前为西伯利亚-北极高纬度地区，极寒冰原型大陆。时间法则浓度极高，呈现凝固与回溯的奇异特性，冰层下冻结着灾变前的城市、森林甚至火山。文化核心是"静"与"恒"，居民推崇持久和忍耐，艺术以冰雕和慢音乐为主。霜冻王座以冷酷高效的统治和强大的冰系术士闻名。',
             'features': '5个主要区域：永冻冰原、寂静山脉、冰川裂谷、冰封森林、时间停滞带。时间冰晶封存永恒瞬间；寂静山脉声音传播极其困难；时间停滞带时间流速严重扭曲，存在时间断层。禁地时间之源据说掌握时间之核可操控整个碎片的时间流速。'},
            {'number_id': 5, 'name': '赤焰焦土', 'area': '5800万 km²', 'population': 8000000, 'dominant_law': '火元素/混沌', 'danger_level': 3, 'max_faction': '炎魔帝国', 'faction_level': '帝国级', 'strongest_power': '灵境2阶',
             'description': '灾变前为环太平洋火山带，火山熔岩型大陆。混沌法则以破坏和熵增形式肆虐，元素法则极端偏向火元素。炎魔帝国国教"永恒炎教"崇拜原初之火，追求"最炽烈的燃烧"。文化核心是"燃烧"哲学，将生命视为一团火。居民代谢速度明显快于其他碎片，成熟更快、衰老更快。艺术以烬画和爆音为特色。',
             'features': '5个主要区域：熔岩高原、灰烬平原、火山群脉、焦黑峡谷、焚风之地。原初火山直径超500公里，岩浆池蕴含纯粹火元素精华；焚风之地温度超100°C的灼热狂风，产出最优质的耐热装备。禁地法则燃尽带正以每年约100米速度缓慢扩张，是所有势力心头最大阴影。'},
            {'number_id': 6, 'name': '虚无裂谷', 'area': '800万 km²', 'population': 80000, 'dominant_law': '虚无', 'danger_level': 5, 'max_faction': '守望者残部', 'faction_level': '据地级', 'strongest_power': '凡境5阶',
             'description': '灾变前为某超级都市群核心区域，虚空崩解型大陆。虚空法则浓度是十八大碎片中最高的，呈现主动吞噬现实、抹除法则、消解意义的力量。灾变时此处不是被撕裂或焚烧而是"崩解"——现实本身碎裂露出世界背后的虚无。文化是"末日文化"，居民发展出极端的"活在当下"哲学，不建造永久建筑、不积累财富。',
             'features': '3个主要区域：裂谷核心、虚无边缘带、现实残片区。裂谷核心现实法则几乎完全崩解，由漂浮的现实残片构成；虚无边缘带地貌呈"未完成"状态；现实残片区保存灾变前超级都市群残骸。禁地虚无之心是虚空法则极致汇聚点，任何进入者都从物质、能量、信息乃至因果层面被彻底抹除，正缓慢扩张。'},
            {'number_id': 7, 'name': '镜面沙海', 'area': '3500万 km²', 'population': 6000000, 'dominant_law': '灵魂/空间', 'danger_level': 3, 'max_faction': '镜之王庭', 'faction_level': '王国级', 'strongest_power': '灵境2阶',
             'description': '沙漠-空间畸变型大陆，被无尽黄沙覆盖的破碎世界。最诡异的特征是散布各处的"世界镜面"——高达数十米至千米的平滑镜面状物体，映照出其他碎片世界、未知维度乃至灾变前地球的景象。整片大陆空间结构极不稳定，镜面周围常伴随空间褶皱与微型裂隙。空间法则浓度78%。',
             'features': '5大区：千镜大沙漠、折射高原、影之谷、碎镜海、静默绿洲带。千镜大沙漠散布超十万面世界镜面；折射高原镜面密度是沙漠带十倍，会周期性切换映照内容甚至将映照之物实体化投射；影之谷谷壁映照无尽深渊与虚空，传言连通虚无裂谷；碎镜海产出珍贵的空间晶砂。'},
            {'number_id': 8, 'name': '骨架丛林', 'area': '3000万 km²', 'population': 15000000, 'dominant_law': '衰变/生命', 'danger_level': 2, 'max_faction': '骨血帝国', 'faction_level': '帝国级', 'strongest_power': '灵境3阶',
             'description': '巨骨-生命演化型大陆，由超巨型生物遗骸构成的诡异世界。灾变前某种无法想象的庞然大物在此陨落，骨骼化作山脉、平原与峡谷。骨髓化为树脂、神经变成藤蔓、血液凝结成湖泊，形成以"死之躯壳孕育新生"为特征的奇异生态系统。生命法则浓度82%，生物生长速度是正常环境的五至十倍，但伴随极高变异率。',
             'features': '5大区：脊骨山脉、肋骨平原、颅骨高地、骨髓深谷、齿刃沼泽。脊骨山脉单节脊椎骨可高达数百米，中空通道构成天然交通网络；肋骨平原风穿过孔洞发出"骨之乐章"；颅骨高地内壁刻满灾变前未知符文；骨髓深谷生长血晶菇林是最肥沃农业区；齿刃沼泽珐琅质是最优质天然磨料。'},
            {'number_id': 9, 'name': '潮声低语', 'area': '1800万 km²', 'population': 4000000, 'dominant_law': '时间/灵魂', 'danger_level': 3, 'max_faction': '潮音殿', 'faction_level': '王国级', 'strongest_power': '灵境2阶',
             'description': '海洋-灵魂污染型大陆，被无尽海洋覆盖的水之世界，陆地仅占不到8%。最恐怖的特征是无处不在的"低语"——从深海传来直接回荡在生灵灵魂中的声音，长年累月侵染会使聆听者灵魂逐渐扭曲。灵魂法则浓度85%，使生灵天生具有较强精神感知力但也极易受精神污染。海洋深处藏着灾变前遗迹与不可名状的深海巨兽。',
             'features': '5大区：低语洋、回声群岛、潮汐裂谷、珊瑚骨林、深渊喉腔。低语洋深海存在"声音通道"将特定频率声音放大传播形成共鸣现象；回声群岛存在"回声井"特定音节可触发超自然现象；潮汐裂谷是低语声最清晰来源地；深渊喉腔是低语源头，偶有不可名状巨物从深处浮上。'},
            {'number_id': 10, 'name': '铁幕山岳', 'area': '8200万 km²', 'population': 55000000, 'dominant_law': '秩序/地元素', 'danger_level': 2, 'max_faction': '铁幕帝国', 'faction_level': '帝国级', 'strongest_power': '灵境3阶',
             'description': '山岳-秩序固结型大陆，十八碎片中面积最大的碎片之一。整个世界被无尽山脉、丘陵与高原覆盖，几乎没有平原。岩石富含特殊金属矿物，山体呈现铁灰、青铜、银白等金属色泽。存在法则浓度75%赋予奇异"稳固性"——物质极难被毁灭，建筑可历经千年不倒，但改变极为困难，社会变革与技术革新比其他碎片缓慢得多。山即是城，城即是山。',
             'features': '7大区：铁冠山脉、青铜丘陵、黑铁峡谷带、银峰高原、赤铜熔脉、铅云盆地、钢脊走廊。铁冠山脉磁铁矿形成天然磁场屏障；黑铁峡谷带底部流淌液态金属流；银峰高原存在数十尊高达千米来历不明的银峰巨像；钢脊走廊是连接东西部的唯一陆路通道，控制走廊便控制碎片交通命脉。'},
            {'number_id': 11, 'name': '灰雾平原', 'area': '1500万 km²', 'population': 1500000, 'dominant_law': '虚无/混沌', 'danger_level': 3, 'max_faction': '时钟塔', 'faction_level': '王国级', 'strongest_power': '灵境2阶',
             'description': '平原-时间畸变型大陆，被永恒灰雾笼罩的诡异世界，地形以无垠平原为主。时间法则极度紊乱（浓度88%），同一片区域内有的地方时间流速是外界百倍，有的几乎停滞；有人行走数步便苍老数十年，也有人被困在某瞬间长达数年。灰雾遮蔽过去与未来，只留下模糊的现在。人口稀少，生存极为艰难，但能适应时间畸变的居民往往获得超乎寻常的寿命或预知能力。',
             'features': '4大区：时雾荒原、静止湖群、流速丘陵、遗忘森林。时雾荒原时间流速以"时区"形式分布，旅行者需依靠"时标石"导航；静止湖群湖水具有时间静止属性，落入物体永不下沉；流速丘陵每座丘陵时间流速各不相同，被称为"时间岛屿"；遗忘森林一切被"定格"，偶尔发生"时间断裂"。'},
            {'number_id': 12, 'name': '晶脉地心', 'area': '5200万 km²', 'population': 20000000, 'dominant_law': '七元素/存在', 'danger_level': 2, 'max_faction': '六晶帝国', 'faction_level': '帝国级', 'strongest_power': '灵境3阶',
             'description': '地下-元素富集型大陆，没有天空的地下世界。整片碎片被厚重岩层封闭，居民抬头看到的是发光晶顶与熔岩穹顶。地质结构以巨型水晶洞穴与元素富集区为主，六种基本元素——火、水、土、雷、毒、光——在此高度凝聚。元素法则浓度80%，使此地成为炼金术士与元素法师的圣地，但失控的元素潮汐也时常带来灾难。社会围绕六大元素区域形成独特的"元素崇拜"文化。',
             'features': '6大区：红晶熔窟、蓝晶冰宫、绿晶毒沼、紫晶雷域、黄晶荒漠、白晶圣所。红晶熔窟流淌岩浆河可加工超高熔点金属；蓝晶冰宫水体会冻结灵魂；绿晶毒沼以毒攻毒药理学发展至极致；紫晶雷域闪电是元素法则具现化；黄晶荒漠埋藏古代地下文明遗迹；白晶圣所光元素水晶散发治愈净化光芒，居民平均寿命是其他区域1.5倍。'},
            {'number_id': 13, 'name': '腐沼深渊', 'area': '2800万 km²', 'population': 5000000, 'dominant_law': '混沌/生命', 'danger_level': 3, 'max_faction': '脓苔帝国', 'faction_level': '帝国级', 'strongest_power': '灵境2阶',
             'description': '万毒之渊，被剧毒沼泽与真菌生态覆盖的危险大陆。混沌法则与生命法则交织，催生了以腐败与变异为核心的诡异生态系统。空气中弥漫致幻毒气，沼气湖泊夜间自燃形成"鬼火海"奇观。深渊泥沼中沉睡着远古巨兽遗骸。真菌网络形成地下神经矩阵，具有初级群体意识。',
             'features': '5大生态-政治区：黑瘴泽、蚀骨平原、菌核高地、淤塞三角洲、尸骸山脉。黑瘴泽泥潭深达数百米漂浮真菌岛屿；蚀骨平原pH值常年低于3普通金属数小时内锈蚀，地下千米存在巨型溶洞海洋；菌核高地菌盖直径可达数公里；淤塞三角洲中心"万毒之眼"吸入一切分解为原始毒素；尸骸山脉最高峰万骨之巅海拔8924米，深处传说通向"原初之胃"。'},
            {'number_id': 14, 'name': '逆流长河', 'area': '2500万 km²', 'population': 7000000, 'dominant_law': '时间/空间', 'danger_level': 3, 'max_faction': '时痕王朝', 'faction_level': '帝国级', 'strongest_power': '灵境2阶',
             'description': '时痕之域，以倒流河流为核心特征的诡异大陆。河流从低地向高地倒流，形成壮观的水墙瀑布。时间法则与空间法则交织，使水流违背重力逆向运动。时痕王朝统治这片土地，居民建造复杂水利系统利用逆流能量。倒流河的源头位于地底深处，河水从地底向上涌出。',
             'features': '5大生态-政治区：溯时高原、环水盆地、支流迷宫、河源深井、河脊山脉。溯时高原中心存在"时痕尖塔"——凝固时间构成的晶体山峰，是碎片时间锚点；环水盆地中央"静水之镜"任何物体触及湖面都被冻结在永恒瞬间；支流迷宫深处"记忆支流"饮水会随机获得过去或未来记忆碎片；河源深井最深的"时间深井"底部存在通往其他碎片时间线的通道。'},
            {'number_id': 15, 'name': '裂空群岛', 'area': '4000万 km²', 'population': 10000000, 'dominant_law': '空间/风元素', 'danger_level': 3, 'max_faction': '穹顶联邦', 'faction_level': '帝国级', 'strongest_power': '灵境2阶',
             'description': '浮天万岛，由无数浮空岛屿组成的空间异常大陆。中央穹顶群岛由十二座巨型浮空主岛组成，每座面积堪比澳大利亚，漂浮在云海之上数公里。主岛底部生长反重力水晶矿脉是浮空动力源。空间法则与风元素法则交织，使整片碎片呈现立体的岛屿生态。穹顶联邦是碎片的帝国级主导势力。',
             'features': '6大生态-政治区：中央穹顶群岛、风暴外海、云海下层、碎岛星链、龙骨高原、裂隙空域。中央穹顶群岛存在"天顶之眼"——悬浮空中的巨型风暴漩涡；风暴外海偶尔出现"雷暴龙巢"——纯雷电构成的巨型生物栖息地；云海下层存在体型堪比城市的云海巨兽；龙骨高原中央横卧长达三百公里的超巨型骨骼；裂隙空域存在连接其他碎片甚至其他维度的"空间节点"。'},
            {'number_id': 16, 'name': '寂灭荒漠', 'area': '1200万 km²', 'population': 300000, 'dominant_law': '衰变/存在', 'danger_level': 5, 'max_faction': '寂灭教廷', 'faction_level': '王国级', 'strongest_power': '灵境1阶',
             'description': '无声之墓，被彻底剥夺生机的死亡大陆。沙粒不是硅酸盐而是被彻底剥夺生机的有机质尘埃，气候绝对干燥千年无雨，空气中没有微生物，连风都是沉默的。衰变法则与存在法则交织，使一切趋于绝对的寂灭。寂灭教廷以灵境1阶教皇为最强战力，是碎片人口最稀少的大陆之一。物质被"灰化"后保持原有形态却呈现灰烬质感。',
             'features': '4大生态-政治区：死寂沙海、灰化高原、遗忘山脉、湮灭裂谷。死寂沙海深处"寂静之心"是直径约十公里的绝对无声区域，灵魂会逐渐沉寂；灰化高原物质可压缩为"寂灭砖"——能吸收声音与灵魂的超级建材；遗忘山脉山体吸收光线与热量，"遗忘洞穴"进入者逐渐失去记忆越深层剥夺越古老；湮灭裂谷谷底是不断缓慢扩张的虚无，偶尔喷出"虚无风暴"。'},
            {'number_id': 17, 'name': '萤火深渊', 'area': '1500万 km²', 'population': 8000000, 'dominant_law': '光/暗元素', 'danger_level': 3, 'max_faction': '魂光帝国', 'faction_level': '帝国级', 'strongest_power': '灵境2阶',
             'description': '魂光之渊，以发光生物与灵魂能量为核心的地下世界。光元素与暗元素法则交织，形成永恒的地下黄昏。荧光丛林中巨大蘑菇和藤蔓发出蓝绿色荧光，结晶洞窟的水晶发出柔和各色光芒。灵魂能量充沛，存在以灵魂能量为养分的巨型灵魂树。魂光帝国是帝国级主导势力，居民发展出独特的声学科技与灵魂修炼体系。',
             'features': '5大生态-政治区：荧光丛林、结晶洞窟、暗河深渊、熔岩脉网、遗忘层区。荧光丛林"灵魂树"以灵魂能量为养分，果实能增强灵魂力量；结晶洞窟巨型水晶具有记录和回放声音与记忆的能力；暗河深处"魂光源泉"是灵魂法则核心节点；熔岩脉网存在"魂火"——以灵魂为燃料能燃烧物质与灵体的奇异火焰；遗忘层区"记忆深渊"掉进去的灵魂会失去所有记忆以空白状态重生。'},
            {'number_id': 18, 'name': '圣堂残骸', 'area': '10000万 km²', 'population': 30000000, 'dominant_law': '全法则高浓度', 'danger_level': 5, 'max_faction': '万法圣庭', 'faction_level': '帝国级', 'strongest_power': '灵境3阶',
             'description': '万法之墟，十八碎片中面积最大、最复杂多元的大陆。灾变前文明的圣堂废墟，全法则高浓度（S+全属性），八种法则在此激烈碰撞交织。面积相当于约两个地球陆地面积，人口3000万。法则的极致浓度使整片碎片环境极端危险但也蕴含巨大机遇，是灾变真相与终极力量的可能所在。万法圣庭是帝国级主导势力。',
             'features': '8大生态-政治区：圣墟平原、法则山脉、时痕森林、虚空海、元素熔炉、灵魂花园、秩序迷宫、混乱荒原。法则山脉八种颜色代表八种主导法则，交汇处存在"法则漩涡"；时痕森林"时间之心"时间流速为外界万分之一；虚空海深处"海底神殿"保存完整虚空法则知识；元素熔炉"元素核心"是所有元素法则平衡共存的奇点；灵魂花园"灵魂之树"直径超十公里；秩序迷宫"秩序核心"能预测碎片内一切事件；混乱荒原"混乱之眼"不断产生随机现象，是碎片最危险区域。'},
        ]
        for fw in fragments:
            defaults = {k: v for k, v in fw.items() if k != 'name'}
            defaults['world'] = world
            self._upsert(FragmentWorld, 'fragment_worlds', stats, {'name': fw['name']}, defaults, True)

    def _seed_shenhai_factions(self, stats, world):
        factions = [
            {'name': '铁砧基地', 'level': 'B', 'type': 'light', 'territory': '第一碎片锈蚀荒原·中央高炉区', 'population': 30000, 'leader': '炉主(灵境三阶)', 'description': '主角所属势力，元素金土主导，底层中型据点。依靠金属武器防具对外交换粮食药品，承接低阶天衡积分任务。内部架构：高炉议会(最高领导层)、锻造部(军工冶炼)、巡防队(天衡任务抵御畸变)、劳工部(采矿基础加工)、外务部(对外交易)。短板：资源匮乏，无高阶功法，常年受磐石联邦压制。'},
            {'name': '绿芽公社', 'level': 'C', 'type': 'light', 'territory': '第一碎片锈蚀荒原·东部枯木林', 'population': 8000, 'leader': '生命法则长老', 'description': '生命法则中立聚落。核心优势：抗污染作物、灵魂肉体治愈药剂、变异植物培育。永久中立不参与势力战争，但摧毁林地掠夺植物资源者会遭到生命法则战力围剿。与铁砧基地稳定贸易：草药粮食换取金属农具防具。'},
            {'name': '观星秘会', 'level': 'A', 'type': 'light', 'territory': '第一碎片锈蚀荒原·北方灰岩山脉废弃天文台', 'population': 300, 'leader': '灵魂法则高阶共鸣者', 'description': '灵魂+命运隐秘组织，全员高阶共鸣者。核心能力：预言推演、灵魂污染治疗、禁区情报解析。不占据领土，以情报预言灵魂知识换取资源。少数知晓深骸真实目的、人类共生载体真相的势力。'},
            {'name': '磐石联邦', 'level': 'A', 'type': 'light', 'territory': '第一碎片锈蚀荒原·下辖三座大型聚居地', 'population': 120000, 'leader': '联邦议长(灵境五阶)', 'description': '锈蚀荒原片区最大综合势力，秩序+元素双法则。完整产业链：军工、农耕、法则研究院、专属大型巡防军团。扩张目标：统一第一碎片全部小型据点，对铁砧基地采取招安、资源封锁双重手段。'},
        ]
        for f in factions:
            defaults = {k: v for k, v in f.items() if k != 'name'}
            defaults['world'] = world
            self._upsert(Faction, 'factions', stats, {'name': f['name']}, defaults, True)

    def _seed_shenhai_ability_system(self, stats, world):
        systems = [
            {'name': '法则共鸣体系', 'description': '深骸世界的核心力量体系。人类躯体与本源法则产生适配，可汲取、操控法则之力。法则之力是可量化能量单位，共鸣者战力、突破境界唯一资源。十大本源法则分为四层层级：根源二元层(存在/虚无)、时空框架层(时间/空间)、演化博弈层(生命/灵魂/秩序/混沌)、具象叙事层(元素/命运)。'},
        ]
        for s in systems:
            defaults = {k: v for k, v in s.items() if k != 'name'}
            defaults['world'] = world
            self._upsert(AbilitySystem, 'ability_systems', stats, {'name': s['name']}, defaults, True)

    def _seed_shenhai_realms(self, stats, world):
        system, _ = AbilitySystem.objects.get_or_create(
            name='法则共鸣体系',
            defaults={'description': '深骸世界的核心力量体系。', 'world': world},
        )

        realms_data = [
            # 凡境 1-9 (mortal, level_order 1-9)
            {'name': '凡境一阶', 'tier': 'mortal', 'level_order': 1, 'breakthrough_conditions': '10法则之力', 'abilities_unlocked': '解锁1个烙印被动', 'description': '轻度副作用'},
            {'name': '凡境二阶', 'tier': 'mortal', 'level_order': 2, 'breakthrough_conditions': '40累计法则之力', 'abilities_unlocked': '被动效果小幅强化', 'description': '轻度副作用'},
            {'name': '凡境三阶', 'tier': 'mortal', 'level_order': 3, 'breakthrough_conditions': '130累计法则之力', 'abilities_unlocked': '解锁1个主动术式', 'description': '轻度副作用'},
            {'name': '凡境四阶', 'tier': 'mortal', 'level_order': 4, 'breakthrough_conditions': '400累计法则之力', 'abilities_unlocked': '术式基础增幅', 'description': '轻度副作用'},
            {'name': '凡境五阶', 'tier': 'mortal', 'level_order': 5, 'breakthrough_conditions': '1210累计法则之力', 'abilities_unlocked': '术式范围提升', 'description': '轻度副作用'},
            {'name': '凡境六阶', 'tier': 'mortal', 'level_order': 6, 'breakthrough_conditions': '3640累计法则之力', 'abilities_unlocked': '解锁第二个主动术式', 'description': '轻度副作用'},
            {'name': '凡境七阶', 'tier': 'mortal', 'level_order': 7, 'breakthrough_conditions': '10930累计法则之力', 'abilities_unlocked': '肉身全面法则抗性', 'description': '轻度副作用'},
            {'name': '凡境八阶', 'tier': 'mortal', 'level_order': 8, 'breakthrough_conditions': '32800累计法则之力', 'abilities_unlocked': '术式消耗降低', 'description': '轻度副作用'},
            {'name': '凡境九阶', 'tier': 'mortal', 'level_order': 9, 'breakthrough_conditions': '98410累计法则之力', 'abilities_unlocked': '解锁第三个主动术式，全技能满阶', 'description': '轻度偏重'},
            # 灵境 1-6 (spirit, level_order 10-15)
            {'name': '灵境一阶', 'tier': 'spirit', 'level_order': 10, 'breakthrough_conditions': '298410法则之力', 'abilities_unlocked': '灵魂烙印成型，法则离体释放领域雏形', 'description': '中度副作用'},
            {'name': '灵境二阶', 'tier': 'spirit', 'level_order': 11, 'breakthrough_conditions': '898410法则之力', 'abilities_unlocked': '术式可附着武器防具，感知翻倍', 'description': '中度副作用'},
            {'name': '灵境三阶', 'tier': 'spirit', 'level_order': 12, 'breakthrough_conditions': '2698410法则之力', 'abilities_unlocked': '稳定展开小型法则领域，压制凡境', 'description': '中度偏重'},
            {'name': '灵境四阶', 'tier': 'spirit', 'level_order': 13, 'breakthrough_conditions': '8098410法则之力', 'abilities_unlocked': '领域改写简易物理规则(重力、温度、硬度)', 'description': '重度副作用'},
            {'name': '灵境五阶', 'tier': 'spirit', 'level_order': 14, 'breakthrough_conditions': '24298410法则之力', 'abilities_unlocked': '远程法则攻击成型，豁免中度污染', 'description': '重度副作用'},
            {'name': '灵境六阶', 'tier': 'spirit', 'level_order': 15, 'breakthrough_conditions': '72898410法则之力', 'abilities_unlocked': '领域圆满，触摸本源门槛，冲击天境前置', 'description': '重度极致'},
            # 天境 1-3 (heaven, level_order 16-18)
            {'name': '天境一阶', 'tier': 'heaven', 'level_order': 16, 'breakthrough_conditions': '法则之力达标，领悟法则内核，完成法则试炼', 'abilities_unlocked': '凝聚法则真身，单人摧毁小型据点', 'description': '躯体半数法则化，需意志维持人形。重度极致'},
            {'name': '天境二阶', 'tier': 'heaven', 'level_order': 17, 'breakthrough_conditions': '法则之力达标，领悟法则内核，完成法则试炼', 'abilities_unlocked': '跨碎片世界短途跃迁，单人封印A级禁区', 'description': '人类情感持续淡化。重度极致'},
            {'name': '天境三阶', 'tier': 'heaven', 'level_order': 18, 'breakthrough_conditions': '法则之力达标，领悟法则内核，完成法则试炼', 'abilities_unlocked': '获得圣堂准入资格，短暂沟通深骸集体意志', 'description': '半法则半人，长期沉眠。重度极致'},
            # 圣境 (sage, level_order 19)
            {'name': '圣境', 'tier': 'sage', 'level_order': 19, 'breakthrough_conditions': '仅十大法则圣堂历代主人抵达此境', 'abilities_unlocked': '可直接触碰单一法则本源权能', 'description': '不再属于纯粹人类，是深骸法则代行者。永久徘徊在法则同化、自我消亡边缘，全大陆仅十人上限。'},
        ]

        for r in realms_data:
            defaults = {k: v for k, v in r.items() if k not in ('name', 'level_order', 'tier')}
            defaults['tier'] = r['tier']
            defaults['level_order'] = r['level_order']
            defaults['system'] = system
            defaults['world'] = world
            self._upsert(Realm, 'realms', stats, {'name': r['name']}, defaults, True)

    def _seed_shenhai_skill_levels(self, stats, world):
        system, _ = AbilitySystem.objects.get_or_create(
            name='法则共鸣体系',
            defaults={'description': '深骸世界的核心力量体系。', 'world': world},
        )
        levels = [
            {'name': '烙印被动', 'level_order': 1, 'description': '凡境一阶解锁。常驻自动生效，法则烙印改造肉身/精神，无消耗无冷却。细分：体质增幅、感知强化、光环辐射。'},
            {'name': '术式主动', 'level_order': 2, 'description': '凡境三阶解锁。消耗法则之力主动释放，存在施法动作冷却消耗。细分：单体靶向、范围覆盖、持续结界、具象召唤。'},
            {'name': '领域权能', 'level_order': 3, 'description': '灵境三阶解锁雏形，天境完全掌控。展开专属法则领域改写区域底层物理/概念规则。细分：秩序型领域、混沌型领域、本源专属领域。'},
        ]
        for lv in levels:
            defaults = {'level_order': lv['level_order'], 'description': lv.get('description', ''), 'system': system, 'world': world}
            self._upsert(SkillLevel, 'skill_levels', stats, {'name': lv['name']}, defaults, True)

    def _seed_shenhai_skills(self, stats, world):
        skills = [
            {'name': '锈蚀感知', 'level_name': '烙印被动', 'description': '元素金土法则烙印被动，感知范围内金属结构变化与混沌污染源。', 'effects': '法则探测、畸变感知', 'prerequisites': '凡境一阶', 'cooldown': '无'},
            {'name': '金属塑形', 'level_name': '术式主动', 'description': '操控周边金属物质塑形为武器或防具。', 'effects': '元素塑形、元素操控', 'prerequisites': '凡境三阶', 'cooldown': '30分钟'},
            {'name': '锈域展开', 'level_name': '领域权能', 'description': '展开锈蚀法则领域，领域内金属自主生长重组，敌人装备快速腐蚀。', 'effects': '领域压制、金属操控、装备腐蚀', 'prerequisites': '灵境三阶', 'cooldown': '24小时'},
            {'name': '虚无裂隙', 'level_name': '术式主动', 'description': '撕开小型虚无裂隙，吞噬目标攻击或物质。', 'effects': '湮灭分解、物质消散', 'prerequisites': '灵境一阶', 'cooldown': '2小时'},
            {'name': '生命治愈', 'level_name': '术式主动', 'description': '汲取生命法则之力治愈肉体损伤。', 'effects': '肉体再生、治愈', 'prerequisites': '凡境三阶', 'cooldown': '1小时'},
        ]
        for s in skills:
            level_name = s.pop('level_name')
            level = SkillLevel.objects.filter(name=level_name).first()
            defaults = s.copy()
            if level:
                defaults['level'] = level
            defaults['world'] = world
            self._upsert(Skill, 'skills', stats, {'name': s['name']}, defaults, True)

    def _seed_shenhai_origin_laws(self, stats, world):
        """十大本源法则 - 根據參考資料02完整注入"""
        laws = [
            {'name': '存在法则', 'tier': 'root', 'order': 1,
             'core_definition': '定义「有」，抵抗彻底消解，锚定万物存在根基。',
             'ability_directions': '存在锚定、实体固化、概念强化、无中生有、物质稳定',
             'side_effect': '存在固化——凡境：肢体局部僵硬；灵境：皮肤石化；天境：躯体大面积固化；圣境：完全化为静止雕塑。',
             'description': '根源二元层。一切法则的起点与终点，与虚无法则永久对立制衡。'},
            {'name': '虚无法则', 'tier': 'root', 'order': 2,
             'core_definition': '定义「无」，深骸代谢清理机制，消解多余、污染、腐朽存在。',
             'ability_directions': '湮灭分解、虚无裂隙、记忆抹除、概念消除、物质消散',
             'side_effect': '存在消解——凡境：物品消失，熟人遗忘；灵境：记忆流失；天境：身体透明化；圣境：彻底从时空消失。',
             'description': '根源二元层。与存在法则对立制衡，构成深骸生命基础。'},
            {'name': '时间法则', 'tier': 'framework', 'order': 3,
             'core_definition': '赋予世界时序、因果、变化节律，深骸生命脉搏。',
             'ability_directions': '时间加速/延缓、时间静止、时序回溯、时间断层、衰老调控',
             'side_effect': '时间错位——凡境：记忆跳段；灵境：衰老返幼；天境：意识割裂；圣境：随机穿梭过去未来。',
             'description': '时空框架层。承载所有物质、意识、事件的基础框架。'},
            {'name': '空间法则', 'tier': 'framework', 'order': 4,
             'core_definition': '深骸物理躯体，承载所有物质、生灵的容器。',
             'ability_directions': '瞬移、空间切割、储物异空间、空间屏障、空间裂隙、隐身',
             'side_effect': '空间碎裂——凡境：肢体错位；灵境：身体穿梭不同空间；天境：躯体散落不同空间；圣境：化为无序空间乱流。',
             'description': '时空框架层。与时间法则共同构成世界承载容器。'},
            {'name': '命运法则', 'tier': 'narrative', 'order': 5,
             'core_definition': '时间、秩序、混沌、灵魂交织形成的概率因果网络，历史惯性。',
             'ability_directions': '气运加持、厄运诅咒、命运窥探、因果扭转、预言、命运收束',
             'side_effect': '命运收束——凡境：小事走向坏结果；灵境：所有选择导向悲剧；天境：命运线被锁死；圣境：无限循环死亡结局。',
             'description': '具象叙事层。全部法则交织形成的概率因果网络。'},
            {'name': '灵魂法则', 'tier': 'evolution', 'order': 6,
             'core_definition': '深骸集体意识载体，承载个体记忆、意志、自我认知。',
             'ability_directions': '灵魂冲击、灵魂实体化、灵魂契约、灵视、魅惑、引魂、意识修复',
             'side_effect': '意识溶解——凡境：听见杂音；灵境：吸纳亡者意识；天境：自我边界消失；圣境：人格消散沦为灵体容器。',
             'description': '演化博弈层。驱动世界演化、生灵诞生的核心动力之一。'},
            {'name': '生命法则', 'tier': 'evolution', 'order': 7,
             'core_definition': '深骸活性本能，在无序中构建有序生命系统。',
             'ability_directions': '肉体再生、生机汲取、共生、生物拟态、基因调和、兽化、治愈',
             'side_effect': '无限增殖——凡境：毛发疯长；灵境：多余器官增生；天境：化为血肉聚合体；圣境：覆盖世界的血肉灾潮。',
             'description': '演化博弈层。与灵魂、秩序、混沌法则持续博弈。'},
            {'name': '秩序法则', 'tier': 'evolution', 'order': 8,
             'core_definition': '深骸稳态倾向，建立稳定、可预测的固定规则。',
             'ability_directions': '规则约束、领域稳定、法则模拟、秩序烙印、预判推演',
             'side_effect': '绝对秩序化——凡境：偏执刻板；灵境：情绪消失；天境：自主意识剥离；圣境：化为纯粹规则傀儡。',
             'description': '演化博弈层。与混沌法则天然对立。'},
            {'name': '混沌法则', 'tier': 'evolution', 'order': 9,
             'core_definition': '深骸进化变异动力，注入随机、破坏、突变，打破固化稳态。',
             'ability_directions': '规则侵蚀、无序畸变、能量暴走、冲突制造、随机进化',
             'side_effect': '混沌畸变——凡境：外貌情绪突变；灵境：器官随机重组；天境：理智丧失；圣境：化为移动混沌乱流。',
             'description': '演化博弈层。与秩序法则天然对立，打破固化稳态。'},
            {'name': '元素法则', 'tier': 'narrative', 'order': 10,
             'core_definition': '深骸血肉与基础能量，一切物质世界的底层构成材料。',
             'ability_directions': '元素塑形、元素操控、元素护盾、元素召唤、能量转化',
             'side_effect': '元素化——凡境：皮肤出现元素特征；灵境：身体一半元素化；天境：人形勉强维持；圣境：化为纯粹元素聚合体。',
             'description': '具象叙事层。细分元素分支：土石金属、水火、风雷、植物、磁能、超微原子。所有法则落地的物质载体。'},
        ]
        for law in laws:
            defaults = {k: v for k, v in law.items() if k != 'name'}
            defaults['world'] = world
            self._upsert(OriginLaw, 'origin_laws', stats, {'name': law['name']}, defaults, True)

    def _seed_shenhai_artifact_categories(self, stats, world):
        categories = [
            {'name': '本源圣器', 'description': '伴随深骸诞生的本源法则具象载体，灾变后大多碎裂。单块碎片即可释放高阶力量，完整圣器等同圣境战力。', 'rarity_level': 'SSS'},
            {'name': '异常物', 'description': '高位面污染与法则之力交织形成的异常物品，三重标签划分：危险等级(C/B/A/S/X)、本源法则属性、功能类型(攻击/防御/辅助/诅咒/自主意识)。', 'rarity_level': 'S'},
            {'name': '法则碎片', 'description': '破碎世界法则的实体化碎片，可直接炼化提升法则之力。', 'rarity_level': 'SS'},
            {'name': '天衡物资', 'description': '天衡系统任务奖励的功能性物品，包括净化药剂、功法卷轴等。', 'rarity_level': 'A'},
        ]
        for cat in categories:
            defaults = {k: v for k, v in cat.items() if k != 'name'}
            defaults['world'] = world
            self._upsert(ArtifactCategory, 'artifact_categories', stats, {'name': cat['name']}, defaults, True)

    def _seed_shenhai_artifacts(self, stats, world):
        artifacts = [
            # 本源圣器 (10)
            {'name': '永固王座', 'category_name': '本源圣器', 'rarity_level': 'SSS', 'owner_name': None, 'origin': '18/15/1/10碎片世界', 'description': '存在法则圣器。锚定一切存在，免疫虚无抹除，固化任何物质/意识。碎裂七块。', 'effects': '存在锚定、实体固化、概念强化'},
            {'name': '虚无魂龛', 'category_name': '本源圣器', 'rarity_level': 'SSS', 'owner_name': None, 'origin': '第六碎片虚无裂谷核心', 'description': '虚无法则圣器。收纳万物，抹除概念，永久封印任何畸变存在。本体完整。', 'effects': '湮灭分解、概念消除、封印'},
            {'name': '时之沙漏', 'category_name': '本源圣器', 'rarity_level': 'SSS', 'owner_name': None, 'origin': '第十四碎片逆流长河', 'description': '时间法则圣器。局部时序操控，短时间回溯单一事件线。整体碎裂。', 'effects': '时间加速/延缓、时序回溯、时间静止'},
            {'name': '界门之钥', 'category_name': '本源圣器', 'rarity_level': 'SSS', 'owner_name': None, 'origin': '第十五碎片裂空群岛', 'description': '空间法则圣器。自由开启跨碎片空间通道，切割空间屏障。主体遗失仅少量碎片现世。', 'effects': '瞬移、空间切割、空间屏障'},
            {'name': '命运纺轮', 'category_name': '本源圣器', 'rarity_level': 'SSS', 'owner_name': None, 'origin': '第七碎片镜面沙海', 'description': '命运法则圣器。改写个体因果线，扭转短期厄运/气运。完整保存。', 'effects': '气运加持、厄运诅咒、因果扭转'},
            {'name': '万魂灯', 'category_name': '本源圣器', 'rarity_level': 'SSS', 'owner_name': None, 'origin': '第十七碎片萤火深渊', 'description': '灵魂法则圣器。收纳亡者灵魂，重塑破碎意识，沟通远古灵体。完整。', 'effects': '灵魂冲击、灵魂实体化、灵视'},
            {'name': '生命母树', 'category_name': '本源圣器', 'rarity_level': 'SSS', 'owner_name': None, 'origin': '第三碎片翡翠天穹', 'description': '生命法则圣器。无尽生机供给，治愈重度法则损伤，短暂复活濒死者。本体存活。', 'effects': '肉体再生、治愈、共生'},
            {'name': '秩序法典', 'category_name': '本源圣器', 'rarity_level': 'SSS', 'owner_name': None, 'origin': '第十碎片铁幕山岳', 'description': '秩序法则圣器。划定领域规则，压制一切混沌、无序畸变。完整供奉。', 'effects': '规则约束、领域稳定、法则模拟'},
            {'name': '混沌炉心', 'category_name': '本源圣器', 'rarity_level': 'SSS', 'owner_name': None, 'origin': '第十三碎片腐沼深渊', 'description': '混沌法则圣器。崩坏区域规则，催生无限畸变与进化。完整封印。', 'effects': '规则侵蚀、无序畸变、随机进化'},
            {'name': '元素原核', 'category_name': '本源圣器', 'rarity_level': 'SSS', 'owner_name': None, 'origin': '第一碎片锈蚀荒原核心', 'description': '元素法则圣器。统御全部元素能量，重塑金属水火风雷物质。碎裂多块。第一碎片埋藏碎片是中后期主线争夺核心道具。', 'effects': '元素塑形、元素操控、能量转化'},
            # 异常物 (4)
            {'name': '锈蚀铁钉', 'category_name': '异常物', 'rarity_level': 'C', 'owner_name': None, 'origin': '锈蚀荒原高炉废弃工地', 'description': 'C级异常物，元素金土+混沌，攻击型。手掌长锈铁钉持续散发暗红色微光。划伤目标后伤口永久溃烂，普通自愈术式无效。', 'effects': '伤口溃烂、金属锈蚀加速'},
            {'name': '忘忧石', 'category_name': '异常物', 'rarity_level': 'B', 'owner_name': None, 'origin': '观星秘会', 'description': 'B级异常物，虚无法则，辅助/诅咒双属性。灰白色光滑卵石握持有失重感。抹除目标72小时指定记忆，中和轻度灵魂污染。', 'effects': '记忆抹除、灵魂净化'},
            {'name': '时之残片', 'category_name': '异常物', 'rarity_level': 'A', 'owner_name': None, 'origin': '第十四碎片逆流长河时间断层', 'description': 'A级异常物，时间法则，辅助攻击型。透明晶体内部流动金色时序纹路。5米范围时间加速/延缓3倍持续10秒。', 'effects': '时间加速/延缓'},
            {'name': '混沌锈炉芯', 'category_name': '异常物', 'rarity_level': 'S', 'owner_name': None, 'origin': '第一碎片锈蚀荒原齿轮峡谷中层', 'description': 'S级异常物，混沌+元素金土，自主意识型。自主催生锈蚀机械畸变体，大范围混沌污染扩散。全锈蚀荒原仅三块。', 'effects': '畸变体催生、混沌污染扩散、金属增殖'},
        ]
        for a in artifacts:
            category_name = a.pop('category_name')
            owner_name = a.pop('owner_name')
            category = ArtifactCategory.objects.filter(name=category_name).first()
            owner = Character.objects.filter(name=owner_name).first() if owner_name else None
            defaults = a.copy()
            if category:
                defaults['category'] = category
            defaults['owner'] = owner
            defaults['world'] = world
            self._upsert(Artifact, 'artifacts', stats, {'name': a['name']}, defaults, True)

    def _seed_shenhai_anomalies(self, stats, world):
        """异常物 - 根據參考資料07完整注入"""
        anomalies = [
            {'name': '锈蚀铁钉', 'danger_level': 'C', 'law_attribute': '元素金土+混沌', 'function_type': 'attack',
             'appearance': '手掌长锈铁钉，持续散发暗红色微光',
             'ability': '划伤目标后伤口永久溃烂，普通自愈术式无效；加速范围内金属锈蚀风化',
             'side_effect': '长期携带者手指硬化，指甲金属化',
             'origin': '锈蚀荒原、高炉废弃工地',
             'description': 'C级异常物。第一碎片锈蚀荒原最常见的低阶异常物。'},
            {'name': '忘忧石', 'danger_level': 'B', 'law_attribute': '虚无法则', 'function_type': 'support',
             'appearance': '灰白色光滑卵石，握持存在失重感',
             'ability': '抹除目标72小时指定记忆，中和轻度灵魂污染',
             'side_effect': '每使用一次，使用者随机丢失一段私人记忆',
             'origin': '观星秘会高阶灵魂医师持有',
             'description': 'B级异常物。辅助/诅咒双属性，观星秘会专属。'},
            {'name': '时之残片', 'danger_level': 'A', 'law_attribute': '时间法则', 'function_type': 'attack',
             'appearance': '透明晶体，内部流动金色时序纹路',
             'ability': '5米范围时间加速/延缓3倍，持续10秒',
             'side_effect': '每次使用加速自身衰老，频繁使用触发时间错位病症',
             'origin': '第十四碎片逆流长河时间断层',
             'description': 'A级异常物。辅助攻击型，时间法则属性。'},
            {'name': '混沌锈炉芯', 'danger_level': 'S', 'law_attribute': '混沌+元素金土', 'function_type': 'autonomous',
             'appearance': '暗红色熔炉核心，表面持续涌动锈蚀金属纹理',
             'ability': '自主催生锈蚀机械畸变体，大范围混沌污染扩散，金属无限增殖',
             'side_effect': '持有者持续躯体畸变，失去人形，完全被混沌支配',
             'origin': '第一碎片锈蚀荒原齿轮峡谷中层',
             'description': 'S级异常物。全锈蚀荒原仅三块。自主意识型，极其危险。'},
        ]
        for a in anomalies:
            defaults = {k: v for k, v in a.items() if k != 'name'}
            defaults['world'] = world
            self._upsert(Anomaly, 'anomalies', stats, {'name': a['name']}, defaults, True)

    def _seed_shenhai_creatures(self, stats, world):
        creatures = [
            # 原生畸变体
            {'name': '锈蚀猎犬', 'species': '原生畸变体', 'danger_level': 1, 'habitat_name': '锈蚀荒原', 'abilities': '全身覆盖锈蚀金属硬甲，高速集群捕猎', 'description': '衰变混沌污染畸变。钢铁议会外围最常见威胁。'},
            {'name': '岩甲巨鼠', 'species': '原生畸变体', 'danger_level': 2, 'habitat_name': '锈蚀荒原', 'abilities': '啃食金属矿石，牙齿可撕裂普通钢铁防具', 'description': '栖息废铁山脉矿洞。'},
            {'name': '锈铁巨犀', 'species': '原生畸变体', 'danger_level': 4, 'habitat_name': '锈蚀荒原', 'abilities': '躯体融合废弃钢板，冲撞可摧毁小型据点围墙', 'description': '齿轮峡谷外围游荡。'},
            # 深骸伴生种
            {'name': '元素之灵', 'species': '深骸伴生种', 'danger_level': 3, 'habitat_name': None, 'abilities': '纯粹能量聚合体，分火土风水分支，主动清理畸变污染', 'description': '深骸原生生物，天然高法则亲和，无高位面污染。'},
            {'name': '石肤守卫', 'species': '深骸伴生种', 'danger_level': 4, 'habitat_name': None, 'abilities': '深骸天然免疫细胞，无自主意识，攻击一切携带高位面污染的生物', 'description': '深骸原生生物。'},
            {'name': '法则蠕虫', 'species': '深骸伴生种', 'danger_level': 1, 'habitat_name': None, 'abilities': '以游离法则之力为食，无主动攻击性', 'description': '富集法则区域大量滋生。'},
            # 高位面扭曲种
            {'name': '裂隙低语者', 'species': '高位面扭曲种', 'danger_level': 5, 'habitat_name': '镜面沙海', 'abilities': '依靠声波传播意识污染，潜藏时空裂隙，迷惑人类自相残杀', 'description': '高维打击外来存在，认知即遭受精神侵蚀。'},
            {'name': '概念吞噬体', 'species': '高位面扭曲种', 'danger_level': 6, 'habitat_name': '圣堂残骸', 'abilities': '吞噬目标的存在概念，使其被全世界生物彻底遗忘，常规攻击完全无效', 'description': '概念级污染载体。'},
            {'name': '时空畸点', 'species': '高位面扭曲种', 'danger_level': 6, 'habitat_name': '逆流长河', 'abilities': '无实体不定型畸变，触碰者卷入无限时空循环永久失踪', 'description': '概念级污染载体。'},
        ]
        for c in creatures:
            habitat_name = c.pop('habitat_name')
            habitat = FragmentWorld.objects.filter(name=habitat_name).first() if habitat_name else None
            defaults = c.copy()
            if habitat:
                defaults['habitat'] = habitat
            defaults['world'] = world
            self._upsert(Creature, 'creatures', stats, {'name': c['name']}, defaults, True)

    def _seed_shenhai_historical_events(self, stats, world):
        events = [
            {'name': '高维概念打击', 'era': 'era1', 'date_description': '灾变元年', 'description': '超脱现有时空物质法则体系的高位面概念存在对深骸进行概念覆盖抹除打击。深骸本体发生概念性碎裂，巨型残躯跃迁途经太阳系冲击撕裂地球，分裂为18块碎片世界。旧文明90%人口瞬间消亡，全域法则污染爆发。', 'consequences': '世界碎裂、法则分散、人类濒临灭绝'},
            {'name': '初代共鸣者诞生', 'era': 'era1', 'date_description': '灾变3年', 'description': '首批存活人类被动觉醒法则亲和，初代共鸣者诞生，仅能无意识微弱调动法则之力。', 'consequences': '人类开始拥有抗争之力'},
            {'name': '天衡系统激活', 'era': 'era1', 'date_description': '灾变30年', 'description': '深骸脱离深度休眠，自动化执行程序天衡系统正式激活，第二纪元萌芽引导期开启。', 'consequences': '任务体系落地、文明重建开始'},
            {'name': '曙光城建成', 'era': 'era2', 'date_description': '灾变76年', 'description': '一号碎片锈蚀荒原建成全人类首个巨型城邦曙光城，文明复兴起点。', 'consequences': '人类文明复兴'},
            {'name': '铁砧基地建立', 'era': 'era2', 'date_description': '灾变112年', 'description': '第一碎片锈蚀荒原幸存者依托旧钢铁厂废墟建立铁砧基地。', 'consequences': '锈蚀荒原人类据点成型'},
            {'name': '法则体系成型', 'era': 'era2', 'date_description': '灾变150年', 'description': '十大法则修炼体系完整成型，各大派系势力割据格局稳定。', 'consequences': '势力格局确立'},
            {'name': '深潜纪元开启', 'era': 'era2', 'date_description': '灾变180年', 'description': '深骸判定人类抗性达标，天衡系统全面升级，深潜纪元正式开启。', 'consequences': '修复进入攻坚阶段'},
            {'name': '黑潮事件', 'era': 'era3', 'date_description': '灾变213年', 'description': '第十三碎片腐沼深渊混沌禁区大规模泄露，数十中小型据点覆灭，势力格局大洗牌。', 'consequences': '大量据点覆灭、格局洗牌'},
            {'name': '圣器碎片出土', 'era': 'era3', 'date_description': '灾变241年', 'description': '第十四碎片逆流长河出土第一块时间沙漏圣器碎片，全碎片世界掀起圣器争夺战乱。', 'consequences': '圣器争夺战乱'},
            {'name': '红锈熔炉S级任务', 'era': 'era3', 'date_description': '灾变253年', 'description': '第一碎片锈蚀荒原齿轮峡谷污染指数持续飙升，天衡发布永久长期S级驻守任务。', 'consequences': '高阶共鸣者试炼场设立'},
            {'name': '当前故事开始', 'era': 'era3', 'date_description': '灾变256年', 'description': '当前故事时间线，主角于铁砧基地开启剧情。', 'consequences': '主线剧情开始'},
        ]
        for e in events:
            defaults = {k: v for k, v in e.items() if k != 'name'}
            defaults['world'] = world
            self._upsert(HistoricalEvent, 'historical_events', stats, {'name': e['name']}, defaults, True)

    def _seed_shenhai_lore_pages(self, stats, world):
        pages = [
            {'title': '深骸世界观总纲', 'slug': 'shenhai-overview', 'category': 'core', 'order': 1, 'content': '深骸是诞生于宇宙原初混沌的法则聚合型至高生命体，自身完整承载十大本源法则，躯体等同于独立微型宇宙。高维概念打击致其碎裂，巨型残躯跃迁撞击地球，撕裂为18块碎片世界。人类作为深骸的共生免疫细胞，在法则共鸣中抗争求存。核心基调：宇宙史诗、宿命压抑、共生博弈、不可名状高维恐怖。'},
            {'title': '十大本源法则', 'slug': 'ten-origin-laws', 'category': 'power', 'order': 2, 'content': '构筑一切存在的十条底层规则，分四层层级：根源二元层(存在/虚无)、时空框架层(时间/空间)、演化博弈层(生命/灵魂/秩序/混沌)、具象叙事层(元素/命运)。每条法则有可用术式方向和过度亲和副作用。复合法则仅同层级可共存。'},
            {'title': '法则共鸣体系', 'slug': 'resonance-system', 'category': 'power', 'order': 3, 'content': '人类躯体与本源法则产生适配，可汲取、操控法则之力。法则之力是可量化能量单位。获取途径：自然吸收、富集环境吸收、异常物/圣器辅助、法则碎片炼化、天衡任务奖励。技能分三大类：烙印被动(凡境一阶)、术式主动(凡境三阶)、领域权能(灵境三阶)。'},
            {'title': '境界阶梯', 'slug': 'realm-ladder', 'category': 'power', 'order': 4, 'content': '四大境界：凡境·肉身共鸣阶(9阶)、灵境·灵魂铭刻阶(6阶)、天境·法则具象阶(3阶)、圣境·本源触摸阶(传说)。法则之力累计达标+领悟法则内核+完成法则试炼方可突破。高阶对低阶存在天然法则压制。'},
            {'title': '碎片世界地理', 'slug': 'fragment-geography', 'category': 'geography', 'order': 5, 'content': '灾变冲击将地球撕裂为18块独立大陆碎片，被薄弱时空壁垒隔绝。每块碎片被单一/双本源法则深度浸染，地貌生态污染类型完全区分。第一碎片锈蚀荒原为主角主场，旧工业钢铁废墟风格。'},
            {'title': '天衡系统', 'slug': 'tianheng-system', 'category': 'civilization', 'order': 6, 'content': '深骸意志休眠后的自动化修复执行程序，无自主情感。四大优先级：稳固时空结构、清理污染、筛选培育共鸣者、收集迭代数据。任务分C/B/A/S/X五级，七大类型。隐藏机制：高阶任务本质是压力测试。'},
            {'title': '高位面污染', 'slug': 'pollution', 'category': 'civilization', 'order': 7, 'content': '高维打击残留的扭曲概念，分四级：轻度(皮肤接触)、中度(体液接触)、重度(空气扩散/视线直视)、概念级(信息传播-看见听见即被侵蚀)。制造畸变、禁区、异常物。'},
            {'title': '势力与人文', 'slug': 'factions-culture', 'category': 'civilization', 'order': 8, 'content': '通用社会阶层五层：顶层掌权层(灵境+)、正式战力层(凡境3-9阶)、预备共鸣层(凡境1-2阶)、普通平民层、流民畸变层。通用货币：天衡积分(跨世界硬通货)+据点本土实物货币。三大绝对禁忌。'},
        ]
        for p in pages:
            defaults = {k: v for k, v in p.items() if k != 'slug'}
            defaults['world'] = world
            self._upsert(LorePage, 'lore_pages', stats, {'slug': p['slug']}, defaults, True)
