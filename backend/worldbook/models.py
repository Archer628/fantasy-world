from django.db import models


# ============================================================
# 0. World - 大世界设定
# ============================================================
class World(models.Model):
    """大世界设定 - 支持多个独立世界观"""
    name = models.CharField('世界名称', max_length=200, unique=True)
    slug = models.SlugField('URL别名', max_length=200, unique=True)
    subtitle = models.CharField('副标题', max_length=500, blank=True, default='')
    description = models.TextField('世界简介', blank=True, default='')
    tone = models.CharField('核心基调', max_length=500, blank=True, default='')
    is_active = models.BooleanField('启用', default=True)
    order = models.PositiveIntegerField('排序', default=0)
    cover_image = models.ImageField('封面图', upload_to='worlds/covers/', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '大世界'
        verbose_name_plural = '大世界'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


# ============================================================
# 1. Faction - 种族 & 势力（统一模型，category 字段区分）
#
#  category = 'race'   → 种族（生灵的物种/血脉分类，支持多层级：人族 → 中原人 / 北境人）
#  category = 'force'  → 势力（由生灵组成的组织团体：宗门 / 王国 / 商会 / 公会等）
#
#  通过 type 字段进一步细分：
#    RACE_TYPES   → 18 种常见种族大类（人族、精灵族、兽人族、矮人族、龙族、海族……）
#    FORCE_TYPES  → 22 种常见势力类型（宗门、皇朝、商会、公会、教派、骑士团……）
# ============================================================
class Faction(models.Model):
    CATEGORY_CHOICES = [
        ('race',  '种族'),
        ('force', '势力'),
    ]
    LEVEL_CHOICES = [
        ('S', 'S 级'),
        ('E', 'E 级'),
        ('A', 'A 级'),
        ('B', 'B 级'),
        ('C', 'C 级'),
    ]
    # ---------- 种族类 type ----------
    RACE_TYPES = [
        ('human',      '人族'),
        ('elf',        '精灵族'),
        ('dwarf',      '矮人族'),
        ('orc',        '兽人族'),
        ('beastman',   '牛头人/半兽类'),
        ('dragon',     '龙族'),
        ('sea',        '海族'),
        ('fish',       '鱼人/人鱼族'),
        ('demon',      '魔族'),
        ('devil',      '恶魔族'),
        ('angel',      '天使族'),
        ('undead',     '亡灵/不死族'),
        ('fairy',      '妖精/小仙子'),
        ('giant',      '巨人族'),
        ('gnome',      '侏儒/地精族'),
        ('insect',     '虫族/昆虫类'),
        ('druid',      '德鲁伊/自然之子'),
        ('monster',    '妖族/精怪族'),
        ('god',        '神族/上界生灵'),
        ('mixed',      '混血/亚人种'),
        ('other_race', '其他种族'),
    ]
    # ---------- 势力类 type ----------
    FORCE_TYPES = [
        ('sect',         '宗门/道统'),
        ('clan',         '世家/家族'),
        ('dynasty',      '皇朝/帝国'),
        ('kingdom',      '王国/公国'),
        ('tribe',        '部落/部族'),
        ('church',       '教会/教派'),
        ('temple',       '神殿/禅院'),
        ('guild',        '公会/行会'),
        ('commerce',     '商会/财阀'),
        ('knight_order', '骑士团'),
        ('mage_tower',   '法师塔/法师学院'),
        ('assassin',     '刺客组织'),
        ('thieves',      '盗贼工会/地下势力'),
        ('mercenary',    '佣兵团'),
        ('adventurer',   '冒险者联盟'),
        ('academy',      '学院/书院'),
        ('senate',       '议会/元老院'),
        ('alliance',     '联盟/阵营'),
        ('resistance',   '反抗军/革命军'),
        ('royal',        '王室/贵族门阀'),
        ('shadow',       '暗部/密探机构'),
        ('other_force',  '其他势力'),
    ]
    # 合成 TYPE_CHOICES 供 Django admin 使用
    TYPE_CHOICES = RACE_TYPES + FORCE_TYPES

    world = models.ForeignKey(
        'World', verbose_name='所属世界',
        on_delete=models.CASCADE, related_name='%(class)ss',
        null=True, blank=True
    )
    category = models.CharField(
        '大类（种族/势力）', max_length=8, choices=CATEGORY_CHOICES, default='force',
        help_text='种族 = 生灵的血脉分类（人族/精灵族…）；势力 = 组织团体（宗门/王国…）'
    )
    name = models.CharField('名称', max_length=200, unique=True)
    description = models.TextField('描述', blank=True, default='')
    level = models.CharField('等级', max_length=1, choices=LEVEL_CHOICES, default='C')
    type = models.CharField(
        '细分类型', max_length=20, choices=TYPE_CHOICES, default='other_force',
        help_text='种族类：人族/精灵族/龙族…  势力类：宗门/王国/商会…'
    )
    parent_faction = models.ForeignKey(
        'self', verbose_name='上级（父种族 / 宗主势力）',
        on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_factions',
        help_text='种族层级：人族 → 中原人；势力层级：正道联盟 → 天剑门'
    )
    territory = models.CharField('聚居地/领地', max_length=500, blank=True, default='',
        help_text='种族：主要聚居区域；势力：控制领地')
    population = models.PositiveIntegerField('人口/规模', default=0,
        help_text='种族：族群数量；势力：成员规模')
    leader = models.CharField('族长/领袖', max_length=200, blank=True, default='')
    traits = models.TextField(
        '种族天赋/势力特征', blank=True, default='',
        help_text='种族：特殊天赋、寿命、外貌特征；势力：核心传承、招牌功法、军事特色'
    )
    ideology = models.CharField('核心理念/阵营倾向', max_length=500, blank=True, default='')
    logo = models.ImageField('标志/族徽', upload_to='factions/logos/', blank=True, null=True)

    class Meta:
        verbose_name = '种族 / 势力'
        verbose_name_plural = '种族 / 势力'
        ordering = ['category', '-level', 'name']

    def __str__(self):
        cat = '种族' if self.category == 'race' else '势力'
        return f'[{cat}] {self.name} ({self.level}级)'


# ============================================================
# 6. AbilitySystem - 能力体系
# ============================================================
class AbilitySystem(models.Model):
    world = models.ForeignKey(
        'World', verbose_name='所属世界',
        on_delete=models.CASCADE, related_name='%(class)ss',
        null=True, blank=True
    )
    name = models.CharField('体系名称', max_length=200, unique=True)
    description = models.TextField('描述', blank=True, default='')

    class Meta:
        verbose_name = '能力体系'
        verbose_name_plural = '能力体系'
        ordering = ['name']

    def __str__(self):
        return self.name


# ============================================================
# 7. Realm - 境界等级
# ============================================================
class Realm(models.Model):
    REALM_TIER_CHOICES = [
        ('mortal', '凡境'),
        ('spirit', '灵境'),
        ('heaven', '天境'),
        ('sage', '圣境'),
    ]

    world = models.ForeignKey(
        'World', verbose_name='所属世界',
        on_delete=models.CASCADE, related_name='%(class)ss',
        null=True, blank=True
    )
    name = models.CharField('境界名称', max_length=200, unique=True)
    level_order = models.PositiveIntegerField('等级排序', default=1,
        help_text='数字越小等级越低，凡境1-9，灵境1-9，神境1-9')
    tier = models.CharField('大境界', max_length=10, choices=REALM_TIER_CHOICES, default='mortal')
    system = models.ForeignKey(
        AbilitySystem, verbose_name='所属体系',
        on_delete=models.CASCADE, related_name='realms'
    )
    description = models.TextField('描述', blank=True, default='')
    breakthrough_conditions = models.TextField('突破条件', blank=True, default='')
    abilities_unlocked = models.TextField('解锁能力', blank=True, default='')

    class Meta:
        verbose_name = '境界等级'
        verbose_name_plural = '境界等级'
        ordering = ['tier', 'level_order']

    def __str__(self):
        return f'{self.get_tier_display()} - {self.name}'


# ============================================================
# 8. SkillLevel - 技能等级
# ============================================================
class SkillLevel(models.Model):
    world = models.ForeignKey(
        'World', verbose_name='所属世界',
        on_delete=models.CASCADE, related_name='%(class)ss',
        null=True, blank=True
    )
    name = models.CharField('等级名称', max_length=100, unique=True)
    level_order = models.PositiveIntegerField('等级排序', default=1)
    system = models.ForeignKey(
        AbilitySystem, verbose_name='所属体系',
        on_delete=models.CASCADE, related_name='skill_levels'
    )
    description = models.TextField('描述', blank=True, default='')

    class Meta:
        verbose_name = '技能等级'
        verbose_name_plural = '技能等级'
        ordering = ['level_order']

    def __str__(self):
        return self.name


# ============================================================
# 2. Character - 角色
# ============================================================
class Character(models.Model):
    REALM_TIER_CHOICES = [
        ('mortal', '凡境'),
        ('spirit', '灵境'),
        ('heaven', '天境'),
        ('sage', '圣境'),
    ]
    STATUS_CHOICES = [
        ('active', '活跃'),
        ('dead', '死亡'),
        ('missing', '失踪'),
        ('sealed', '封印'),
    ]

    world = models.ForeignKey(
        'World', verbose_name='所属世界',
        on_delete=models.CASCADE, related_name='%(class)ss',
        null=True, blank=True
    )
    name = models.CharField('角色名称', max_length=200, unique=True)
    aliases = models.CharField('别名', max_length=500, blank=True, default='')
    # —— 种族 / 势力双关联 ——
    race = models.ForeignKey(
        Faction,
        verbose_name='种族',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='characters_of_race',
        limit_choices_to={'category': 'race'},
        help_text='生灵的血脉/物种分类（例：人族 → 中原人 / 高等精灵 / 红龙 / 牛头人）'
    )
    faction = models.ForeignKey(
        Faction,
        verbose_name='所属势力',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='characters',
        limit_choices_to={'category': 'force'},
        help_text='角色加入的组织（例：天剑门 / 大炎皇朝 / 冒险者公会）'
    )
    realm_tier = models.CharField('大境界', max_length=10, choices=REALM_TIER_CHOICES, default='mortal')
    realm_order = models.PositiveIntegerField('境界阶数', default=1,
        help_text='1-9阶')
    abilities = models.ManyToManyField('Skill', verbose_name='能力/技能', blank=True, related_name='characters')
    weapons = models.ManyToManyField('Artifact', verbose_name='武器', blank=True, related_name='wielders')
    artifacts = models.ManyToManyField('Artifact', verbose_name='持有宝物', blank=True, related_name='possessors')
    bio = models.TextField('生平', blank=True, default='')
    personality = models.TextField('性格', blank=True, default='')
    appearance_desc = models.TextField('外貌描述', blank=True, default='')
    faction_role = models.CharField(
        '势力身份', max_length=200, blank=True, default='',
        help_text='在所属势力中的职位/角色，如「底层民众」「外门弟子」「长老」「铁砧基地锻造师」'
    )
    power_progression = models.JSONField(
        '实力成长时间线', blank=True, default=list,
        help_text='数组形式：[{stage, era, age, realm_tier, realm_order, realm_name, abilities, artifacts, events, note}]，每一项描述角色某个阶段的境界/能力变化'
    )
    status = models.CharField('状态', max_length=10, choices=STATUS_CHOICES, default='active')

    class Meta:
        verbose_name = '角色'
        verbose_name_plural = '角色'
        ordering = ['-realm_tier', '-realm_order', 'name']

    def __str__(self):
        status_map = dict(self.STATUS_CHOICES)
        return f'{self.name} ({self.get_realm_tier_display()}{self.realm_order}阶 / {status_map.get(self.status, self.status)})'


# ============================================================
# 3. ArtifactCategory - 宝物种类
# ============================================================
class ArtifactCategory(models.Model):
    RARITY_CHOICES = [
        ('SSS', 'SSS 级'),
        ('SS', 'SS 级'),
        ('S', 'S 级'),
        ('A', 'A 级'),
        ('B', 'B 级'),
        ('C', 'C 级'),
    ]

    world = models.ForeignKey(
        'World', verbose_name='所属世界',
        on_delete=models.CASCADE, related_name='%(class)ss',
        null=True, blank=True
    )
    name = models.CharField('种类名称', max_length=200, unique=True)
    description = models.TextField('描述', blank=True, default='')
    rarity_level = models.CharField('稀有度', max_length=3, choices=RARITY_CHOICES, default='C')

    class Meta:
        verbose_name = '宝物种类'
        verbose_name_plural = '宝物种类'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.rarity_level})'


