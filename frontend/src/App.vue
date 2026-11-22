<script setup>
/**
 * 根组件
 * 根据当前路由决定使用前台布局(LoreLayout)还是后台布局(AdminLayout)
 * 通过 router-view 的嵌套实现不同布局的切换
 */
</script>

<template>
  <router-view />
</template>

<style scoped>
/* 根组件无需额外样式，布局由子组件控制 */
</style>
