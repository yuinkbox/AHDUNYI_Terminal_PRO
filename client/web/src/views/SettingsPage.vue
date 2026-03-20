<template>
  <div class="settings-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <a-space direction="vertical" :size="8">
        <a-typography-title :level="2">
          ⚙️ 系统设置
        </a-typography-title>
        <a-typography-text type="secondary">
          管理系统配置和用户权限
        </a-typography-text>
      </a-space>
    </div>

    <!-- 页面内容 -->
    <a-card class="content-card">
      <a-typography-paragraph>
        系统设置页面正在开发中...
      </a-typography-paragraph>
    </a-card>
  </div>
</template>

<script setup lang="ts">
// 系统设置页面
</script>

<style scoped>
.settings-page {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.content-card {
  padding: 24px;
}
</style>