# ============================================================
# 4. Artifact - 宝物
# ============================================================
class Artifact(models.Model):
    RARITY_CHOICES = [
        ('SSS', 'SSS 级'),
        ('SS', 'SS 级'),
        ('S', 'S 级'),
        ('A', 'A 级'),
        ('B', 'B 级'),
        ('C', 'C 级'),
    ]

    world = models.ForeignKey(
        'World', verbose_name='所属世界',
        on_delete=models.CASCADE, related_name='%(class)ss',
        null=True, blank=True
    )
    name = models.CharField('宝物名称', max_length=200, unique=True)
    category = models.ForeignKey(
        ArtifactCategory, verbose_name='种类',
        on_delete=models.CASCADE, related_name='artifacts'
    )
    description = models.TextField('描述', blank=True, default='')
    origin = models.TextField('来历', blank=True, default='')
    effects = models.TextField('效果', blank=True, default='')
    owner = models.ForeignKey(
        Character, verbose_name='持有者',
        on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_artifacts'
    )
    location = models.CharField('位置', max_length=500, blank=True, default='')
    image = models.ImageField('图片', upload_to='artifacts/images/', blank=True, null=True)
    rarity_level = models.CharField('稀有度', max_length=3, choices=RARITY_CHOICES, default='C')

    class Meta:
        verbose_name = '宝物'
        verbose_name_plural = '宝物'
        ordering = ['-rarity_level', 'name']

    def __str__(self):
        return f'{self.name} ({self.rarity_level})'


