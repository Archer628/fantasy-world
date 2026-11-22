/* =========================================================================
 *  presetMetaChoices.js — 「基础元分类」预置项（全局共用，不区分大世界）
 *  ----------------------------------------------------------------------
 *  本文件提供 8 类「基础设定元分类」的预置模板：
 *
 *    ①  ARTIFACT_RARITY_TEMPLATES     — 宝物稀有度分级（6 套 × 6-8 级）
 *    ②  CREATURE_DANGER_TEMPLATES     — 异兽危险等级（5 套 × 5-7 级）
 *    ③  ANOMALY_DANGER_TEMPLATES      — 异常物/禁忌物危险等级（4 套 × 5-7 级）
 *    ④  ERA_TEMPLATES                 — 历史时代分类（6 套 × 6-12 期）
 *    ⑤  RELATION_TYPE_TEMPLATES       — 角色关系类型（5 套 × 10-16 型）
 *    ⑥  ORIGIN_LAW_TIER_TEMPLATES     — 本源法则层级分类（4 套 × 4-7 层）
 *    ⑦  LORE_CATEGORY_TEMPLATES       — 设定页（LorePage）类目（5 套 × 10-18 类）
 *    ⑧  ABILITY_SYSTEM_TEMPLATES      — 能力体系（修真/魔法/异能/斗气等）（6 套 × 6-14 项）
 *    ⑨  PROFESSION_TEMPLATES          — 职业体系（战士/法师/牧师/盗贼/猎人/炼丹师…）（6 套 × 14-30 职业）
 *    ⑩  CURRENCY_TEMPLATES            — 货币 / 灵石体系（5 套 × 6-14 币种）
 *
 *  使用方式：
 *    1. 在 ChoicesEditor 页面中点击「📜 套用模板」选择对应模板一键写入 choices store
 *    2. 所有模板的元分类 key 与后端模型 choices key 保持一致（可直接保存到 F 键值）
 *  ========================================================================= */

/* =========================================================================
 *  通用工具：生成模板描述块
 *  ========================================================================= */
const makeTpl = (key, name, icon, tags, desc, items, fieldName) => ({
  templateKey: key,
  templateName: name,
  templateIcon: icon,
  templateTags: tags,
  templateDesc: desc,
  [fieldName]: items,
  count: items.length,
})

/* =========================================================================
 *  ①  ARTIFACT_RARITY_TEMPLATES  宝物稀有度分级（后端 RARITY_CHOICES: SSS/SS/S/A/B/C）
 *  ========================================================================= */
const ARTIFACT_RARITY_TEMPLATES = [
  makeTpl('rarity_xianxia', '修真·仙宝品级', '💎', ['修真', '仙侠', '宝物'],
    '修真文经典宝物分级：凡器→灵器→法宝→灵宝→仙器→造化至宝，含 6 级进阶描述与对应产出地。',
    [
      { key: 'C',   label: '凡器 / 凡品',     color: 'gray',    weight: 6, desc: '凡人铁匠打造，无灵气加持，仅锋利耐用。市价：百两白银以下。' },
      { key: 'B',   label: '灵器 / 下品灵器', color: 'emerald', weight: 5, desc: '注入初阶灵气，可斩金断玉。筑基修士主流装备。' },
      { key: 'A',   label: '法宝 / 灵宝',     color: 'cyan',    weight: 4, desc: '金丹/元婴级核心器物，自生灵智雏形，有器魂者称灵宝。' },
      { key: 'S',   label: '仙器 / 半仙之宝', color: 'violet',  weight: 3, desc: '渡劫/大乘级持有，可借天道之力，一方镇宗之宝。' },
      { key: 'SS',  label: '上古仙器 / 神器', color: 'amber',   weight: 2, desc: '洪荒/远古遗存，真仙级炼制，承载远古规则。' },
      { key: 'SSS', label: '造化至宝 / 鸿蒙', color: 'gold',    weight: 1, desc: '开天辟地之器，一念定乾坤（诛仙剑、太极图、盘古幡、混沌钟）。' },
    ], 'rarities'),

  makeTpl('rarity_western_dnd', '西幻·D&D 魔法物品', '🪙', ['西幻', 'D&D', '魔法物品'],
    'D&D 5e 经典魔法物品分级：普通→非稀有→稀有→极稀有→传奇→神器，共 6 级。',
    [
      { key: 'C',   label: 'Common 普通',       color: 'gray',    weight: 6, desc: '无魔法效果或仅微光，一般工匠作品（50 gp 以下）。' },
      { key: 'B',   label: 'Uncommon 非稀有',   color: 'emerald', weight: 5, desc: '附有基础魔法（+1 武器、飞行药水），101-500 gp。' },
      { key: 'A',   label: 'Rare 稀有',         color: 'cyan',    weight: 4, desc: '成熟魔法制品（+2、元素抗性），501-5,000 gp。' },
      { key: 'S',   label: 'Very Rare 极稀有',  color: 'violet',  weight: 3, desc: '强大魔法（+3、传送术），5,001-50,000 gp。' },
      { key: 'SS',  label: 'Legendary 传奇',    color: 'amber',   weight: 2, desc: '传奇物品（命运之锤、红龙法杖），50,001+ gp。' },
      { key: 'SSS', label: 'Artifact 神器',     color: 'gold',    weight: 1, desc: '神祇造物（命运之石板、萨弗拉斯权杖、死亡三圣器）。' },
    ], 'rarities'),

  makeTpl('rarity_warcraft', '魔兽·装备物品等级', '⚒', ['魔兽', 'MMO', '装备'],
    '魔兽世界经典装备分级：普通→优秀→精良→史诗→传说→神器，对应颜色系统。',
    [
      { key: 'C',   label: '普通 灰色 / 优秀 绿色', color: 'gray',    weight: 6, desc: '任务奖励 / 小怪掉落，无特殊效果。' },
      { key: 'B',   label: '精良 蓝色',             color: 'emerald', weight: 5, desc: '副本蓝装、主属性+套装部件雏形。' },
      { key: 'A',   label: '稀有 蓝紫过渡',         color: 'cyan',    weight: 4, desc: '5人本/团队本初阶史诗前装备。' },
      { key: 'S',   label: '史诗 紫色',             color: 'violet',  weight: 3, desc: '主流团队副本核心套装。' },
      { key: 'SS',  label: '传说 橙色',             color: 'amber',   weight: 2, desc: '风剑、橙锤、蛋刀、橙弓等极少数橙武。' },
      { key: 'SSS', label: '神器 Artifact',         color: 'gold',    weight: 1, desc: 'Legion 资料片专属神器（灰烬使者、毁灭之锤、萨拉塔斯）。' },
    ], 'rarities'),

  makeTpl('rarity_isekai', '异世界·转生轻小说', '💠', ['异世界', '转生', '魔道具'],
    '转生轻小说常见分级：消耗品→普通魔道具→A 级秘宝→国家重宝→神造遗物→作弊级。',
    [
      { key: 'C',   label: '消耗品 / 一般道具', color: 'gray',    weight: 6, desc: '回复药、面包、打火石等杂货。' },
      { key: 'B',   label: '魔道具',            color: 'emerald', weight: 5, desc: '附魔剑、魔法包、冒险者徽章。' },
      { key: 'A',   label: 'A 级秘宝',          color: 'cyan',    weight: 4, desc: '永久附魔 + 属性加成，A 级冒险者持有。' },
      { key: 'S',   label: '国家重宝 / 国宝',   color: 'violet',  weight: 3, desc: '圣剑 / 魔道书 / 龙王核，仅王族或 S 级冒险者持有。' },
      { key: 'SS',  label: '神造遗物',          color: 'amber',   weight: 2, desc: '神明遗留，有自我意识（厄里斯女神之泪、贤者之杖）。' },
      { key: 'SSS', label: '作弊级 / 系统级',   color: 'gold',    weight: 1, desc: '转生者独有（智慧之王拉斐尔、暴食者、无限创造 Gamer 系统）。' },
    ], 'rarities'),

  makeTpl('rarity_apocalypse', '末日·废土觉醒', '☢', ['末日', '废土', '异能'],
    '末日异能觉醒流：废弃物资→军用装备→觉醒级→S 级异能核心→法则残片→世界本源。',
    [
      { key: 'C',   label: '废弃物资 / 白装',      color: 'gray',    weight: 6, desc: '废土垃圾、破损铁器、过期罐头。' },
      { key: 'B',   label: '军用装备 / 绿装',      color: 'emerald', weight: 5, desc: '战前军品、防暴甲、冲锋枪。' },
      { key: 'A',   label: '觉醒级 / 蓝装',        color: 'cyan',    weight: 4, desc: 'D-C 级异能者使用，附微弱异能共鸣。' },
      { key: 'S',   label: 'S 级异能核心 / 紫装',  color: 'violet',  weight: 3, desc: 'A 级以上觉醒材料，S 级异能者标配。' },
      { key: 'SS',  label: '法则残片 / 橙装',      color: 'amber',   weight: 2, desc: 'SS 级存在可接触，蕴含空间/时间法则。' },
      { key: 'SSS', label: '世界本源 / 金红装',    color: 'gold',    weight: 1, desc: '深渊 / 虚空 / 创世神级遗留。' },
    ], 'rarities'),

  makeTpl('rarity_interstellar', '星际·文明科技', '🛰', ['星际', '科幻', '科技'],
    '星际文明分级：工业级→军用级→行星级→恒星级→星系级→维度级，共 6 级。',
    [
      { key: 'C',   label: '工业级 / T7 民用',  color: 'gray',    weight: 6, desc: '行星内民用科技。' },
      { key: 'B',   label: '军用级 / T6',       color: 'emerald', weight: 5, desc: '国家级军用装备（电磁炮、外骨骼）。' },
      { key: 'A',   label: '行星级 / T5',       color: 'cyan',    weight: 4, desc: '曲率引擎、纳米装配、反物质弹头。' },
      { key: 'S',   label: '恒星级 / T4',       color: 'violet',  weight: 3, desc: '戴森球、恒星采矿、光粒武器。' },
      { key: 'SS',  label: '星系级 / T3',       color: 'amber',   weight: 2, desc: '虫洞桥、黑洞武器、强相互作用探测器。' },
      { key: 'SSS', label: '维度级 / T2-T0',    color: 'gold',    weight: 1, desc: '降维打击、二向箔、数学规律武器、重启宇宙。' },
    ], 'rarities'),
]

/* =========================================================================
 *  ②  CREATURE_DANGER_TEMPLATES  异兽 / 怪物危险等级（后端 Creature.danger_level: 1-5 PositiveInt）
 *  ========================================================================= */
