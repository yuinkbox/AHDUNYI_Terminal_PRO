<template>
  <div class="dashboard-page">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <a-spin size="large">
        <div class="loading-content">
          <icon-loading />
          <div class="loading-text">正在加载用户角色...</div>
        </div>
      </a-spin>
    </div>
    
    <!-- 根据用户角色显示不同视图 -->
    <div v-else-if="userRole === 'auditor'">
      <AuditorView />
    </div>
    
    <div v-else-if="userRole === 'shift_leader'">
      <ShiftLeaderView />
    </div>
    
    <div v-else-if="userRole === 'supervisor'">
      <SupervisorView />
    </div>
    
    <div v-else>
      <a-alert type="warning" show-icon>
        <template #icon>
          <icon-exclamation-circle />
        </template>
        无法识别用户角色，请联系管理员
        <template #content>
          <div class="role-error-details">
            <p>可能的原因：</p>
            <ul>
              <li>用户信息未正确保存</li>
              <li>localStorage键名不匹配</li>
              <li>用户角色字段缺失</li>
            </ul>
            <div class="debug-info">
              <a-button size="small" type="outline" @click="showDebugInfo">
                显示调试信息
              </a-button>
            </div>
          </div>
        </template>
      </a-alert>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getUserRole, getUserRoleSync } from '@/api/rbac'
import AuditorView from './dashboard/AuditorView.vue'
import ShiftLeaderView from './dashboard/ShiftLeaderView.vue'
import SupervisorView from './dashboard/SupervisorView.vue'

const userRole = ref<string | null>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    // 优先使用异步版本
    const role = await getUserRole()
    userRole.value = role
    
    if (!role) {
      // 如果异步版本失败，尝试同步版本
      const syncRole = getUserRoleSync()
      userRole.value = syncRole
      
      if (!syncRole) {
        console.error('无法获取用户角色，检查localStorage:', {
          oldKey: localStorage.getItem('user_info'),
          newKey: localStorage.getItem('ahdunyi_user_info')
        })
      }
    }
  } catch (error) {
    console.error('获取用户角色失败:', error)
    // 最后尝试同步版本
    userRole.value = getUserRoleSync()
  } finally {
    loading.value = false
  }
})

// 调试函数
const showDebugInfo = () => {
  console.log('🔍 用户角色调试信息:', {
    userRole: userRole.value,
    localStorage: {
      old_user_info: localStorage.getItem('user_info'),
      new_user_info: localStorage.getItem('ahdunyi_user_info'),
      old_access_token: localStorage.getItem('access_token'),
      new_access_token: localStorage.getItem('ahdunyi_access_token')
    },
    authTool: '尝试导入 @/utils/auth'
  })
  
  alert(`用户角色: ${userRole.value || 'null'}
localStorage检查:
- user_info: ${localStorage.getItem('user_info') ? '存在' : '不存在'}
- ahdunyi_user_info: ${localStorage.getItem('ahdunyi_user_info') ? '存在' : '不存在'}
- access_token: ${localStorage.getItem('access_token') ? '存在' : '不存在'}
- ahdunyi_access_token: ${localStorage.getItem('ahdunyi_access_token') ? '存在' : '不存在'}

请检查控制台获取详细信息。`)
}
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

.role-error-details {
  margin-top: 8px;
  font-size: 13px;
  color: var(--color-text-2);
}

.role-error-details ul {
  margin: 8px 0;
  padding-left: 20px;
}

.role-error-details li {
  margin-bottom: 4px;
}

.debug-info {
  margin-top: 12px;
}
</style>