# ============================================================
# 9. Skill - 技能
# ============================================================
class Skill(models.Model):
    world = models.ForeignKey(
        'World', verbose_name='所属世界',
        on_delete=models.CASCADE, related_name='%(class)ss',
        null=True, blank=True
    )
    name = models.CharField('技能名称', max_length=200, unique=True)
    level = models.ForeignKey(
        SkillLevel, verbose_name='技能等级',
        on_delete=models.CASCADE, related_name='skills'
    )
    description = models.TextField('描述', blank=True, default='')
    effects = models.TextField('效果', blank=True, default='')
    prerequisites = models.TextField('前置条件', blank=True, default='')
    cooldown = models.CharField('冷却时间', max_length=200, blank=True, default='')

    class Meta:
        verbose_name = '技能'
        verbose_name_plural = '技能'
        ordering = ['level__level_order', 'name']

    def __str__(self):
        return f'{self.name} ({self.level.name})'


# ============================================================
# 10. FragmentWorld - 碎片世界
# ============================================================
class FragmentWorld(models.Model):
    world = models.ForeignKey(
        'World', verbose_name='所属世界',
        on_delete=models.CASCADE, related_name='%(class)ss',
        null=True, blank=True
    )
    name = models.CharField('世界名称', max_length=200, unique=True)
    number_id = models.PositiveIntegerField('编号', validators=[], help_text='1-18')
    area = models.CharField('面积', max_length=200, blank=True, default='')
    population = models.PositiveIntegerField('人口', default=0)
    dominant_law = models.CharField('主导法则', max_length=200, blank=True, default='')
    danger_level = models.PositiveIntegerField('危险等级', default=1,
        help_text='1-5，5为最危险')
    max_faction = models.CharField('最强势力', max_length=200, blank=True, default='')
    faction_level = models.CharField('势力等级', max_length=10, blank=True, default='')
    strongest_power = models.CharField('最强力量', max_length=200, blank=True, default='')
    description = models.TextField('描述', blank=True, default='')
    features = models.TextField('特征', blank=True, default='')

    class Meta:
        verbose_name = '碎片世界'
        verbose_name_plural = '碎片世界'
        ordering = ['number_id']

    def __str__(self):
        return f'#{self.number_id} {self.name}'