const CREATURE_DANGER_TEMPLATES = [
  makeTpl('danger_creature_standard', '标准·五级危险度', '🐲', ['通用', '异兽', '怪物'],
    '1-5 级通用异兽/魔物分级：无害 / 低危 / 中危 / 高危 / 灾厄，适用大多数世界。',
    [
      { key: '1', label: '★ 一级·无害',     color: 'emerald', weight: 1, desc: '类似家养动物，普通孩童可击败（小白兔、史莱姆 Lv1）。' },
      { key: '2', label: '★★ 二级·低危',    color: 'cyan',    weight: 2, desc: '一般成年男子持武器可独立应对（野狼、哥布林、跳跳兔）。' },
      { key: '3', label: '★★★ 三级·中危',   color: 'amber',   weight: 3, desc: '需要 3-5 人冒险者小队（兽人战士、石像鬼、毒蝎）。' },
      { key: '4', label: '★★★★ 四级·高危',  color: 'violet',  weight: 4, desc: '城镇级威胁，需军队或高阶修士（上古巨龙、九婴、比蒙）。' },
      { key: '5', label: '★★★★★ 五级·灾厄', color: 'red',     weight: 5, desc: '国家级威胁，需多名最强者联手（毁灭龙王、蚩尤、行星级异兽）。' },
    ], 'dangers'),

  makeTpl('danger_creature_xianxia', '修真·妖兽品阶', '🦑', ['修真', '仙侠', '妖兽'],
    '修真文妖兽进阶：一阶灵兽→二阶妖兽→三阶大妖→四阶妖王→五阶妖圣→六阶妖帝。',
    [
      { key: '1', label: '一阶·灵兽',   color: 'emerald', weight: 1, desc: '略通灵性，炼气 / 筑基修士可猎。' },
      { key: '2', label: '二阶·妖兽',   color: 'cyan',    weight: 2, desc: '可吐人言雏形，金丹级修士方可正面对抗。' },
      { key: '3', label: '三阶·大妖',   color: 'amber',   weight: 3, desc: '完全化形，元婴 / 化神级战力，可裂山断河。' },
      { key: '4', label: '四阶·妖王',   color: 'violet',  weight: 4, desc: '称尊一方，统领百族，炼虚 / 合体级战力。' },
      { key: '5', label: '五阶·妖圣',   color: 'red',     weight: 5, desc: '大乘 / 渡劫级，远古血脉觉醒，接近仙。' },
    ], 'dangers'),

  makeTpl('danger_creature_warcraft', '魔兽·生物威胁度', '🦂', ['魔兽', 'MMO', '怪物'],
    '魔兽世界风格：普通→精英→稀有精英→首领→世界首领，对应 5 级。',
    [
      { key: '1', label: '普通小怪',     color: 'emerald', weight: 1, desc: '野外普通怪，一人可 solo。' },
      { key: '2', label: '精英怪',       color: 'cyan',    weight: 2, desc: '副本普通精英，需要小队伍 2-3 人。' },
      { key: '3', label: '稀有精英',     color: 'amber',   weight: 3, desc: '稀有刷新，掉落较好装备（5 人小队）。' },
      { key: '4', label: '副本首领 Boss',color: 'violet',  weight: 4, desc: '10-25 人团队副本首领。' },
      { key: '5', label: '世界首领',     color: 'red',     weight: 5, desc: '40 人以上团刷（卡扎克、艾索雷葛斯、末日行者）。' },
    ], 'dangers'),

  makeTpl('danger_creature_dnd', 'D&D·挑战等级', '🐙', ['西幻', 'D&D', '怪物'],
    'D&D 5e 怪物挑战等级（CR）压缩至 5 级：低→中→高→极→传奇。',
    [
      { key: '1', label: 'CR 1/8-2',   color: 'emerald', weight: 1, desc: '1-4 级新手冒险者可打（地精、狼、史莱姆）。' },
      { key: '2', label: 'CR 3-6',     color: 'cyan',    weight: 2, desc: '5-8 级小队常见敌人（石像鬼、食人魔、巨蜘蛛）。' },
      { key: '3', label: 'CR 7-12',    color: 'amber',   weight: 3, desc: '9-14 级精英（年轻红龙、石巨人、巫妖学徒）。' },
      { key: '4', label: 'CR 13-19',   color: 'violet',  weight: 4, desc: '15-19 级成熟队（成年红龙、巫妖、泰坦）。' },
      { key: '5', label: 'CR 20-30+',  color: 'red',     weight: 5, desc: '20 级满队对抗（太古红龙、神祗化身、提亚马特）。' },
    ], 'dangers'),

  makeTpl('danger_creature_apocalypse', '末日·变异兽等级', '🦎', ['末日', '废土', '变异兽'],
    '末日变异兽 / 丧尸 / 深渊魔兽分级：F→D→C→B→A→S。',
    [
      { key: '1', label: 'F 级（普通丧尸）',  color: 'emerald', weight: 1, desc: '行动迟缓，普通人可击倒。' },
      { key: '2', label: 'D 级（变异犬）',    color: 'cyan',    weight: 2, desc: 'E 级觉醒者或 3 名士兵可应付。' },
      { key: '3', label: 'C 级（变异巨熊）',  color: 'amber',   weight: 3, desc: 'D 级觉醒者组队 / C 级单挑战胜。' },
      { key: '4', label: 'B 级（暴君/魔将）', color: 'violet',  weight: 4, desc: 'B-A 级觉醒者才能抗衡，一炮炸平街区。' },
      { key: '5', label: 'S 级（领主/深渊）', color: 'red',     weight: 5, desc: '国家级灾难，需 SSS 级觉醒者或核弹级武力。' },
    ], 'dangers'),
]

/* =========================================================================
 *  ③  ANOMALY_DANGER_TEMPLATES  异常物 / 禁忌物危险等级
 *     后端 Anomaly.DANGER_CHOICES: C / B / A / S / X
 *  ========================================================================= */
const ANOMALY_DANGER_TEMPLATES = [
  makeTpl('anomaly_standard', '异常物·SCP 风格', '📓', ['异常物', '禁忌物', 'SCP'],
    '仿 SCP / 超自然档案馆危险分级：Safe→Euclid→Keter→Thaumiel→Apollyon，对应 C/B/A/S/X。',
    [
      { key: 'C', label: 'C 级 · Safe（安全）',       color: 'emerald', weight: 1, desc: '行为规律、可预测，人类理解其原理后可安全操作。' },
      { key: 'B', label: 'B 级 · Euclid（未定）',     color: 'cyan',    weight: 2, desc: '行为不完全可预测，需要严格收容程序。' },
      { key: 'A', label: 'A 级 · Keter（高危）',      color: 'amber',   weight: 3, desc: '持续收容极其困难，需要大量资源且频繁失效。' },
      { key: 'S', label: 'S 级 · 禁忌 / 神造',        color: 'violet',  weight: 4, desc: '非必要不可使用；触碰会导致人格 / 世界级侵蚀。' },
      { key: 'X', label: 'X 级 · 概念级 / Apollyon',  color: 'red',     weight: 5, desc: '无法收容，概念级存在，会引发终末事件 / 世界重启。' },
    ], 'dangers'),

  makeTpl('anomaly_forbidden', '修真·禁忌物/魔道器物', '📿', ['修真', '禁忌物', '魔道'],
    '修真世界中不能轻易碰的东西：凡禁→邪器→魔器→鬼道至邪→先天灭世级。',
    [
      { key: 'C', label: 'C 级·凡禁',     color: 'emerald', weight: 1, desc: '世俗皇家禁用，江湖人不敢碰（御赐毒物、前朝龙气兵）。' },
      { key: 'B', label: 'B 级·邪器',     color: 'cyan',    weight: 2, desc: '沾血过多，产生邪气，易反噬主（人骨珠、百人斩刀）。' },
      { key: 'A', label: 'A 级·魔器',     color: 'amber',   weight: 3, desc: '魔道重宝，需正道联手封印（血煞珠、九幽门禁阵旗）。' },
      { key: 'S', label: 'S 级·至邪',     color: 'violet',  weight: 4, desc: '远古魔道遗存，一现天下血（蚩尤旗、十二都天神煞幡）。' },
      { key: 'X', label: 'X 级·灭世级',   color: 'red',     weight: 5, desc: '非人力可制，需圣人出手（鸿蒙魔气、混沌大劫之物）。' },
    ], 'dangers'),

  makeTpl('anomaly_waifa', '外法 / 克苏鲁禁忌', '🗿', ['克苏鲁', '外神', '旧神'],
    '克苏鲁神话风格：文献→图腾→咒物→外神碎片→阿撒托斯残响。',
    [
      { key: 'C', label: 'C 级·邪典文献',  color: 'emerald', weight: 1, desc: '死灵之书抄本、发黄笔记，阅读后轻微失眠。' },
      { key: 'B', label: 'B 级·异教徒图腾', color: 'cyan',    weight: 2, desc: '深潜者木雕、黄印、银之钥匙仿造品。' },
      { key: 'A', label: 'A 级·咒物实体',  color: 'amber',   weight: 3, desc: '闪耀的偏方三八面体、修格斯组织样本。' },
      { key: 'S', label: 'S 级·外神碎片',  color: 'violet',  weight: 4, desc: '克苏鲁触须化石、莎布尼古拉斯种子、奈亚拉托提普化身。' },
      { key: 'X', label: 'X 级·阿撒托斯',  color: 'red',     weight: 5, desc: '盲痴之神核心残响，接触者文明级认知崩坏。' },
    ], 'dangers'),

  makeTpl('anomaly_houkai', '崩坏·律者核心', '💎', ['崩坏', '律者', '终焉'],
    '崩坏三 / 星穹铁道风格：碎片级→结晶级→核心级→律者核心→终焉核心。',
    [
      { key: 'C', label: 'C 级·崩坏能碎片',  color: 'emerald', weight: 1, desc: '微量崩坏能结晶，可做能源。' },
      { key: 'B', label: 'B 级·死士结晶',    color: 'cyan',    weight: 2, desc: '死士 / 崩坏兽体内结晶，B 级女武神可接触。' },
      { key: 'A', label: 'A 级·拟似律者核', color: 'amber',   weight: 3, desc: '拟似律者核心，A 级女武神级别能量。' },
      { key: 'S', label: 'S 级·律者核心',    color: 'violet',  weight: 4, desc: '真·律者核心（空之律者、雷之律者、冰之律者）。' },
      { key: 'X', label: 'X 级·终焉 / 星神', color: 'red',     weight: 5, desc: '终焉之律者核心 / 星神神核 / 反物质宇宙级。' },
    ], 'dangers'),
]

