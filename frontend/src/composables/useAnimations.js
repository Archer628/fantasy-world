import { onMounted, onUnmounted, ref } from 'vue'
import { gsap } from 'gsap'

/**
 * GSAP 动画封装
 *
 * 提供常用的动画方法，统一管理动画生命周期
 * - 淡入动画
 * - 滑入动画
 * - 缩放动画
 * - 列表错位动画
 * - 金色闪光效果
 */

export function useAnimations() {
  /** 动画引用集合，用于组件卸载时清理 */
  const animations = ref([])

  /**
   * 元素淡入向上动画
   * @param {Element|Vue ref} el - 目标元素
   * @param {Object} options - 动画选项
   */
  function fadeInUp(el, options = {}) {
    const element = el?.$el || el
    if (!element) return

    const anim = gsap.fromTo(
      element,
      { opacity: 0, y: 30 },
      {
        opacity: 1,
        y: 0,
        duration: 0.6,
        ease: 'power2.out',
        ...options,
      }
    )
    animations.value.push(anim)
    return anim
  }

  /**
   * 元素淡入动画
   * @param {Element|Vue ref} el - 目标元素
   * @param {Object} options - 动画选项
   */
  function fadeIn(el, options = {}) {
    const element = el?.$el || el
    if (!element) return

    const anim = gsap.fromTo(
      element,
      { opacity: 0 },
      {
        opacity: 1,
        duration: 0.5,
        ease: 'power2.out',
        ...options,
      }
    )
    animations.value.push(anim)
    return anim
  }

  /**
   * 元素缩放进入动画
   * @param {Element|Vue ref} el - 目标元素
   * @param {Object} options - 动画选项
   */
  function scaleIn(el, options = {}) {
    const element = el?.$el || el
    if (!element) return

    const anim = gsap.fromTo(
      element,
      { opacity: 0, scale: 0.8 },
      {
        opacity: 1,
        scale: 1,
        duration: 0.4,
        ease: 'back.out(1.7)',
        ...options,
      }
    )
    animations.value.push(anim)
    return anim
  }

  /**
   * 列表错位动画
   * @param {Array<Element>|NodeList} elements - 元素列表
   * @param {Object} options - 动画选项
   */
  function staggerList(elements, options = {}) {
    const els = Array.from(elements)
    if (els.length === 0) return

    const anim = gsap.fromTo(
      els,
      { opacity: 0, y: 20 },
      {
        opacity: 1,
        y: 0,
        duration: 0.5,
        stagger: 0.08,
        ease: 'power2.out',
        ...options,
      }
    )
    animations.value.push(anim)
    return anim
  }

  /**
   * 从左滑入动画
   * @param {Element|Vue ref} el - 目标元素
   * @param {Object} options - 动画选项
   */
  function slideInLeft(el, options = {}) {
    const element = el?.$el || el
    if (!element) return

    const anim = gsap.fromTo(
      element,
      { opacity: 0, x: -40 },
      {
        opacity: 1,
        x: 0,
        duration: 0.5,
        ease: 'power2.out',
        ...options,
      }
    )
    animations.value.push(anim)
    return anim
  }

  /**
   * 金色闪光脉冲效果（循环动画）
   * @param {Element|Vue ref} el - 目标元素
   */
  function goldPulse(el) {
    const element = el?.$el || el
    if (!element) return

    const anim = gsap.to(element, {
      boxShadow: '0 0 20px rgba(212, 168, 83, 0.6), 0 0 40px rgba(212, 168, 83, 0.3)',
      duration: 1.5,
      repeat: -1,
      yoyo: true,
      ease: 'sine.inOut',
    })
    animations.value.push(anim)
    return anim
  }

  /**
   * 悬停动画 - 金色发光
   * @param {Element|Vue ref} el - 目标元素
   */
  function hoverGlow(el) {
    const element = el?.$el || el
    if (!element) return

    const enter = () => {
      gsap.to(element, {
        boxShadow: '0 0 20px rgba(212, 168, 83, 0.5)',
        scale: 1.02,
        duration: 0.3,
        ease: 'power2.out',
      })
    }

    const leave = () => {
      gsap.to(element, {
        boxShadow: '0 0 0px rgba(212, 168, 83, 0)',
        scale: 1,
        duration: 0.3,
        ease: 'power2.out',
      })
    }

    element.addEventListener('mouseenter', enter)
    element.addEventListener('mouseleave', leave)

    return () => {
      element.removeEventListener('mouseenter', enter)
      element.removeEventListener('mouseleave', leave)
    }
  }

  /**
   * 清理所有动画
   */
  function killAllAnimations() {
    animations.value.forEach((anim) => {
      if (anim && typeof anim.kill === 'function') {
        anim.kill()
      }
    })
    animations.value = []
  }

  // 组件卸载时自动清理动画
  onUnmounted(() => {
    killAllAnimations()
  })

  return {
    fadeInUp,
    fadeIn,
    scaleIn,
    staggerList,
    slideInLeft,
    goldPulse,
    hoverGlow,
    killAllAnimations,
    gsap, // 暴露 gsap 供高级使用
  }
}
