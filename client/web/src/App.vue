<template>
  <a-config-provider>
    <div id="app">
      <!-- 路由视图 -->
      <router-view />
      
      <!-- 全局消息提示容器 -->
      <a-message-provider />
      <a-notification-provider />
      <a-modal-provider />
    </div>
  </a-config-provider>
</template>

<script setup lang="ts">
// App.vue 现在是纯路由容器
// 所有页面逻辑都在各自的页面组件中
</script>

<style>
#app {
  min-height: 100vh;
  width: 100%;
}
</style>