/* =========================================================================
 *  ④  ERA_TEMPLATES  历史时代分类（后端 HistoricalEvent.ERA_CHOICES: era1-era5）
 *  ========================================================================= */
const ERA_TEMPLATES = [
  makeTpl('era_fantasy_growth', '茧化·萌芽·深潜·爆发·终局', '📜', ['原创', '玄幻', '5 期'],
    '项目原始 5 期设定：沉眠茧化 → 萌芽引导 → 深潜纪元 → 高潮爆发 → 未来伏笔，对应 era1-era5。',
    [
      { key: 'era1', label: '茧化期（沉眠·孕育）', color: 'violet', weight: 1, desc: '世界 / 角色在故事开始前的沉眠 / 孕育 / 转世之前，一切尚未开始。' },
      { key: 'era2', label: '萌芽期（引导·开篇）', color: 'emerald', weight: 2, desc: '故事正式开篇，主角登场，世界观基础事件建立。' },
      { key: 'era3', label: '深潜纪元（展开·中盘）', color: 'cyan',   weight: 3, desc: '主线全面展开，冲突升级，势力大规模登场。' },
      { key: 'era4', label: '爆发期（高潮·终战）', color: 'red',     weight: 4, desc: '所有伏笔引爆，世界格局大洗牌，终局之战。' },
      { key: 'era5', label: '后日谈 / 未来伏笔',  color: 'amber',   weight: 5, desc: '结局后、序章外的未来碎片 / 续作伏笔 / 下一世代。' },
    ], 'eras'),

  makeTpl('era_xianxia', '修真·开天辟地 12 纪元', '🌌', ['修真', '洪荒', '纪元'],
    '洪荒 / 修真文 12 纪元递进：混沌 → 开天 → 龙汉初 → 巫妖 → 封神 → 西游 → 末法。',
    [
      { key: 'era1', label: '混沌纪元（开天前）',    color: 'violet', weight: 1, desc: '盘古未开，混沌三千魔神横行。' },
      { key: 'era2', label: '开天纪元（洪荒初成）',  color: 'gold',   weight: 2, desc: '盘古开天，洪荒大地成形，先天神灵诞生。' },
      { key: 'era3', label: '龙汉纪元（三族争霸）',  color: 'red',    weight: 3, desc: '龙凤麒麟三族大战，洪荒第一次大劫。' },
      { key: 'era4', label: '巫妖纪元（十二祖巫）',  color: 'amber',  weight: 4, desc: '巫妖两族分治天地，后羿射日、夸父逐日。' },
      { key: 'era5', label: '封神纪元（商周易代）',  color: 'cyan',   weight: 5, desc: '武王伐纣，三教共立封神榜，众神归位。' },
    ], 'eras'),

  makeTpl('era_warcraft', '魔兽·艾泽拉斯年表', '🐉', ['魔兽', 'MMO', '编年史'],
    '魔兽世界编年史简化 6 期：上古 → 泰坦 → 巨龙 → 巨魔帝国 → 人类王国 → 现代。',
    [
      { key: 'era1', label: '上古黑暗（虚空·光）',   color: 'violet', weight: 1, desc: '虚空与光的对立，泰坦初醒。' },
      { key: 'era2', label: '泰坦塑造艾泽拉斯',     color: 'cyan',   weight: 2, desc: '万神殿塑造世界，古神被封印。' },
      { key: 'era3', label: '巨龙时代',            color: 'amber',  weight: 3, desc: '五色守护巨龙掌权，暗夜精灵崛起。' },
      { key: 'era4', label: '巨魔 / 精灵双帝国',    color: 'emerald',weight: 4, desc: '赞达拉巨魔帝国与卡多雷暗夜帝国。' },
      { key: 'era5', label: '人类七国 / 现代',      color: 'gold',   weight: 5, desc: '阿拉索分裂七国、魔兽争霸 / 世界主线。' },
    ], 'eras'),

  makeTpl('era_isekai', '异世界·转生者编年', '🌀', ['异世界', '转生', '年表'],
    '异世界轻小说经典 6 期：创世 → 众神时代 → 古代文明 → 魔王纪元 → 勇者时代 → 转生者登场。',
    [
      { key: 'era1', label: '创世·神代',           color: 'violet', weight: 1, desc: '众神创造世界，原初七大天使 / 魔王原型诞生。' },
      { key: 'era2', label: '古代精灵文明',        color: 'emerald',weight: 2, desc: '精灵建造世界树魔法文明，现代之前的黄金期。' },
      { key: 'era3', label: '魔族入侵纪元',        color: 'red',    weight: 3, desc: '魔族第一次大规模入侵，勇者体系建立。' },
      { key: 'era4', label: '王国 / 公会时代',     color: 'cyan',   weight: 4, desc: '人族建立王国、冒险者公会，现代主线前期。' },
      { key: 'era5', label: '转生者 / 穿越者时代', color: 'gold',   weight: 5, desc: '作弊级转生者登场，世界格局改写（故事主线）。' },
    ], 'eras'),

  makeTpl('era_apocalypse', '末日·废土纪年', '☢', ['末日', '废土', '纪年'],
    '末日废土 6 期：黄金战前 → 大灾变 → 废土混乱 → 势力割据 → 曙光重建 → 星际。',
    [
      { key: 'era1', label: '战前黄金年代',       color: 'emerald', weight: 1, desc: '现代文明 / 科技高峰，末世尚未到来。' },
      { key: 'era2', label: '大灾变 / 降临日',    color: 'red',     weight: 2, desc: '陨石 / 病毒 / 灵气复苏 / 异界之门打开。' },
      { key: 'era3', label: '黑暗纪元·废土混乱',  color: 'violet',  weight: 3, desc: '法律失效，幸存者挣扎，异能者初现。' },
      { key: 'era4', label: '势力割据·新纪元',    color: 'amber',   weight: 4, desc: '幸存者基地、军部、觉醒者公会建立。' },
      { key: 'era5', label: '曙光重建 / 反攻',    color: 'gold',    weight: 5, desc: '文明重建，反攻深渊 / 虫群 / 域外天魔。' },
    ], 'eras'),

  makeTpl('era_interstellar', '星际·文明阶梯', '🚀', ['星际', '科幻', '文明'],
    '刘慈欣三体式 6 期：行星文明 → 恒星 → 星系 → 星团 → 宇宙 → 维度重启。',
    [
      { key: 'era1', label: 'T7-T6 行星文明',    color: 'emerald', weight: 1, desc: '文明仍在母星（信息时代 / 原子能）。' },
      { key: 'era2', label: 'T5 恒星文明',       color: 'cyan',    weight: 2, desc: '曲率引擎、戴森云、殖民内太阳系。' },
      { key: 'era3', label: 'T4 星系文明',       color: 'amber',   weight: 3, desc: '光帆 / 冬眠舰队、殖民整个星系。' },
      { key: 'era4', label: 'T3 宇宙文明',       color: 'violet',  weight: 4, desc: '虫洞桥、跨河系旅行，接触黑暗森林。' },
      { key: 'era5', label: 'T2-T0 维度文明',    color: 'red',     weight: 5, desc: '掌握数学规律 / 降维 / 重启宇宙。' },
    ], 'eras'),
]

/* =========================================================================
 *  ⑤  RELATION_TYPE_TEMPLATES  角色关系类型
 *     后端 Relationship.RELATION_TYPE_CHOICES: ally/enemy/master/family/lover/rival/subordinate/friend/other
 *  ========================================================================= */
