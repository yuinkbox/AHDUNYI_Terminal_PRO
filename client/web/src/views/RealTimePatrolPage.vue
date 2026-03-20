<template>
  <div class="real-time-patrol-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <a-space direction="vertical" :size="8">
        <a-typography-title :level="2">
          📡 实时巡查
        </a-typography-title>
        <a-typography-text type="secondary">
          实时监控与异常行为检测
        </a-typography-text>
      </a-space>
    </div>

    <!-- 页面内容 -->
    <a-card class="content-card">
      <a-space direction="vertical" :size="24">
        <!-- 状态指示 -->
        <a-alert type="success" show-icon>
          <template #icon>
            <icon-check-circle />
          </template>
          实时巡查系统运行正常，监控覆盖率达到 98.7%
        </a-alert>

        <!-- 监控面板 -->
        <a-row :gutter="16">
          <a-col :span="12">
            <a-card title="监控概览" :bordered="false">
              <a-statistic
                title="活跃监控点"
                :value="156"
                :precision="0"
                :value-style="{ color: '#165dff' }"
              >
                <template #prefix>
                  <icon-eye />
                </template>
              </a-statistic>
              <a-statistic
                title="今日告警"
                :value="8"
                :precision="0"
                :value-style="{ color: '#ff7d00' }"
                style="margin-top: 16px"
              >
                <template #prefix>
                  <icon-alert />
                </template>
              </a-statistic>
            </a-card>
          </a-col>
          <a-col :span="12">
            <a-card title="系统状态" :bordered="false">
              <a-space direction="vertical" :size="12">
                <a-progress
                  :percent="92"
                  :stroke-width="8"
                  status="success"
                  :show-text="false"
                >
                  <template #label>
                    <span>CPU 使用率: 92%</span>
                  </template>
                </a-progress>
                <a-progress
                  :percent="78"
                  :stroke-width="8"
                  status="normal"
                  :show-text="false"
                >
                  <template #label>
                    <span>内存使用率: 78%</span>
                  </template>
                </a-progress>
                <a-progress
                  :percent="45"
                  :stroke-width="8"
                  status="normal"
                  :show-text="false"
                >
                  <template #label>
                    <span>网络带宽: 45%</span>
                  </template>
                </a-progress>
              </a-space>
            </a-card>
          </a-col>
        </a-row>

        <!-- 功能说明 -->
        <a-card title="功能说明">
          <a-typography-paragraph>
            实时巡查模块负责监控系统运行状态，检测异常行为，并及时发出告警。
          </a-typography-paragraph>
          <a-typography-paragraph>
            主要功能包括：
          </a-typography-paragraph>
          <ul>
            <li>实时数据流监控</li>
            <li>异常行为模式识别</li>
            <li>自动告警与通知</li>
            <li>监控报表生成</li>
          </ul>
        </a-card>
      </a-space>
    </a-card>
  </div>
</template>

<script setup lang="ts">
// 实时巡查页面
</script>

<style scoped>
.real-time-patrol-page {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.content-card {
  padding: 24px;
}
</style>