# ============================================================
# 11. Creature - 异兽
# ============================================================
class Creature(models.Model):
    world = models.ForeignKey(
        'World', verbose_name='所属世界',
        on_delete=models.CASCADE, related_name='%(class)ss',
        null=True, blank=True
    )
    name = models.CharField('异兽名称', max_length=200, unique=True)
    species = models.CharField('物种', max_length=200, blank=True, default='')
    danger_level = models.PositiveIntegerField('危险等级', default=1,
        help_text='1-5，5为最危险')
    habitat = models.ForeignKey(
        FragmentWorld, verbose_name='栖息地',
        on_delete=models.SET_NULL, null=True, blank=True, related_name='creatures'
    )
    abilities = models.TextField('能力', blank=True, default='')
    description = models.TextField('描述', blank=True, default='')
    image = models.ImageField('图片', upload_to='creatures/images/', blank=True, null=True)

    class Meta:
        verbose_name = '异兽'
        verbose_name_plural = '异兽'
        ordering = ['-danger_level', 'name']

    def __str__(self):
        return f'{self.name} (危险等级 {self.danger_level})'


# ============================================================
# 5. HistoricalEvent - 历史事件
# ============================================================
class HistoricalEvent(models.Model):
    ERA_CHOICES = [
        ('era1', '沉眠茧化期'),
        ('era2', '萌芽引导期'),
        ('era3', '深潜纪元'),
        ('era4', '未来伏笔'),
        ('era5', '其他'),
    ]

    world = models.ForeignKey(
        'World', verbose_name='所属世界',
        on_delete=models.CASCADE, related_name='%(class)ss',
        null=True, blank=True
    )
    name = models.CharField('事件名称', max_length=200, unique=True)
    era = models.CharField('时代', max_length=10, choices=ERA_CHOICES, default='era1')
    date_description = models.CharField('时间描述', max_length=500, blank=True, default='')
    description = models.TextField('描述', blank=True, default='')
    involved_factions = models.ManyToManyField(
        Faction, verbose_name='涉及势力', blank=True, related_name='historical_events'
    )
    involved_characters = models.ManyToManyField(
        Character, verbose_name='涉及角色', blank=True, related_name='historical_events'
    )
    consequences = models.TextField('后果', blank=True, default='')

    class Meta:
        verbose_name = '历史事件'
        verbose_name_plural = '历史事件'
        ordering = ['era', 'id']

    def __str__(self):
        return f'{self.name} ({self.get_era_display()})'