const RELATION_TYPE_TEMPLATES = [
  makeTpl('relation_universal', '通用·全关系谱', '🤝', ['通用', '角色关系'],
    '涵盖所有类型：亲友、敌对、爱憎、师徒、上下级、暧昧、宿命、前世…共 12 型。',
    [
      { key: 'family',      label: '👨‍👩‍👧 亲属（血缘/养亲）', color: 'amber',   weight: 1, desc: '直系血亲、旁系、养父母、兄弟姐妹。' },
      { key: 'lover',       label: '💕 恋人 / 夫妻',       color: 'red',     weight: 2, desc: '正式恋人、婚约者、已婚夫妻、前世缘。' },
      { key: 'friend',      label: '🤝 挚友 / 战友',       color: 'emerald', weight: 3, desc: '生死之交、战友、同学、发小。' },
      { key: 'master',      label: '📚 师徒 / 主仆',       color: 'violet',  weight: 4, desc: '师徒、义父义子、主从契约、仆从关系。' },
      { key: 'ally',        label: '🛡 同盟 / 合作',       color: 'cyan',    weight: 5, desc: '临时 / 长期同盟、契约合作、同事。' },
      { key: 'subordinate', label: '⚔ 上下级 / 君臣',      color: 'gold',    weight: 6, desc: '宗门上下、朝廷君臣、军队指挥链。' },
      { key: 'rival',       label: '🏹 宿命对手 / 竞争者', color: 'amber',   weight: 7, desc: '惺惺相惜的宿敌、同期竞争对手。' },
      { key: 'enemy',       label: '💀 仇敌 / 敌对',       color: 'red',     weight: 8, desc: '血海深仇、势力敌对、杀亲之仇。' },
      { key: 'other',       label: '❓ 其他 / 未定义',     color: 'gray',    weight: 99, desc: '暂时无法归类的关系。' },
    ], 'relations'),

  makeTpl('relation_xianxia', '修真·仙门人际关系', '🎋', ['修真', '仙侠', '门派'],
    '修真世界特色：道侣、同门、义兄弟、丹道道友、因果、宿慧… 14 型。',
    [
      { key: 'family',      label: '👨‍👩‍👧 凡俗血亲',         color: 'amber',   weight: 1, desc: '未修行前的家族血缘。' },
      { key: 'lover',       label: '💍 道侣 / 双修伴侣',    color: 'red',     weight: 2, desc: '修真界的夫妻 / 道侣 / 双修道伴。' },
      { key: 'friend',      label: '🗡 义结金兰 / 道友',    color: 'emerald', weight: 3, desc: '八拜之交、丹道/剑道道友。' },
      { key: 'master',      label: '📜 师承（传功/衣钵）', color: 'violet',  weight: 4, desc: '师父-弟子、祖师爷-徒孙、隔代传功。' },
      { key: 'subordinate', label: '🏯 宗门上下（师兄弟）', color: 'gold',    weight: 5, desc: '掌门、长老、内门、外门、弟子辈分。' },
      { key: 'ally',        label: '🛡 宗门同盟',          color: 'cyan',    weight: 6, desc: '正道同盟、两个宗门的互助条约。' },
      { key: 'rival',       label: '🏹 论剑宿敌',          color: 'amber',   weight: 7, desc: '百年来的剑道 / 丹道宿敌。' },
      { key: 'enemy',       label: '💀 血仇 / 正邪',       color: 'red',     weight: 8, desc: '灭门之仇、道统之争、正邪殊途。' },
      { key: 'other',       label: '☯ 因果 / 宿慧 / 转世', color: 'gray',    weight: 99, desc: '前世恩人、宿世因果、神识印记。' },
    ], 'relations'),

  makeTpl('relation_western', '西幻·王国贵族关系', '👑', ['西幻', '贵族', '王国'],
    '西幻王国特色：封君封臣、骑士侍从、宫廷情人、私生子、结拜兄弟、教会弟兄。',
    [
      { key: 'family',      label: '👑 王室 / 贵族血缘',   color: 'amber',   weight: 1, desc: '王族、公爵、伯爵等世袭家族。' },
      { key: 'lover',       label: '💒 婚约 / 宫廷恋人',   color: 'red',     weight: 2, desc: '政治婚约、王室婚姻、贵族情人。' },
      { key: 'friend',      label: '⚔ 骑士结拜 / 冒险队', color: 'emerald', weight: 3, desc: '战友、冒险小队、圣骑士兄弟连。' },
      { key: 'master',      label: '🛡 骑士·侍从 / 导师',  color: 'violet',  weight: 4, desc: '骑士-侍从、法师-学徒、剑士导师。' },
      { key: 'subordinate', label: '🏰 封君·封臣 / 君臣',  color: 'gold',    weight: 5, desc: '国王-公爵-伯爵的封建金字塔。' },
      { key: 'ally',        label: '🕊 王国同盟 / 联姻',   color: 'cyan',    weight: 6, desc: '两国同盟、家族联姻、军事条约。' },
      { key: 'rival',       label: '🎭 宫廷政敌',          color: 'amber',   weight: 7, desc: '继承权之争、王室派系政敌。' },
      { key: 'enemy',       label: '💀 国仇 / 异端审判',   color: 'red',     weight: 8, desc: '王国之间的战争、教会与异端。' },
      { key: 'other',       label: '⛪ 教会弟兄 / 信徒',   color: 'gray',    weight: 99, desc: '同信一神的弟兄姊妹、教友。' },
    ], 'relations'),

  makeTpl('relation_crime', '谍战·权谋·组织关系', '🕶', ['谍战', '权谋', '黑道'],
    '谍战/权谋文专用：卧底、线人、暗棋、内鬼、白手套、替罪羊、政敌、盟友。',
    [
      { key: 'family',      label: '🏛 政治家族 / 门阀',   color: 'amber',   weight: 1, desc: '世袭门阀、政治联姻家族。' },
      { key: 'lover',       label: '🌹 政治情人 / 枕边谍', color: 'red',     weight: 2, desc: '间谍伪装的情人 / 政治联姻。' },
      { key: 'friend',      label: '🤝 私人信交 / 故旧',   color: 'emerald', weight: 3, desc: '私下密友、同窗、旧识、老同事。' },
      { key: 'master',      label: '🎩 幕后老板 / 导师',   color: 'violet',  weight: 4, desc: '组织头目、情报导师、暗线操控者。' },
      { key: 'subordinate', label: '🕶 上下级 / 白手套',   color: 'gold',    weight: 5, desc: '直属下属、白手套、代持人。' },
      { key: 'ally',        label: '🤝 利益同盟 / 暗盟',   color: 'cyan',    weight: 6, desc: '台面上或台面下的利益盟友。' },
      { key: 'rival',       label: '⚔ 政敌 / 竞合',        color: 'amber',   weight: 7, desc: '官场上的政敌、商业竞争对手。' },
      { key: 'enemy',       label: '🔪 死敌 / 灭门仇人',   color: 'red',     weight: 8, desc: '政治清算、血仇、暗杀目标。' },
      { key: 'other',       label: '🗝 卧底 / 线人 / 暗棋', color: 'gray',    weight: 99, desc: '卧底、线人、双面间谍、内鬼、暗子。' },
    ], 'relations'),

  makeTpl('relation_apocalypse', '末日·废土关系', '💣', ['末日', '废土', '幸存者'],
    '末日废土关系：幸存者小队、共享物资、救命之恩、背叛、基地指挥官、拾荒同伴。',
    [
      { key: 'family',      label: '👨‍👩‍👧 末世幸存家人',    color: 'amber',   weight: 1, desc: '灾难后仍聚在一起的家人。' },
      { key: 'lover',       label: '💞 末世相互扶持的情侣', color: 'red',     weight: 2, desc: '废土中相依为命的恋人。' },
      { key: 'friend',      label: '🎒 拾荒 / 战友',       color: 'emerald', weight: 3, desc: '一起拾荒、一起作战的伙伴。' },
      { key: 'master',      label: '🔬 异能导师 / 师父',   color: 'violet',  weight: 4, desc: '异能觉醒引路人、战斗师父。' },
      { key: 'subordinate', label: '🏕 基地指挥官 / 队长', color: 'gold',    weight: 5, desc: '幸存者基地领袖、小队队长。' },
      { key: 'ally',        label: '📦 资源共享 / 基地同盟',color: 'cyan',   weight: 6, desc: '互相以物易物、共同御敌。' },
      { key: 'rival',       label: '🔫 资源争夺 / 敌对团', color: 'amber',   weight: 7, desc: '抢地盘、抢资源的幸存者敌对团。' },
      { key: 'enemy',       label: '💀 背叛者 / 仇人',     color: 'red',     weight: 8, desc: '背叛队友、抢粮杀人的死仇。' },
      { key: 'other',       label: '🙏 救命之恩 / 欠人情', color: 'gray',    weight: 99, desc: '一饭之恩、救命之恩、人情债。' },
    ], 'relations'),
]

/* =========================================================================
 *  ⑥  ORIGIN_LAW_TIER_TEMPLATES  本源法则层级
 *     后端 OriginLaw.TIER_CHOICES: root / framework / evolution / narrative
 *  ========================================================================= */
const ORIGIN_LAW_TIER_TEMPLATES = [
  makeTpl('originlaw_standard', '本源法则·四层阶梯', '🔮', ['原创', '玄幻', '法则'],
    '项目原始 4 层：根源二元 → 时空框架 → 演化博弈 → 具象叙事。',
    [
      { key: 'root',        label: '根源二元层',   color: 'violet', weight: 1, desc: '阴阳、有无、善恶、光暗……世界存在的最根本二律背反。' },
      { key: 'framework',   label: '时空框架层',   color: 'cyan',   weight: 2, desc: '空间、时间、物质、能量、因果、命运……世界运作的骨架。' },
      { key: 'evolution',   label: '演化博弈层',   color: 'amber',  weight: 3, desc: '生命、死亡、进化、战争、和平、秩序、混乱……动态博弈。' },
      { key: 'narrative',   label: '具象叙事层',   color: 'gold',   weight: 4, desc: '火焰、寒冰、雷霆、剑气、炼丹、阵法……主角可直接施展的「术」。' },
    ], 'tiers'),

  makeTpl('originlaw_xianxia', '修真·三千大道阶梯', '☯', ['修真', '仙侠', '大道'],
    '修真三千大道分级：无上大道 → 至高法则 → 高级法则 → 中级 → 基础术式。',
    [
      { key: 'root',        label: '无上大道（盘古/鸿钧）', color: 'violet', weight: 1, desc: '混沌、大道、鸿蒙、无极、太极。' },
      { key: 'framework',   label: '至高法则',             color: 'cyan',   weight: 2, desc: '时间、空间、因果、命运、轮回、造化。' },
      { key: 'evolution',   label: '高级法则',             color: 'amber',  weight: 3, desc: '生死、毁灭、创造、战争、秩序、混乱、气运。' },
      { key: 'narrative',   label: '具象元素 / 术法',      color: 'gold',   weight: 4, desc: '五行、风雷、阴阳、光暗、剑气、丹道、阵法。' },
    ], 'tiers'),

  makeTpl('originlaw_magic', '西幻·魔网法则', '🪄', ['西幻', '魔法', '魔网'],
    'D&D / 龙枪魔网层级：神力之源 → 魔网骨架 → 魔法学派 → 具体法术。',
    [
      { key: 'root',        label: '神力源（AO / 诸神）', color: 'violet', weight: 1, desc: '神上神 AO、原初魔法、符文之秘。' },
      { key: 'framework',   label: '魔网层（Weave）',    color: 'cyan',   weight: 2, desc: '魔法女神编织的魔网、影魔网、符文骨架。' },
      { key: 'evolution',   label: '八大学派',           color: 'amber',  weight: 3, desc: '防护、咒法、预言、附魔、塑能、幻术、死灵、变化。' },
      { key: 'narrative',   label: '具体法术 0-9 环',    color: 'gold',   weight: 4, desc: '火球术、传送术、时间停止、许愿术。' },
    ], 'tiers'),

  makeTpl('originlaw_interstellar', '星际·宇宙法则', '🌌', ['星际', '科幻', '宇宙'],
    '星际科幻 4 层：数学规律 → 四大基本力 → 物理化学 → 工程应用。',
    [
      { key: 'root',        label: '数学规律层',   color: 'violet', weight: 1, desc: '修改圆周率、二向箔、因果律武器。' },
      { key: 'framework',   label: '四大力框架',  color: 'cyan',   weight: 2, desc: '强相互作用、电磁力、弱力、引力。' },
      { key: 'evolution',   label: '物理化学层',   color: 'amber',  weight: 3, desc: '相对论、量子力学、元素周期、熵增。' },
      { key: 'narrative',   label: '工程应用层',   color: 'gold',   weight: 4, desc: '聚变、反物质、纳米、AI、曲率引擎。' },
    ], 'tiers'),
]

/* =========================================================================
 *  ⑦  LORE_CATEGORY_TEMPLATES  设定页分类
 *     后端 LorePage.CATEGORY_CHOICES: core/power/civilization/geography/history/creature/artifact/faction/character/other
 *  ========================================================================= */
