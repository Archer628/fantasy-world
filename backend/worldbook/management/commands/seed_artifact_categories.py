"""
Django management command: seed_artifact_categories
一键导入 20+ 通用宝物分类预置模板（修真 + 西幻 + 通用混合体系）。

这些宝物种类在 ArtifactCategory 中 world 字段为 NULL，表示全局共用，
所有大世界下的宝物编辑器都可使用它们作为下拉选项。

Usage:
    python manage.py seed_artifact_categories
    python manage.py seed_artifact_categories --force   # 覆盖更新已有同名种类
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from worldbook.models import ArtifactCategory


# ============================================================
# 预置宝物分类模板
# ============================================================
# rarity_level: SSS = 至高 / SS = 传说 / S = 史诗 / A = 稀有 / B = 优质 / C = 普通
# world: None -> 全局共用（基础设定中使用）
PRESET_CATEGORIES = [
    # ===================== 修真系列（10 种） =====================
    {
        'name': '法器',
        'rarity_level': 'A',
        'description': '修真者的战斗兵器与辅助法宝。飞剑、拂尘、法印、法轮、宝镜、魂灯……从低阶法器到仙器、神器的通用分类。',
    },
    {
        'name': '丹药',
        'rarity_level': 'B',
        'description': '炼丹师炼制的修行辅助药物。回气丹、聚灵丹、筑基丹、破障丹、九转金丹、长生丹……品级从凡丹到仙丹。',
    },
    {
        'name': '阵法',
        'rarity_level': 'A',
        'description': '阵法师布置的天地大阵。护山大阵、聚灵阵、传送阵、迷踪阵、诛仙剑阵、周天星斗大阵……',
    },
    {
        'name': '符箓',
        'rarity_level': 'C',
        'description': '以灵墨朱砂绘制的一次性消耗品。引火符、御风符、护身符、传音符、五雷符、封神符……',
    },
    {
        'name': '灵草',
        'rarity_level': 'C',
        'description': '天地灵草、仙药、灵药。朱果、黄精、紫河车、千年灵芝、万年雪莲、悟道茶树……炼丹主料。',
    },
    {
        'name': '功法',
        'rarity_level': 'A',
        'description': '修行典籍与传承秘法。吐纳法、心法、剑谱、秘录、古经、帝经、吞天魔功……决定修行上限。',
    },
    {
        'name': '御兽',
        'rarity_level': 'B',
        'description': '可驯化、可契约的灵宠/妖兽。灵鹤、青牛、九尾天狐、真灵凤凰、龙子、鲲鹏……',
    },
    {
        'name': '灵材',
        'rarity_level': 'B',
        'description': '炼器/炼丹的天地灵材。玄铁、赤铜、秘银、星辰金、太阴精石、混沌原石……',
    },
    {
        'name': '仙府',
        'rarity_level': 'S',
        'description': '移动/固定洞府空间。储物袋、储物戒、须弥芥子、随身小世界、洞天福地、独立仙府……',
    },
    {
        'name': '传承印记',
        'rarity_level': 'SS',
        'description': '远古大能留下的传承印记。金丹传承、道韵烙印、圣人骨血、帝玉、古殿令符……获取即获得大机缘。',
    },

    # ===================== 西幻 / D&D 系列（10 种） =====================
    {
        'name': '法杖',
        'rarity_level': 'A',
        'description': '法师与术士的施法媒介。学徒法杖、橡木法杖、秘银法杖、巫妖骨杖、龙息法杖、世界树之杖……',
    },
    {
        'name': '药水',
        'rarity_level': 'C',
        'description': '炼金术士调配的消耗品。生命药水、魔力药水、次级复原药剂、隐身药水、龙息药剂、不朽药剂……',
    },
    {
        'name': '魔法卷轴',
        'rarity_level': 'B',
        'description': '一次性固化的法术卷轴。火球术卷轴、传送术卷轴、九级禁咒卷轴、复活卷轴、大预言卷轴……',
    },
    {
        'name': '圣器',
        'rarity_level': 'S',
        'description': '受神灵祝福或承载传说之力的神圣物品。圣杯、圣剑、龙晶权杖、圣光护符、荆棘王冠……',
    },
    {
        'name': '魔核',
        'rarity_level': 'B',
        'description': '魔兽体内凝结的能量核心。低阶魔核、七阶魔核、龙晶、恶魔心脏、上古魔魂结晶……炼金/锻造主料。',
    },
    {
        'name': '炼金药剂',
        'rarity_level': 'A',
        'description': '炼金术士的高阶作品。巨魔之血、真理药剂、变形药剂、永恒之水、贤者之石……与普通药水区分开。',
    },
    {
        'name': '魔法饰品',
        'rarity_level': 'B',
        'description': '可佩戴的附魔饰品。附魔戒指、护符、项链、耳环、护腕、腰带……常附带被动或主动法术效果。',
    },
    {
        'name': '附魔武器',
        'rarity_level': 'A',
        'description': '经过附魔/符文加持的武器。符文剑、烈焰斧、寒冰长弓、破魔战锤、龙牙匕首、斩神巨剑……',
    },
    {
        'name': '神器',
        'rarity_level': 'SSS',
        'description': '真神铸造或承载神职的至高造物。雷神之锤、冥王之剑、命运之书、混沌之心、世界之树种子……',
    },
    {
        'name': '魔法道具',
        'rarity_level': 'C',
        'description': '泛用型魔法物品。魔法灯笼、飞毯、次元口袋、魔法塔模型、传送门钥匙、占卜水晶球……',
    },

    # ===================== 通用 / 跨作品（6 种） =====================
    {
        'name': '神兵',
        'rarity_level': 'S',
        'description': '不分体系的顶级兵器通称。神剑、魔刀、圣器、仙兵、神枪……属于该世界最顶尖的武器类别。',
    },
    {
        'name': '防具',
        'rarity_level': 'B',
        'description': '各类护具。铠甲、道袍、法袍、战甲、披风、护心镜、内甲……',
    },
    {
        'name': '秘典',
        'rarity_level': 'A',
        'description': '记载禁忌知识的古籍。魔法书、禁忌之书、亡灵黑经、天帝玉册、天书残页……',
    },
    {
        'name': '异火',
        'rarity_level': 'S',
        'description': '天地奇火。三昧真火、净世白莲焰、虚无吞炎、骨灵冷火、太阳金焰……炼丹炼器/战斗多用。',
    },
    {
        'name': '血脉信物',
        'rarity_level': 'SS',
        'description': '承载种族/家族血脉的信物。龙晶、麒麟角、凤凰羽、伏羲骨、神圣血脉晶核……用于觉醒或传承。',
    },
    {
        'name': '杂物',
        'rarity_level': 'C',
        'description': '未分类的普通物品。地图、钥匙、酒葫芦、香烛、灵石袋、传讯玉牌……不好归类时使用此项。',
    },
]


class Command(BaseCommand):
    help = '一键导入 26 种通用宝物分类预置模板（修真 + 西幻 + 通用）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制覆盖更新已存在的同名种类（默认只创建新的）',
        )

    def handle(self, *args, **options):
        force = options['force']
        created = 0
        updated = 0
        skipped = 0

        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS(f'  宝物种类预置模板注入 - 共 {len(PRESET_CATEGORIES)} 项'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

        with transaction.atomic():
            for cat in PRESET_CATEGORIES:
                existing = ArtifactCategory.objects.filter(
                    name=cat['name'],
                    world__isnull=True,  # 只匹配全局共用的
                ).first()

                if existing:
                    if force:
                        existing.rarity_level = cat['rarity_level']
                        existing.description = cat['description']
                        # world 保持 None（全局）
                        existing.save(update_fields=['rarity_level', 'description'])
                        updated += 1
                        self.stdout.write(
                            f'  [更新] {cat["name"]:12s}  ({cat["rarity_level"]:3s})  - '
                            f'{cat["description"][:24]}...'
                        )
                    else:
                        skipped += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f'  [跳过] {cat["name"]:12s}  已存在（使用 --force 可覆盖更新）'
                            )
                        )
                else:
                    ArtifactCategory.objects.create(
                        name=cat['name'],
                        rarity_level=cat['rarity_level'],
                        description=cat['description'],
                        world=None,  # 全局共用
                    )
                    created += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  [新建] {cat["name"]:12s}  ({cat["rarity_level"]:3s})  - '
                            f'{cat["description"][:24]}...'
                        )
                    )

        # 汇总
        total = ArtifactCategory.objects.filter(world__isnull=True).count()
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('-' * 60))
        self.stdout.write(self.style.SUCCESS('  宝物种类预置 - 完成统计'))
        self.stdout.write(self.style.SUCCESS('-' * 60))
        self.stdout.write(f'    新建：{created}')
        self.stdout.write(f'    更新：{updated}')
        self.stdout.write(f'    跳过：{skipped}')
        self.stdout.write(self.style.SUCCESS(f'    当前全局宝物种类数：{total}'))
