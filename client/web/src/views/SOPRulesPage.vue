<template>
  <div class="sop-rules-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <a-space direction="vertical" :size="8">
        <a-typography-title :level="2">
          ⚙️ 业务规则
        </a-typography-title>
        <a-typography-text type="secondary">
          配置和管理业务规则
        </a-typography-text>
      </a-space>
    </div>

    <!-- 页面内容 -->
    <a-card class="content-card">
      <a-typography-paragraph>
        业务规则页面正在开发中...
      </a-typography-paragraph>
    </a-card>
  </div>
</template>

<script setup lang="ts">
// 业务规则页面
</script>

<style scoped>
.sop-rules-page {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.content-card {
  padding: 24px;
}
</style>