const LORE_CATEGORY_TEMPLATES = [
  makeTpl('lore_universal', '通用·全类目 10 项', '📚', ['通用', '设定页', '分类'],
    '项目原始 10 类 + 扩充 2 项（资源·政治）：总计 12 类。',
    [
      { key: 'core',         label: '🌌 世界观核心',  color: 'violet', weight: 1, desc: '创世神话、世界结构、大背景、核心基调。' },
      { key: 'geography',    label: '🗺 地理·疆域',    color: 'emerald',weight: 2, desc: '大陆、海洋、山脉、城池、秘境、位面。' },
      { key: 'history',      label: '📜 历史·年表',    color: 'amber',  weight: 3, desc: '历代大事纪、战争、朝代更迭。' },
      { key: 'civilization', label: '🏛 文明·政治',    color: 'gold',   weight: 4, desc: '种族文明、政治制度、经济贸易、宗教。' },
      { key: 'power',        label: '⚡ 力量体系',    color: 'cyan',   weight: 5, desc: '修炼境界、魔法体系、异能、斗气、血脉。' },
      { key: 'faction',      label: '🏰 势力·种族志', color: 'violet', weight: 6, desc: '宗门、王国、商会、种族分布。' },
      { key: 'character',    label: '👥 人物志',      color: 'red',    weight: 7, desc: '核心人物的深度介绍、性格、事迹。' },
      { key: 'artifact',     label: '💎 宝物志',      color: 'amber',  weight: 8, desc: '神器、法宝、圣器、神兵、特殊物品。' },
      { key: 'creature',     label: '🐲 异兽志',      color: 'emerald',weight: 9, desc: '妖兽、灵兽、魔物、幻想生物。' },
      { key: 'other',        label: '❓ 其他 / 杂录', color: 'gray',   weight: 99, desc: '食谱、诗词、风俗、节日等其他设定。' },
    ], 'categories'),

  makeTpl('lore_xianxia', '修真·洪荒设定类目', '🏔', ['修真', '洪荒', '设定'],
    '修真 / 洪荒文专属：三界结构、封神榜、天地大劫、丹器阵符、龙脉地脉… 14 类。',
    [
      { key: 'core',         label: '🌌 三界·三十六天', color: 'violet', weight: 1, desc: '凡界 / 仙界 / 佛界 / 三十六天 / 九幽。' },
      { key: 'geography',    label: '🗺 四大部洲 / 仙山', color: 'emerald',weight: 2, desc: '东胜神洲 / 南赡部洲 / 西牛贺洲 / 北俱芦洲 / 昆仑 / 蓬莱。' },
      { key: 'history',      label: '📜 天地大劫年表',   color: 'amber',  weight: 3, desc: '开天 / 龙汉 / 巫妖 / 封神 / 西游 / 末法。' },
      { key: 'civilization', label: '🏛 皇朝·宗门制度',  color: 'gold',   weight: 4, desc: '王朝制度、宗门等级、科举 / 仙考。' },
      { key: 'power',        label: '⚡ 境界·功法·血脉', color: 'cyan',   weight: 5, desc: '修真境界、神通功法、血脉、根骨。' },
      { key: 'faction',      label: '🏰 宗门·道统',     color: 'violet', weight: 6, desc: '正道七宗、魔道六派、三教九流。' },
      { key: 'character',    label: '👥 仙佛·人物志',   color: 'red',    weight: 7, desc: '古之仙人、菩萨、大帝、圣贤。' },
      { key: 'artifact',     label: '💎 法宝·先天灵宝', color: 'amber',  weight: 8, desc: '诛仙剑、太极图、杏黄旗、葫芦娃。' },
      { key: 'creature',     label: '🐲 妖族·山海经',   color: 'emerald',weight: 9, desc: '龙凤麒麟、三族、山海经异兽。' },
      { key: 'other',        label: '🧪 丹·器·阵·符',   color: 'gray',   weight: 99, desc: '炼丹、炼器、阵法、符箓、灵草百科。' },
    ], 'categories'),

  makeTpl('lore_isekai', '异世界·转生设定类目', '🗾', ['异世界', '轻小说', '转生'],
    '异世界轻小说 / 转生史莱姆、骨王、无职转生风格 14 类。',
    [
      { key: 'core',         label: '🌌 世界树·神创',    color: 'violet', weight: 1, desc: '创世神、世界树、魔族 / 勇者神话。' },
      { key: 'geography',    label: '🗺 大陆 / 迷宫',     color: 'emerald',weight: 2, desc: '三大大陆、魔族领域、龙之迷宫、地下城。' },
      { key: 'history',      label: '📜 勇者·魔王年表',  color: 'amber',  weight: 3, desc: '历代魔王、勇者传承、魔族入侵纪元。' },
      { key: 'civilization', label: '🏛 王国·公会制度',  color: 'gold',   weight: 4, desc: '封建王国、冒险者公会、奴隶制度、货币。' },
      { key: 'power',        label: '⚡ 魔法·技能·段位', color: 'cyan',   weight: 5, desc: '六属性魔法、技能板、职业段位、固有技能。' },
      { key: 'faction',      label: '🏰 王国·教国·魔族', color: 'violet', weight: 6, desc: '四大王国、神圣教国、魔国联邦、龙族议会。' },
      { key: 'character',    label: '👥 勇者·转生者',    color: 'red',    weight: 7, desc: '历代勇者、转生者、作弊主角。' },
      { key: 'artifact',     label: '💎 圣剑·魔道具',    color: 'amber',  weight: 8, desc: '勇者圣剑、魔国国宝、神造遗物。' },
      { key: 'creature',     label: '🐲 魔物·恶魔·龙',  color: 'emerald',weight: 9, desc: '哥布林、史莱姆、恶魔族、古龙种。' },
      { key: 'other',        label: '🍞 食物·节日·货币', color: 'gray',   weight: 99, desc: '异世界料理、节日庆典、金币铜币、魔石能源。' },
    ], 'categories'),

  makeTpl('lore_warcraft', '魔兽·艾泽拉斯百科', '🗺', ['魔兽', 'MMO', '设定'],
    '魔兽世界百科式分类：编年史 / 地理 / 阵营 / 副本 / 传说人物 / 神器… 12 类。',
    [
      { key: 'core',         label: '🌌 编年史·泰坦·虚空',color: 'violet', weight: 1, desc: '泰坦与古神、光与暗、魔兽世界诞生。' },
      { key: 'geography',    label: '🗺 东部王国·卡利姆多',color: 'emerald',weight: 2, desc: '东部王国 / 卡利姆多 / 诺森德 / 潘达利亚 / 德拉诺。' },
      { key: 'history',      label: '📜 资料片时间线',    color: 'amber',  weight: 3, desc: '魔兽 1-3 → TBC/WotLK/Cata/MoP/WoD/Legion/BfA/SL。' },
      { key: 'civilization', label: '🏛 联盟·部落文明',  color: 'gold',   weight: 4, desc: '联盟/部落的政治结构、种族文化、信仰。' },
      { key: 'power',        label: '⚡ 职业·专精·神器',  color: 'cyan',   weight: 5, desc: '战士/法师/牧师/猎人 12 职业 + 神器。' },
      { key: 'faction',      label: '🏰 阵营·主城·中立', color: 'violet', weight: 6, desc: '联盟主城/部落主城/中立组织（塞纳里奥/银色北伐）。' },
      { key: 'character',    label: '👥 传说人物',        color: 'red',    weight: 7, desc: '阿尔萨斯、伊利丹、萨尔、安度因、吉安娜。' },
      { key: 'artifact',     label: '💎 神器·传说装备',  color: 'amber',  weight: 8, desc: '灰烬使者、霜之哀伤、埃辛诺斯战刃。' },
      { key: 'creature',     label: '🐲 龙族·上古之神',  color: 'emerald',weight: 9, desc: '五色龙 / 元素领主 / 上古之神 / 燃烧军团。' },
      { key: 'other',        label: '🎭 副本·节日·美食', color: 'gray',   weight: 99, desc: '经典副本 / 美酒节 / 火焰节 / 魔兽美食。' },
    ], 'categories'),

  makeTpl('lore_apocalypse', '末日·废土设定类目', '☣', ['末日', '废土', '觉醒'],
    '末日废土 / 灵气复苏 / 深渊入侵 设定分类 13 项。',
    [
      { key: 'core',         label: '🌌 末日起因',        color: 'violet', weight: 1, desc: '陨石 / 病毒 / 灵气复苏 / 深渊降临 / AI 叛变。' },
      { key: 'geography',    label: '🗺 废墟 / 安全区',    color: 'emerald',weight: 2, desc: '末日城市废墟、地下掩体、安全区、禁区。' },
      { key: 'history',      label: '📜 灾变日纪年',       color: 'amber',  weight: 3, desc: '灾变前 / 灾变日 / 黑暗十年 / 新纪元。' },
      { key: 'civilization', label: '🏛 基地 / 军部制度',  color: 'gold',   weight: 4, desc: '幸存者基地、军部、黑市、觉醒者公会。' },
      { key: 'power',        label: '⚡ 异能 / 觉醒体系',  color: 'cyan',   weight: 5, desc: '觉醒分级、异能属性、基因锁、基因进化。' },
      { key: 'faction',      label: '🏰 势力·军阀·公会',   color: 'violet', weight: 6, desc: '军部、家族财阀、觉醒者公会、邪教。' },
      { key: 'character',    label: '👥 觉醒者 / 重生者',  color: 'red',    weight: 7, desc: 'S 级觉醒者、重生者、深渊宿主。' },
      { key: 'artifact',     label: '💎 异能结晶 / 遗物',  color: 'amber',  weight: 8, desc: '崩坏能结晶、深渊遗物、神之序列药剂。' },
      { key: 'creature',     label: '🐲 变异兽 / 丧尸',   color: 'emerald',weight: 9, desc: '变异兽 / 丧尸 / 深渊魔兽 / 虫群。' },
      { key: 'other',        label: '🥫 物资·货币·装备',   color: 'gray',   weight: 99, desc: '食物等级 / 贡献点 / 战前科技装备。' },
    ], 'categories'),
]

/* =========================================================================
 *  ⑧  ABILITY_SYSTEM_TEMPLATES  能力体系（对应后端 AbilitySystem 模型，可一键批量创建）
 *  ========================================================================= */
