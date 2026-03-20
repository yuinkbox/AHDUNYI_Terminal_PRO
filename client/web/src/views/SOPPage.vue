<template>
  <div class="sop-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <a-space direction="vertical" :size="8">
        <a-typography-title :level="2">
          📋 红线标准
        </a-typography-title>
        <a-typography-text type="secondary">
          查看和管理安全红线标准
        </a-typography-text>
      </a-space>
    </div>

    <!-- 页面内容 -->
    <a-card class="content-card">
      <a-typography-paragraph>
        红线标准页面正在开发中...
      </a-typography-paragraph>
    </a-card>
  </div>
</template>

<script setup lang="ts">
// 红线标准页面
</script>

<style scoped>
.sop-page {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.content-card {
  padding: 24px;
}
</style>