# ============================================================
# 12. Relationship - 关系网络
# ============================================================
class Relationship(models.Model):
    RELATION_TYPE_CHOICES = [
        ('ally', '同盟'),
        ('enemy', '敌对'),
        ('master', '师徒'),
        ('family', '亲属'),
        ('lover', '恋侣'),
        ('rival', '竞争者'),
        ('subordinate', '上下级'),
        ('friend', '朋友'),
        ('other', '其他'),
    ]

    from_character = models.ForeignKey(
        Character, verbose_name='角色A',
        on_delete=models.CASCADE, related_name='relationships_from'
    )
    to_character = models.ForeignKey(
        Character, verbose_name='角色B',
        on_delete=models.CASCADE, related_name='relationships_to'
    )
    relation_type = models.CharField('关系类型', max_length=20, choices=RELATION_TYPE_CHOICES, default='other')
    description = models.TextField('描述', blank=True, default='')

    class Meta:
        verbose_name = '关系网络'
        verbose_name_plural = '关系网络'
        unique_together = ('from_character', 'to_character', 'relation_type')
        ordering = ['from_character', 'to_character']

    def __str__(self):
        return f'{self.from_character.name} - {self.get_relation_type_display()} - {self.to_character.name}'


# ============================================================
# 13. LorePage - 设定页面
# ============================================================
class LorePage(models.Model):
    CATEGORY_CHOICES = [
        ('core', '世界观核心'),
        ('power', '力量体系'),
        ('civilization', '文明体系'),
        ('geography', '地理'),
        ('history', '历史'),
        ('creature', '异兽志'),
        ('artifact', '宝物志'),
        ('faction', '势力志'),
        ('character', '人物志'),
        ('other', '其他'),
    ]

    world = models.ForeignKey(
        'World', verbose_name='所属世界',
        on_delete=models.CASCADE, related_name='%(class)ss',
        null=True, blank=True
    )
    title = models.CharField('标题', max_length=200)
    slug = models.SlugField('URL别名', max_length=200, unique=True)
    category = models.CharField('分类', max_length=20, choices=CATEGORY_CHOICES, default='core')
    content = models.TextField('内容', blank=True, default='')
    related_terms = models.ManyToManyField(
        'self', verbose_name='相关设定', blank=True, symmetrical=True
    )
    order = models.PositiveIntegerField('排序', default=0)

    class Meta:
        verbose_name = '设定页面'
        verbose_name_plural = '设定页面'
        ordering = ['category', 'order', 'title']

    def __str__(self):
        return f'{self.title} [{self.get_category_display()}]'