const ABILITY_SYSTEM_TEMPLATES = [
  makeTpl('ability_xianxia', '修真·仙术体系 14 类', '☯', ['修真', '仙侠', '能力'],
    '正统修真能力体系：剑道、丹道、阵道、符箓、炼器、御兽、星象、咒术、音杀… 14 项。',
    [
      { key: 'sword',    label: '⚔ 剑道',           color: 'cyan',    weight: 1,  desc: '以剑入道：御剑、剑意、剑域、剑心通明。' },
      { key: 'dan',      label: '🧪 丹道',           color: 'emerald', weight: 2,  desc: '炼丹：九转金丹、渡劫丹、回春丹、悟道茶。' },
      { key: 'zhen',     label: '🕸 阵道',           color: 'violet',  weight: 3,  desc: '阵法：护山大阵、诛仙剑阵、传送阵、迷踪阵。' },
      { key: 'fu',       label: '📜 符箓',           color: 'amber',   weight: 4,  desc: '画符：镇尸符、火符、雷符、聚灵符、替身符。' },
      { key: 'qi',       label: '🔨 器道（炼器）',   color: 'gold',    weight: 5,  desc: '法器炼制：飞剑、法袍、法宝、先天灵宝。' },
      { key: 'beast',    label: '🐲 御兽·驯兽',      color: 'emerald', weight: 6,  desc: '收服妖兽、灵兽契约、万兽幡。' },
      { key: 'star',     label: '⭐ 星象·摘星术',    color: 'violet',  weight: 7,  desc: '夜观星象、借星力、摘星手、七星剑阵。' },
      { key: 'curse',    label: '☠ 咒术·蛊道',       color: 'red',     weight: 8,  desc: '诅咒、降头、蛊虫、血祭（多为魔道）。' },
      { key: 'sound',    label: '🎵 音杀·琴道',       color: 'cyan',    weight: 9,  desc: '琴心三叠、天魔琴、狮子吼、佛门梵音。' },
      { key: 'body',     label: '💪 体修·炼体',      color: 'amber',   weight: 10, desc: '九转玄功、八九玄功、金刚不坏体。' },
      { key: 'spirit',   label: '👁 神识·读心·卜筮', color: 'violet',  weight: 11, desc: '神念扫、读心、卜卦、天机推演。' },
      { key: 'escape',   label: '🌀 遁法·神通',       color: 'cyan',    weight: 12, desc: '五行大遁、血遁、金光遁、缩地成寸。' },
      { key: 'divine',   label: '☄ 神通·古法',        color: 'gold',    weight: 13, desc: '七十二变、法天象地、三头六臂、袖里乾坤。' },
      { key: 'budda',    label: '🙏 佛门·禅定',       color: 'amber',   weight: 14, desc: '金刚经、六字大明咒、佛光普照、因果。' },
    ], 'abilities'),

  makeTpl('ability_dnd_school', '西幻·魔法八大学派', '🪄', ['西幻', 'D&D', '魔法学派'],
    'D&D 5e 标准八大学派 + 2 项通用：9 大能力体系。',
    [
      { key: 'abjuration',   label: '🛡 防护学派 Abjuration',   color: 'cyan',    weight: 1, desc: '护盾、反魔法、驱散、结界类魔法。' },
      { key: 'conjuration',  label: '🌀 咒法学派 Conjuration',  color: 'violet',  weight: 2, desc: '召唤、传送、创造物体（召唤怪物/异界誓缚）。' },
      { key: 'divination',   label: '🔮 预言学派 Divination',   color: 'amber',   weight: 3, desc: '侦测、真知、预言术、天眼。' },
      { key: 'enchantment',  label: '💫 附魔学派 Enchantment',  color: 'gold',    weight: 4, desc: '魅惑人类、暗示、支配人类、士气。' },
      { key: 'evocation',    label: '🔥 塑能学派 Evocation',    color: 'red',     weight: 5, desc: '火球术、闪电链、冰风暴（纯伤害）。' },
      { key: 'illusion',     label: '🎭 幻术学派 Illusion',     color: 'violet',  weight: 6, desc: '隐身、拟态、镜像、虚假幻境。' },
      { key: 'necromancy',   label: '💀 死灵学派 Necromancy',   color: 'gray',    weight: 7, desc: '操纵亡骸、吸血术、复活、恐惧。' },
      { key: 'transmutation',label: '🔬 变化学派 Transmutation',color: 'emerald', weight: 8, desc: '变形术、石化、飞行、加速、变大变小。' },
      { key: 'universal',    label: '✨ 通用秘术 Universal',    color: 'cyan',    weight: 9, desc: '奥术秘闻、秘法印记、法师护甲（跨学派）。' },
    ], 'abilities'),

  makeTpl('ability_isekai_cheat', '异世界·作弊技能体系', '🌟', ['异世界', '转生', '技能'],
    '转生文常见 10 大能力体系：技能面板、大贤者、暴食者、锻造、料理、魔法、神性…',
    [
      { key: 'skill_panel', label: '📊 技能面板 / 鉴定', color: 'cyan',    weight: 1, desc: 'Gamer 系统 / 鉴定眼 / 数值可视化。' },
      { key: 'sage',        label: '🧠 大贤者 / 解析',   color: 'violet',  weight: 2, desc: '智慧之王拉斐尔、万物解析、自动翻译。' },
      { key: 'predator',    label: '🫁 暴食者 / 捕食',   color: 'red',     weight: 3, desc: '暴食者、捕食者、毒龙吞噬、胃袋世界。' },
      { key: 'create',      label: '🛠 创造 / 土神通',   color: 'amber',   weight: 4, desc: '无限创造 / 土神通 / 神之绘手 / 物质创造。' },
      { key: 'magic',       label: '🪄 魔法 / 咏唱',      color: 'cyan',    weight: 5, desc: '六属性魔法、上位魔法、龙语魔法。' },
      { key: 'sword',       label: '⚔ 剑术 / 斗气',      color: 'gold',    weight: 6, desc: '剑技、居合、斗气、光速斩。' },
      { key: 'blacksmith',  label: '⚒ 锻造 / 神锻',       color: 'amber',   weight: 7, desc: '神级锻造、固有技能·极致加工。' },
      { key: 'cooking',     label: '🍳 料理 / 食力',      color: 'emerald', weight: 8, desc: '异世界食堂、全属性提升料理。' },
      { key: 'divine',      label: '👼 神性 / 祝福',      color: 'violet',  weight: 9, desc: '女神的祝福、勇者召唤、英雄加护。' },
      { key: 'beast_tame',  label: '🐲 魔物使 / 驯服',    color: 'emerald', weight: 10, desc: '魔物驯服、史莱姆养殖、龙骑士契约。' },
    ], 'abilities'),

  makeTpl('ability_apocalypse', '末日·异能属性 14 类', '☢', ['末日', '废土', '异能'],
    '末日觉醒异能 14 大属性：金木水火土风雷冰光暗时空精神念力。',
    [
      { key: 'metal',      label: '⛓ 金属系',       color: 'gray',    weight: 1,  desc: '操纵金属、钢铁身躯、磁力控制。' },
      { key: 'wood',       label: '🌿 草木系',       color: 'emerald', weight: 2,  desc: '催生植物、荆棘缠绕、自愈。' },
      { key: 'water',      label: '💧 水系',         color: 'cyan',    weight: 3,  desc: '控制水流、治疗、海啸。' },
      { key: 'fire',       label: '🔥 火系',         color: 'red',     weight: 4,  desc: '烈焰、爆炎、焚天。' },
      { key: 'earth',      label: '🏔 土系',         color: 'amber',   weight: 5,  desc: '地刺、土墙、重力、沙暴。' },
      { key: 'wind',       label: '💨 风系',         color: 'cyan',    weight: 6,  desc: '风刃、龙卷风、飞行、音速。' },
      { key: 'thunder',    label: '⚡ 雷系',         color: 'violet',  weight: 7,  desc: '雷击、电磁、麻痹、瞬身。' },
      { key: 'ice',        label: '🧊 冰系',         color: 'cyan',    weight: 8,  desc: '绝对零度、冰封、冰刃。' },
      { key: 'light',      label: '☀ 光系',          color: 'gold',    weight: 9,  desc: '圣光、治疗、净化、激光。' },
      { key: 'dark',       label: '🌑 暗系',         color: 'gray',    weight: 10, desc: '暗影、腐蚀、侵蚀、封印。' },
      { key: 'space',      label: '🌀 空间系',       color: 'violet',  weight: 11, desc: '瞬移、次元存储、传送、撕裂。' },
      { key: 'time',       label: '⏳ 时间系',        color: 'amber',   weight: 12, desc: '减速、加速、时间回溯、时停。' },
      { key: 'spirit',     label: '👁 精神系',       color: 'violet',  weight: 13, desc: '读心、催眠、幻术、精神冲击。' },
      { key: 'psycho',     label: '🧠 念力·御物',     color: 'cyan',    weight: 14, desc: '意念控物、TK、脑域开发。' },
    ], 'abilities'),

  makeTpl('ability_wuxia', '武侠·九流十宗', '🎋', ['武侠', '江湖', '门派'],
    '武侠九流十宗：剑、刀、枪、拳、掌、指、腿、内功、轻功、奇门。10 项。',
    [
      { key: 'sword',    label: '⚔ 剑派',       color: 'cyan',    weight: 1, desc: '独孤九剑、太极剑、辟邪剑谱。' },
      { key: 'blade',    label: '🗡 刀派',       color: 'red',     weight: 2, desc: '小李飞刀、屠龙刀、狂风刀法。' },
      { key: 'spear',    label: '🔱 枪法',       color: 'amber',   weight: 3, desc: '杨家枪、岳家枪、霸王枪。' },
      { key: 'fist',     label: '👊 拳法',       color: 'gold',    weight: 4, desc: '降龙十八掌、少林罗汉拳、太极拳。' },
      { key: 'palm',     label: '✋ 掌法',       color: 'violet',  weight: 5, desc: '黯然销魂掌、铁砂掌、冰蚕寒掌。' },
      { key: 'finger',   label: '👉 指法',       color: 'emerald', weight: 6, desc: '六脉神剑、一阳指、拈花指。' },
      { key: 'leg',      label: '🦵 腿法',       color: 'amber',   weight: 7, desc: '旋风扫叶腿、佛山无影脚。' },
      { key: 'inner',    label: '🧘 内功心法',   color: 'violet',  weight: 8, desc: '九阴真经、九阳神功、易筋经。' },
      { key: 'qing',     label: '🍃 轻功',       color: 'cyan',    weight: 9, desc: '凌波微步、梯云纵、神行百变。' },
      { key: 'special',  label: '🎭 奇门异术',   color: 'red',     weight: 10, desc: '毒术、暗器、易容、蛊术、阵法。' },
    ], 'abilities'),

  makeTpl('ability_warcraft', '魔兽·12 职业体系', '⚔', ['魔兽', 'MMO', '职业'],
    '魔兽世界 12 大职业（经典版）：战士、圣骑士、猎人、盗贼、牧师、死亡骑士、萨满、法师、术士、武僧、德鲁伊、恶魔猎手。',
    [
      { key: 'warrior',      label: '⚔ 战士 Warrior',          color: 'red',     weight: 1,  desc: '武器 / 狂怒 / 防护三系，近战物理王者。' },
      { key: 'paladin',      label: '🛡 圣骑士 Paladin',        color: 'gold',    weight: 2,  desc: '惩戒 / 神圣 / 防护，圣光信仰者。' },
      { key: 'hunter',       label: '🏹 猎人 Hunter',           color: 'emerald', weight: 3,  desc: '兽王 / 射击 / 生存，带宠物远程。' },
      { key: 'rogue',        label: '🗡 潜行者 Rogue',          color: 'amber',   weight: 4,  desc: '刺杀 / 战斗 / 敏锐，潜行爆发。' },
      { key: 'priest',       label: '✨ 牧师 Priest',           color: 'violet',  weight: 5,  desc: '戒律 / 神圣 / 暗影，治疗 / 暗伤双修。' },
      { key: 'dk',           label: '💀 死亡骑士 Death Knight', color: 'gray',    weight: 6,  desc: '鲜血 / 冰霜 / 邪恶，WotLK 英雄职业。' },
      { key: 'shaman',       label: '🌊 萨满祭司 Shaman',       color: 'cyan',    weight: 7,  desc: '元素 / 增强 / 恢复，部落传统信仰。' },
      { key: 'mage',         label: '🔮 法师 Mage',             color: 'cyan',    weight: 8,  desc: '奥术 / 火焰 / 冰霜，远程法术输出。' },
      { key: 'warlock',      label: '😈 术士 Warlock',          color: 'violet',  weight: 9,  desc: '痛苦 / 恶魔 / 毁灭，召唤恶魔契约者。' },
      { key: 'monk',         label: '☯ 武僧 Monk',              color: 'amber',   weight: 10, desc: '酒仙 / 织雾 / 踏风，潘达利亚武学。' },
      { key: 'druid',        label: '🐻 德鲁伊 Druid',          color: 'emerald', weight: 11, desc: '平衡 / 野性 / 守护 / 恢复，四系变形。' },
      { key: 'dh',           label: '👿 恶魔猎手 Demon Hunter', color: 'red',     weight: 12, desc: '浩劫 / 复仇，Legion 英雄职业，双持战刃。' },
    ], 'abilities'),
]

