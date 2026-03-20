<template>
  <div class="violation-review-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <a-space direction="vertical" :size="8">
        <a-typography-title :level="2">
          📜 违规复核
        </a-typography-title>
        <a-typography-text type="secondary">
          违规事件审查与处理流程管理
        </a-typography-text>
      </a-space>
    </div>

    <!-- 页面内容 -->
    <a-card class="content-card">
      <a-space direction="vertical" :size="24">
        <!-- 状态提示 -->
        <a-alert type="warning" show-icon>
          <template #icon>
            <icon-exclamation-circle />
          </template>
          违规复核模块正在优化中，部分功能暂不可用
        </a-alert>

        <!-- 待处理事项 -->
        <a-card title="待处理事项" :bordered="false">
          <a-list :data="pendingItems">
            <template #item="{ item }">
              <a-list-item>
                <a-list-item-meta>
                  <template #title>
                    <a-tag :color="item.severityColor">{{ item.severity }}</a-tag>
                    {{ item.title }}
                  </template>
                  <template #description>
                    <a-space :size="8">
                      <span>{{ item.description }}</span>
                      <a-tag size="small">{{ item.type }}</a-tag>
                    </a-space>
                  </template>
                </a-list-item-meta>
                <template #actions>
                  <a-button type="outline" size="small">查看详情</a-button>
                  <a-button type="primary" size="small">处理</a-button>
                </template>
              </a-list-item>
            </template>
          </a-list>
        </a-card>

        <!-- 统计信息 -->
        <a-row :gutter="16">
          <a-col :span="6">
            <a-statistic
              title="待处理"
              :value="12"
              :value-style="{ color: '#ff7d00' }"
              show-group-separator
            >
              <template #prefix>
                <icon-clock-circle />
              </template>
            </a-statistic>
          </a-col>
          <a-col :span="6">
            <a-statistic
              title="处理中"
              :value="5"
              :value-style="{ color: '#165dff' }"
              show-group-separator
            >
              <template #prefix>
                <icon-sync />
              </template>
            </a-statistic>
          </a-col>
          <a-col :span="6">
            <a-statistic
              title="已完成"
              :value="48"
              :value-style="{ color: '#00b42a' }"
              show-group-separator
            >
              <template #prefix>
                <icon-check-circle />
              </template>
            </a-statistic>
          </a-col>
          <a-col :span="6">
            <a-statistic
              title="关闭率"
              :value="80"
              :precision="1"
              suffix="%"
              :value-style="{ color: '#722ed1' }"
            >
              <template #prefix>
                <icon-percentage />
              </template>
            </a-statistic>
          </a-col>
        </a-row>

        <!-- 模块说明 -->
        <a-card title="模块功能">
          <a-typography-paragraph>
            违规复核模块用于审查和处理系统检测到的违规事件，确保合规性要求得到满足。
          </a-typography-paragraph>
          <a-descriptions :column="2" bordered>
            <a-descriptions-item label="主要功能">
              事件审查、处理流程、结果反馈
            </a-descriptions-item>
            <a-descriptions-item label="处理周期">
              1-3个工作日
            </a-descriptions-item>
            <a-descriptions-item label="支持类型">
              安全违规、操作违规、数据违规
            </a-descriptions-item>
            <a-descriptions-item label="负责人">
              安全审计团队
            </a-descriptions-item>
          </a-descriptions>
        </a-card>
      </a-space>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// 待处理事项数据
const pendingItems = ref([
  {
    id: 1,
    title: '未授权访问尝试',
    description: '检测到来自未知IP的访问尝试',
    type: '安全违规',
    severity: '高危',
    severityColor: 'red',
    time: '2024-01-15 14:30'
  },
  {
    id: 2,
    title: '数据导出异常',
    description: '批量数据导出超出正常范围',
    type: '操作违规',
    severity: '中危',
    severityColor: 'orange',
    time: '2024-01-15 13:45'
  },
  {
    id: 3,
    title: '权限配置错误',
    description: '用户权限配置不符合最小权限原则',
    type: '配置违规',
    severity: '低危',
    severityColor: 'blue',
    time: '2024-01-15 12:20'
  }
])
</script>

<style scoped>
.violation-review-page {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.content-card {
  padding: 24px;
}
</style>