# ============================================================
# 14. OriginLaw - 本源法则
# ============================================================
class OriginLaw(models.Model):
    TIER_CHOICES = [
        ('root', '根源二元层'),
        ('framework', '时空框架层'),
        ('evolution', '演化博弈层'),
        ('narrative', '具象叙事层'),
    ]

    world = models.ForeignKey(
        'World', verbose_name='所属世界',
        on_delete=models.CASCADE, related_name='%(class)ss',
        null=True, blank=True
    )
    name = models.CharField('法则名称', max_length=200, unique=True)
    tier = models.CharField('层级', max_length=20, choices=TIER_CHOICES, default='root',
        help_text='根源二元层(存在/虚无)、时空框架层(时间/空间)、演化博弈层(生命/灵魂/秩序/混沌)、具象叙事层(元素/命运)')
    core_definition = models.TextField('核心定义', blank=True, default='')
    ability_directions = models.TextField('可用术式方向', blank=True, default='')
    side_effect = models.TextField('过度亲和副作用', blank=True, default='')
    description = models.TextField('详细描述', blank=True, default='')
    order = models.PositiveIntegerField('排序', default=0)

    class Meta:
        verbose_name = '本源法则'
        verbose_name_plural = '本源法则'
        ordering = ['order', 'name']

    def __str__(self):
        return f'{self.name} ({self.get_tier_display()})'


# ============================================================
# 15. Anomaly - 异常物
# ============================================================
class Anomaly(models.Model):
    DANGER_CHOICES = [
        ('C', 'C级 (普通)'),
        ('B', 'B级 (危险)'),
        ('A', 'A级 (高危)'),
        ('S', 'S级 (禁忌)'),
        ('X', 'X级 (概念级)'),
    ]
    FUNCTION_CHOICES = [
        ('attack', '攻击型'),
        ('defense', '防御型'),
        ('support', '辅助增益型'),
        ('curse', '诅咒侵蚀型'),
        ('autonomous', '自主意识型'),
    ]

    world = models.ForeignKey(
        'World', verbose_name='所属世界',
        on_delete=models.CASCADE, related_name='%(class)ss',
        null=True, blank=True
    )
    name = models.CharField('异常物名称', max_length=200, unique=True)
    danger_level = models.CharField('危险等级', max_length=1, choices=DANGER_CHOICES, default='C')
    law_attribute = models.CharField('本源法则属性', max_length=200, blank=True, default='')
    function_type = models.CharField('功能类型', max_length=20, choices=FUNCTION_CHOICES, default='attack')
    appearance = models.TextField('外形描述', blank=True, default='')
    ability = models.TextField('能力', blank=True, default='')
    side_effect = models.TextField('副作用', blank=True, default='')
    origin = models.CharField('产出地', max_length=500, blank=True, default='')
    description = models.TextField('详细描述', blank=True, default='')

    class Meta:
        verbose_name = '异常物'
        verbose_name_plural = '异常物'
        ordering = ['-danger_level', 'name']

    def __str__(self):
        return f'{self.name} ({self.danger_level}级)'