/* =========================================================================
 *  ⑨  PROFESSION_TEMPLATES  职业体系
 *  ========================================================================= */
const PROFESSION_TEMPLATES = [
  makeTpl('profession_universal', '冒险者·通用 30 职业', '🧭', ['通用', '冒险者', '职业'],
    '通用战斗职业 + 生产职业：战士、法师、牧师、盗贼、猎人、骑士、武僧、刺客、忍者 + 生产职业合计 30 项。',
    [
      // 战系 8
      { key: 'warrior',    label: '⚔ 战士',           color: 'red',     weight: 1,  desc: '近战物理输出，血量高。' },
      { key: 'knight',     label: '🛡 骑士 / 圣骑士',  color: 'gold',    weight: 2,  desc: '重甲 + 信仰 / 盾反。' },
      { key: 'fighter',    label: '🥊 武僧 / 格斗家',  color: 'amber',   weight: 3,  desc: '徒手格斗，拳脚功夫。' },
      { key: 'berserker',  label: '🪓 狂战士',         color: 'red',     weight: 4,  desc: '狂暴状态下输出翻倍。' },
      { key: 'archer',     label: '🏹 弓箭手 / 猎人', color: 'emerald', weight: 5,  desc: '远程物理 + 宠物。' },
      { key: 'assassin',   label: '🗡 刺客 / 忍者',    color: 'violet',  weight: 6,  desc: '潜行爆发，背刺暴击。' },
      { key: 'lancer',     label: '🔱 枪兵',           color: 'cyan',    weight: 7,  desc: '长柄武器，骑乘专精。' },
      { key: 'scout',      label: '🔭 斥候 / 侦察兵', color: 'amber',   weight: 8,  desc: '陷阱、侦察、小地图。' },
      // 法系 8
      { key: 'mage',       label: '🔮 法师',           color: 'cyan',    weight: 9,  desc: '元素 / 奥术魔法输出。' },
      { key: 'priest',     label: '⛪ 牧师',           color: 'gold',    weight: 10, desc: '治疗 + 辅助 + 圣光。' },
      { key: 'warlock',    label: '😈 术士 / 召唤师', color: 'violet',  weight: 11, desc: '召唤恶魔 / 亡灵 / 宠物。' },
      { key: 'druid',      label: '🌿 德鲁伊',         color: 'emerald', weight: 12, desc: '变形 + 自然魔法。' },
      { key: 'necromancer',label: '💀 死灵法师',       color: 'gray',    weight: 13, desc: '召唤亡骸 / 吸血术。' },
      { key: 'bard',       label: '🎵 吟游诗人',       color: 'cyan',    weight: 14, desc: '辅助 + 控场 + 歌唱。' },
      { key: 'sorcerer',   label: '✨ 术士 Sorcerer',  color: 'violet',  weight: 15, desc: '天生血脉施法者。' },
      { key: 'shaman',     label: '🌊 萨满',           color: 'cyan',    weight: 16, desc: '图腾 + 元素 + 祖先魂。' },
      // 生产 8
      { key: 'blacksmith', label: '⚒ 铁匠 / 锻造师',  color: 'amber',   weight: 17, desc: '打造武器防具。' },
      { key: 'alchemist',  label: '🧪 炼金 / 药师',    color: 'emerald', weight: 18, desc: '制作药水、炼金物品。' },
      { key: 'chef',       label: '🍳 厨师 / 料理人', color: 'red',     weight: 19, desc: '做属性加成食物。' },
      { key: 'tailor',     label: '🧵 裁缝',           color: 'violet',  weight: 20, desc: '制作布甲、长袍。' },
      { key: 'leather',    label: '🦬 制皮师',         color: 'amber',   weight: 21, desc: '制作皮甲、背包。' },
      { key: 'jewel',      label: '💍 珠宝匠',         color: 'gold',    weight: 22, desc: '宝石切割、首饰镶嵌。' },
      { key: 'scribe',     label: '📜 抄写员 / 铭文师',color: 'cyan',    weight: 23, desc: '卷轴、铭文、法杖附魔。' },
      { key: 'engineer',   label: '⚙ 工程师',         color: 'gray',    weight: 24, desc: '机械、爆炸物、虫洞生成器。' },
      // 特殊 6
      { key: 'merchant',   label: '💰 商人',           color: 'gold',    weight: 25, desc: '砍价、拍卖行、倒卖。' },
      { key: 'farmer',     label: '🌾 农民 / 药草师',  color: 'emerald', weight: 26, desc: '种田、采药、采矿。' },
      { key: 'miner',      label: '⛏ 矿工 / 伐木工',  color: 'amber',   weight: 27, desc: '采集矿物、木材资源。' },
      { key: 'fisher',     label: '🎣 渔夫',           color: 'cyan',    weight: 28, desc: '钓鱼、水系资源。' },
      { key: 'ranger',     label: '🏞 游侠 / 守林人',  color: 'emerald', weight: 29, desc: '野外生存、向导。' },
      { key: 'sage',       label: '📚 贤者 / 学者',    color: 'violet',  weight: 30, desc: '知识、考古、研究。' },
    ], 'professions'),

  makeTpl('profession_xianxia', '修真·百业 22 类', '🏮', ['修真', '仙侠', '职业'],
    '修真百业：剑修、法修、丹修、器修、阵修、符修、御兽、魔修、鬼修、体修、禅修… 22 项。',
    [
      // 正统 10
      { key: 'jianxiu',   label: '⚔ 剑修',         color: 'cyan',    weight: 1,  desc: '以剑入道，一剑破万法。' },
      { key: 'faxiu',     label: '✨ 法修 / 术修',  color: 'violet',  weight: 2,  desc: '五行法术、雷法、火系。' },
      { key: 'danxiu',    label: '🧪 丹修',         color: 'emerald', weight: 3,  desc: '炼丹为业，丹道圣手。' },
      { key: 'qixiu',     label: '🔨 器修',         color: 'amber',   weight: 4,  desc: '炼器、铸剑、傀儡。' },
      { key: 'zhenxiu',   label: '🕸 阵修',         color: 'violet',  weight: 5,  desc: '布置阵法、阵盘、阵旗。' },
      { key: 'fuxiu',     label: '📜 符修',         color: 'gold',    weight: 6,  desc: '画符、符箓买卖。' },
      { key: 'yushou',    label: '🐲 御兽师',       color: 'emerald', weight: 7,  desc: '收服妖兽、驭兽战斗。' },
      { key: 'tixiu',     label: '💪 体修',         color: 'amber',   weight: 8,  desc: '外功炼体，金刚不坏。' },
      { key: 'chanxiu',   label: '🙏 禅修 / 佛修',  color: 'gold',    weight: 9,  desc: '佛门弟子、修心炼性。' },
      { key: 'daoxiu',    label: '☯ 道修 / 炼气士', color: 'violet',  weight: 10, desc: '正统道门、清净无为。' },
      // 旁门 8
      { key: 'moxiu',     label: '😈 魔修',         color: 'red',     weight: 11, desc: '魔道、血祭、双修。' },
      { key: 'guixiu',    label: '👻 鬼修 / 尸修',  color: 'gray',    weight: 12, desc: '鬼道、尸解、阴神。' },
      { key: 'yaoxiu',    label: '🦊 妖修',         color: 'emerald', weight: 13, desc: '妖族化形、修炼。' },
      { key: 'guxiu',     label: '🐢 蛊修 / 毒修',  color: 'red',     weight: 14, desc: '养蛊、下毒、苗疆秘术。' },
      { key: 'jixiu',     label: '🎭 机关 / 傀儡师', color: 'gray',    weight: 15, desc: '墨家机关术、傀儡操控。' },
      { key: 'yinxiu',    label: '🎵 音修',         color: 'cyan',    weight: 16, desc: '琴道、箫道、梵音。' },
      { key: 'buxiu',     label: '🌀 卜筮 / 算命',  color: 'amber',   weight: 17, desc: '天机推演、占卜、看相。' },
      { key: 'lixiu',     label: '⚖ 律修 / 儒修',   color: 'gold',    weight: 18, desc: '读书养浩然气、笔伐口诛。' },
      // 杂项 4
      { key: 'lingshou',  label: '💰 灵商 / 掮客',   color: 'gold',    weight: 19, desc: '坊市买卖、中介、拍卖会。' },
      { key: 'lieshou',   label: '🏹 灵猎',         color: 'emerald', weight: 20, desc: '猎取妖兽材料、灵草。' },
      { key: 'mushi',     label: '🏥 灵医',         color: 'cyan',    weight: 21, desc: '疗伤、解毒、问诊。' },
      { key: 'ditu',      label: '🗺 地师 / 寻龙',   color: 'amber',   weight: 22, desc: '看风水、寻龙脉、找秘境。' },
    ], 'professions'),
]

