<template>
  <div class="risk-audit-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <a-space direction="vertical" :size="8">
        <a-typography-title :level="2">
          🛡️ 风险审查
        </a-typography-title>
        <a-typography-text type="secondary">
          风险识别、评估与处置管理
        </a-typography-text>
      </a-space>
    </div>

    <!-- 页面内容 -->
    <a-card class="content-card">
      <a-space direction="vertical" :size="24">
        <!-- 模块状态 -->
        <a-alert type="info" show-icon>
          <template #icon>
            <icon-info-circle />
          </template>
          风险审查模块正在开发中，预计 v1.1 版本上线
        </a-alert>

        <!-- 功能预览 -->
        <a-row :gutter="16">
          <a-col :span="8">
            <a-card hoverable>
              <template #cover>
                <div class="module-icon">
                  <icon-radar-chart size="48" />
                </div>
              </template>
              <a-card-meta title="实时风险监测">
                <template #description>
                  动态监控系统风险指标
                </template>
              </a-card-meta>
            </a-card>
          </a-col>
          <a-col :span="8">
            <a-card hoverable>
              <template #cover>
                <div class="module-icon">
                  <icon-alert size="48" />
                </div>
              </template>
              <a-card-meta title="风险预警">
                <template #description>
                  智能预警与通知机制
                </template>
              </a-card-meta>
            </a-card>
          </a-col>
          <a-col :span="8">
            <a-card hoverable>
              <template #cover>
                <div class="module-icon">
                  <icon-file-search size="48" />
                </div>
              </template>
              <a-card-meta title="审计报告">
                <template #description>
                  生成详细风险审计报告
                </template>
              </a-card-meta>
            </a-card>
          </a-col>
        </a-row>

        <!-- 开发进度 -->
        <a-card title="开发进度">
          <a-progress :percent="35" :show-text="false" />
          <a-typography-text type="secondary">
            已完成基础框架，正在进行业务逻辑开发
          </a-typography-text>
        </a-card>
      </a-space>
    </a-card>
  </div>
</template>

<script setup lang="ts">
// 风险审查页面
</script>

<style scoped>
.risk-audit-page {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.content-card {
  padding: 24px;
}

.module-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 120px;
  background: linear-gradient(135deg, #f0f5ff 0%, #e6f7ff 100%);
  border-radius: 8px 8px 0 0;
}
</style>