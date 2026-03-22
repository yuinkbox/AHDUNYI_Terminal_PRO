<template>
  <div class="dashboard-page">
    <!-- 权限驱动的视图路由 -->
    <!-- dashboardView 由后端 role_meta.dashboard_view 决定，前端零硬编码 -->
    <!-- 如果权限 Store 未水合，使用默认视图（AuditorView） -->
    <template v-if="!permissionStore.hydrated">
      <!-- 加载状态：等待权限 Store 水合 -->
      <div class="loading-state">
        <a-spin size="large">
          <div class="loading-content">
            <icon-loading />
            <div class="loading-text">正在加载权限信息...</div>
          </div>
        </a-spin>
      </div>
    </template>
    <template v-else>
      <SupervisorView   v-if="permissionStore.dashboardView === 'supervisor'" />
      <ShiftLeaderView  v-else-if="permissionStore.dashboardView === 'leader'" />
      <AuditorView      v-else />
    </template>
  </div>
</template>

<script setup lang="ts">
import { usePermissionStore } from '@/stores/permission'
import AuditorView    from './dashboard/AuditorView.vue'
import ShiftLeaderView from './dashboard/ShiftLeaderView.vue'
import SupervisorView  from './dashboard/SupervisorView.vue'

const permissionStore = usePermissionStore()
</script>

<style scoped>
.dashboard-page {
  padding: 0;
  min-height: 100vh;
}

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.loading-text {
  color: var(--color-text-2);
  font-size: 14px;
}
</style>
