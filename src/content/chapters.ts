export interface ChapterMeta {
  id: string
  /** 章节序号，如 "第一章" */
  num: string
  title: string
  short: string
  desc: string
  /** 题量徽标，如 "30 题"；无则为空 */
  questions?: string
  /** 预计阅读分钟数 */
  minutes: number
  /** 内容最近整理月份 */
  lastUpdated: string
  /** 适用范围 */
  applicableTo: string
  /** 模块主题色 */
  color: string
  icon: string
  group: 'start' | 'modules' | 'tools'
}

export const chapterGroups: { key: ChapterMeta['group']; label: string }[] = [
  { key: 'start', label: '入门' },
  { key: 'modules', label: '六大模块' },
  { key: 'tools', label: '规划与工具' },
]

export const chapters: ChapterMeta[] = [
  {
    id: 'intro',
    num: '第一章',
    title: '认识行测：考试全景与备考地图',
    short: '认识行测',
    desc: '试卷结构、题量分布、时间与分值、六大模块难度—性价比矩阵与做题顺序建议。',
    minutes: 8,
    lastUpdated: '2026-09',
    applicableTo: '国考与省考通用框架',
    color: '#2563eb',
    icon: 'compass',
    group: 'start',
  },
  {
    id: 'yanyu',
    num: '第二章',
    title: '言语理解与表达',
    short: '言语理解',
    desc: '逻辑填空三步法、实词成语辨析、片段阅读六大考点与语句表达规律。',
    questions: '30 题',
    minutes: 22,
    lastUpdated: '2026-09',
    applicableTo: '国考与多数省考',
    color: '#0ea5e9',
    icon: 'chat',
    group: 'modules',
  },
  {
    id: 'zhengzhi',
    num: '第三章',
    title: '政治理论',
    short: '政治理论',
    desc: '投入产出比最高的模块：马原框架、党史节点、新时代核心表述与背诵锚点。',
    questions: '20 题',
    minutes: 15,
    lastUpdated: '2026-09',
    applicableTo: '通用理论框架，时政以最新考纲为准',
    color: '#e11d48',
    icon: 'flag',
    group: 'modules',
  },
  {
    id: 'panduan',
    num: '第四章',
    title: '判断推理',
    short: '判断推理',
    desc: '图形推理规律清单、定义要件匹配、类比关系模型与逻辑判断七大考点。',
    questions: '35 题',
    minutes: 30,
    lastUpdated: '2026-09',
    applicableTo: '国考与多数省考',
    color: '#7c3aed',
    icon: 'puzzle',
    group: 'modules',
  },
  {
    id: 'changshi',
    num: '第五章',
    title: '常识判断',
    short: '常识判断',
    desc: '六大板块考点清单：法律与科技生活重点攻坚，其余板块高效积累策略。',
    questions: '15 题',
    minutes: 12,
    lastUpdated: '2026-09',
    applicableTo: '通用知识框架，时政以最新考纲为准',
    color: '#d97706',
    icon: 'book',
    group: 'modules',
  },
  {
    id: 'shuliang',
    num: '第六章',
    title: '数量关系',
    short: '数量关系',
    desc: '七大核心解题思想与九类高频题型：行程、工程、利润、排列组合、概率、容斥。',
    questions: '15/10 题',
    minutes: 28,
    lastUpdated: '2026-09',
    applicableTo: '国考与多数省考',
    color: '#059669',
    icon: 'sigma',
    group: 'modules',
  },
  {
    id: 'ziliao',
    num: '第七章',
    title: '资料分析',
    short: '资料分析',
    desc: '全卷性价比之王：公式体系、截位直除、特征数字法与比重秒杀判断。',
    questions: '20 题',
    minutes: 26,
    lastUpdated: '2026-09',
    applicableTo: '国考与多数省考',
    color: '#0891b2',
    icon: 'chart',
    group: 'modules',
  },
  {
    id: 'beikao',
    num: '第八章',
    title: '备考路线图与时间分配',
    short: '备考路线图',
    desc: '三阶段备考法、各模块时间与得分目标、错题本建立方法与常见误区。',
    minutes: 9,
    lastUpdated: '2026-09',
    applicableTo: '通用备考建议，题量以招考公告为准',
    color: '#e05e8a',
    icon: 'route',
    group: 'tools',
  },
  {
    id: 'fujian',
    num: '附录',
    title: '速查工具箱',
    short: '速查工具箱',
    desc: '速算对照表、高频易错成语、核心公式速查与每日学习计划模板。',
    minutes: 10,
    lastUpdated: '2026-09',
    applicableTo: '国考与多数省考',
    color: '#64748b',
    icon: 'bookmark',
    group: 'tools',
  },
]

export const chapterMap = new Map(chapters.map((c) => [c.id, c]))

export function getChapter(id: string): ChapterMeta | undefined {
  return chapterMap.get(id)
}