/* =========================================================================
 *  ⑩  CURRENCY_TEMPLATES  货币 / 灵石体系
 *  ========================================================================= */
const CURRENCY_TEMPLATES = [
  makeTpl('currency_xianxia', '修真·灵石体系 8 级', '💎', ['修真', '灵石', '货币'],
    '下品灵石→中品→上品→极品→仙晶→神晶→鸿蒙紫气，1:100 汇率。',
    [
      { key: 'c_tong',    label: '🟤 铜钱（凡俗）',        color: 'amber',   weight: 1, desc: '1000 文 = 1 两白银，凡人交易。' },
      { key: 'c_yin',     label: '⚪ 白银（凡俗）',        color: 'gray',    weight: 2, desc: '凡俗通用：10 两 = 1 两黄金。' },
      { key: 'c_xia',     label: '🟢 下品灵石',           color: 'emerald', weight: 3, desc: '修士基础货币：100 下品 = 1 中品。' },
      { key: 'c_zhong',   label: '🔵 中品灵石',           color: 'cyan',    weight: 4, desc: '筑基 / 金丹修士常用。' },
      { key: 'c_shang',   label: '🟣 上品灵石',           color: 'violet',  weight: 5, desc: '元婴 / 化神大宗交易。' },
      { key: 'c_jipin',   label: '🟠 极品灵石',           color: 'amber',   weight: 6, desc: '炼虚 / 合体 / 大乘级。' },
      { key: 'c_xian',    label: '🟡 仙晶（仙界货币）',    color: 'gold',    weight: 7, desc: '飞升仙界后使用：仙气凝结。' },
      { key: 'c_shen',    label: '💠 神晶 / 鸿蒙紫气',     color: 'gold',    weight: 8, desc: '圣人级 / 封神 / 混沌之物。' },
    ], 'currencies'),

  makeTpl('currency_western_dnd', '西幻·D&D 标准金币', '🪙', ['西幻', 'D&D', '金币'],
    'D&D 5e 标准：CP(铜)→SP(银)→EP(银电)→GP(金)→PP(铂) + 魔法晶石。',
    [
      { key: 'cp', label: '🟤 CP 铜币 Copper',   color: 'amber',   weight: 1, desc: '100 CP = 1 GP。' },
      { key: 'sp', label: '⚪ SP 银币 Silver',   color: 'gray',    weight: 2, desc: '10 SP = 1 GP。' },
      { key: 'ep', label: '🔵 EP 电银 Electrum', color: 'cyan',    weight: 3, desc: '5 EP = 1 GP（少见）。' },
      { key: 'gp', label: '🟡 GP 金币 Gold',     color: 'gold',    weight: 4, desc: '标准本位币。' },
      { key: 'pp', label: '💎 PP 铂币 Platinum', color: 'violet',  weight: 5, desc: '1 PP = 10 GP。' },
      { key: 'gs', label: '💠 魔晶石',            color: 'cyan',    weight: 6, desc: '大型交易 / 魔法耗材（1 GS ≈ 50 GP）。' },
    ], 'currencies'),

  makeTpl('currency_warcraft', '魔兽·金币体系', '💰', ['魔兽', 'MMO', '金币'],
    '魔兽经典：铜 → 银 → 金 + 时光徽章 + 要塞资源。',
    [
      { key: 'wc_cu', label: '🟤 铜币 Copper',    color: 'amber',   weight: 1, desc: '100 铜 = 1 银。' },
      { key: 'wc_si', label: '⚪ 银币 Silver',    color: 'gray',    weight: 2, desc: '100 银 = 1 金。' },
      { key: 'wc_go', label: '🟡 金币 Gold',      color: 'gold',    weight: 3, desc: '基本货币：大鸟 5000G 时代。' },
      { key: 'wc_tk', label: '⏳ 时光徽章 WoW Token', color: 'violet', weight: 4, desc: '现金兑换金币，跨服交易。' },
      { key: 'wc_ap', label: '⚔ 勇气 / 征服点',   color: 'red',     weight: 5, desc: '副本货币：兑换 476+ 装备。' },
      { key: 'wc_gr', label: '💎 要塞资源',       color: 'emerald', weight: 6, desc: 'Warlords of Draenor 要塞货栈。' },
    ], 'currencies'),

  makeTpl('currency_isekai', '异世界·金·银·铜币 + 贡献', '🌏', ['异世界', '转生', '货币'],
    '异世界通用：铜币 / 银币 / 金币 / 白金币 / 魔石 / 公会贡献点。',
    [
      { key: 'is_c',   label: '🟤 铜币',           color: 'amber',   weight: 1, desc: '100 铜 = 1 银。' },
      { key: 'is_s',   label: '⚪ 银币',           color: 'gray',    weight: 2, desc: '100 银 = 1 金。' },
      { key: 'is_g',   label: '🟡 金币',           color: 'gold',    weight: 3, desc: '一般冒险者常用。' },
      { key: 'is_p',   label: '💎 白金币',         color: 'cyan',    weight: 4, desc: '1 白金 = 100 金，贵族交易。' },
      { key: 'is_m',   label: '💠 魔石',           color: 'violet',  weight: 5, desc: '魔物核心 / 能源 / 等价物。' },
      { key: 'is_po',  label: '🪙 王国金币 / 圣币', color: 'gold',    weight: 6, desc: '神圣教国圣金、王国纪念币。' },
      { key: 'is_pt',  label: '⭐ 公会贡献点',     color: 'emerald', weight: 7, desc: '冒险者公会任务积分。' },
      { key: 'is_hon', label: '🛡 王国荣誉值',     color: 'red',     weight: 8, desc: '击退魔族 / 战功获得。' },
    ], 'currencies'),

  makeTpl('currency_apocalypse', '末日·物资·贡献·结晶', '☢', ['末日', '废土', '货币'],
    '末日废土：香烟（硬通货）、罐头、贡献点、信用点、异能结晶、基因药剂。',
    [
      { key: 'ap_fd',  label: '🥫 食物·罐头（硬通货）', color: 'amber',   weight: 1, desc: '最基础等价物，1 罐头 = 1 天口粮。' },
      { key: 'ap_xy',  label: '🚬 香烟',               color: 'gray',    weight: 2, desc: '末日后社交硬通货。' },
      { key: 'ap_zy',  label: '💊 药品·抗生素',        color: 'emerald', weight: 3, desc: '高价值救命等价物。' },
      { key: 'ap_gx',  label: '⭐ 基地贡献点',         color: 'gold',    weight: 4, desc: '安全区内部电子积分。' },
      { key: 'ap_xy2', label: '💳 信用点 / 军票',       color: 'cyan',    weight: 5, desc: '军部 / 大型基地发行。' },
      { key: 'ap_yn',  label: '💎 异能结晶',           color: 'violet',  weight: 6, desc: '击杀变异兽 / 丧尸获取，觉醒者硬通货。' },
      { key: 'ap_jy',  label: '🧬 基因药剂 / S 核',    color: 'red',     weight: 7, desc: '顶级贵重物品，用于觉醒 / 突破。' },
    ], 'currencies'),
]

/* =========================================================================
 *  全部导出
 *  ========================================================================= */
export {
  ARTIFACT_RARITY_TEMPLATES,
  CREATURE_DANGER_TEMPLATES,
  ANOMALY_DANGER_TEMPLATES,
  ERA_TEMPLATES,
  RELATION_TYPE_TEMPLATES,
  ORIGIN_LAW_TIER_TEMPLATES,
  LORE_CATEGORY_TEMPLATES,
  ABILITY_SYSTEM_TEMPLATES,
  PROFESSION_TEMPLATES,
  CURRENCY_TEMPLATES,
}

/** 宝物稀有度模板列表（供编辑器显示） */
export function getArtifactRarityTemplateList() { return ARTIFACT_RARITY_TEMPLATES.slice() }
export function getArtifactRarityTemplateByKey(key) {
  return ARTIFACT_RARITY_TEMPLATES.find(t => t.templateKey === key)
}

/** 异兽危险等级模板列表 */
export function getCreatureDangerTemplateList() { return CREATURE_DANGER_TEMPLATES.slice() }
export function getCreatureDangerTemplateByKey(key) {
  return CREATURE_DANGER_TEMPLATES.find(t => t.templateKey === key)
}

/** 异常物危险等级模板列表 */
export function getAnomalyDangerTemplateList() { return ANOMALY_DANGER_TEMPLATES.slice() }
export function getAnomalyDangerTemplateByKey(key) {
  return ANOMALY_DANGER_TEMPLATES.find(t => t.templateKey === key)
}

/** 时代分类模板列表 */
export function getEraTemplateList() { return ERA_TEMPLATES.slice() }
export function getEraTemplateByKey(key) { return ERA_TEMPLATES.find(t => t.templateKey === key) }

/** 关系类型模板列表 */
export function getRelationTemplateList() { return RELATION_TYPE_TEMPLATES.slice() }
export function getRelationTemplateByKey(key) {
  return RELATION_TYPE_TEMPLATES.find(t => t.templateKey === key)
}

/** 本源法则层级模板列表 */
export function getOriginLawTemplateList() { return ORIGIN_LAW_TIER_TEMPLATES.slice() }
export function getOriginLawTemplateByKey(key) {
  return ORIGIN_LAW_TIER_TEMPLATES.find(t => t.templateKey === key)
}

/** 设定页分类模板列表 */
export function getLoreCategoryTemplateList() { return LORE_CATEGORY_TEMPLATES.slice() }
export function getLoreCategoryTemplateByKey(key) {
  return LORE_CATEGORY_TEMPLATES.find(t => t.templateKey === key)
}

/** 能力体系模板列表 */
export function getAbilitySystemTemplateList() { return ABILITY_SYSTEM_TEMPLATES.slice() }
export function getAbilitySystemTemplateByKey(key) {
  return ABILITY_SYSTEM_TEMPLATES.find(t => t.templateKey === key)
}

/** 职业体系模板列表 */
export function getProfessionTemplateList() { return PROFESSION_TEMPLATES.slice() }
export function getProfessionTemplateByKey(key) {
  return PROFESSION_TEMPLATES.find(t => t.templateKey === key)
}

/** 货币体系模板列表 */
export function getCurrencyTemplateList() { return CURRENCY_TEMPLATES.slice() }
export function getCurrencyTemplateByKey(key) {
  return CURRENCY_TEMPLATES.find(t => t.templateKey === key)
}
