import { computed } from 'vue'
import { useWorldDataStore } from '@/stores/worldData'

/**
 * 术语链接处理逻辑 (LoreLink 核心功能)
 *
 * 该 composable 负责将纯文本内容中的已知术语（角色名、族群名、宝物名等）
 * 自动识别并转换为可点击的链接信息。
 *
 * 使用方式：
 *   const { processText, getLoreLink } = useLoreLinks()
 *   const segments = processText('旅者与雷电将军在稻妻相遇')
 *   // segments => [{ text: '旅者与', type: 'text' }, { text: '雷电将军', type: 'link', ... }, { text: '在稻妻相遇', type: 'text' }]
 */

export function useLoreLinks() {
  const worldData = useWorldDataStore()

  /**
   * 根据术语类型获取对应的路由路径
   * @param {string} type - 术语类型 (character/faction/artifact/creature/fragment-world)
   * @param {string|number} idOrSlug - ID或slug
   * @returns {string} 路由路径
   */
  function getLoreLink(type, idOrSlug) {
    const id = idOrSlug || ''
    switch (type) {
      case 'character':
        return `/characters/${id}`
      case 'faction':
        return `/factions/${id}`
      case 'artifact':
        return `/artifacts/${id}`
      case 'creature':
        return `/creatures/${id}`
      case 'fragment-world':
        return `/fragment-worlds/${id}`
      case 'ability':
        return `/abilities/${id}`
      case 'realm':
        return `/realms/${id}`
      default:
        // 未知类型走通用 slug 路由
        return `/lore/${id}`
    }
  }

  /**
   * 处理文本，将术语替换为链接段
   * @param {string} text - 原始文本
   * @returns {Array} 文本段数组，每个段标记是普通文本还是链接
   *
   * 返回格式示例：
   * [
   *   { type: 'text', content: '旅者与' },
   *   { type: 'link', content: '雷电将军', linkType: 'character', href: '/characters/1', id: 1 },
   *   { type: 'text', content: '在稻妻相遇' }
   * ]
   */
  function processText(text) {
    if (!text) return [{ type: 'text', content: '' }]

    const dictionary = worldData.loreDictionary
    // 获取所有术语名，按长度降序排序（优先匹配长术语）
    const terms = Object.keys(dictionary).sort((a, b) => b.length - a.length)

    if (terms.length === 0) {
      return [{ type: 'text', content: text }]
    }

    // 构建正则表达式匹配所有术语
    const escapedTerms = terms.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
    const regex = new RegExp(`(${escapedTerms.join('|')})`, 'g')

    const segments = []
    let lastIndex = 0
    let match

    while ((match = regex.exec(text)) !== null) {
      // 添加匹配前的普通文本
      if (match.index > lastIndex) {
        segments.push({
          type: 'text',
          content: text.slice(lastIndex, match.index),
        })
      }

      // 添加匹配到的术语链接
      const term = match[0]
      const loreInfo = dictionary[term]
      segments.push({
        type: 'link',
        content: term,
        linkType: loreInfo.type,
        href: getLoreLink(loreInfo.type, loreInfo.slug || loreInfo.id),
        id: loreInfo.id,
      })

      lastIndex = regex.lastIndex
    }

    // 添加剩余的普通文本
    if (lastIndex < text.length) {
      segments.push({
        type: 'text',
        content: text.slice(lastIndex),
      })
    }

    return segments
  }

  /**
   * 检查文本中是否包含任何已知术语
   * @param {string} text - 待检查文本
   * @returns {boolean}
   */
  function hasLoreTerms(text) {
    if (!text) return false
    const dictionary = worldData.loreDictionary
    return Object.keys(dictionary).some((term) => text.includes(term))
  }

  return {
    processText,
    getLoreLink,
    hasLoreTerms,
    // 暴露词典供外部使用
    loreDictionary: computed(() => worldData.loreDictionary),
  }
}
