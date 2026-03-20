<template>
  <a-layout class="main-layout">
    <!-- 顶部 Header -->
    <a-layout-header class="header">
      <div class="header-left">
        <div class="logo">
          <icon-terminal size="24" />
          <span class="logo-text">AHDUNYI 风控审核中台</span>
        </div>
      </div>
      
      <div class="header-right">
        <!-- 用户信息 -->
        <a-dropdown trigger="click" position="br">
          <div class="user-info">
            <a-avatar :size="32" :style="{ backgroundColor: userColor }">
              {{ userAvatar }}
            </a-avatar>
            <div class="user-details">
              <div class="user-name">{{ userName }}</div>
              <div class="user-role">{{ userRole }}</div>
            </div>
            <icon-down class="dropdown-icon" />
          </div>
          
          <template #content>
            <a-doption @click="goToDashboard">
              <template #icon>
                <icon-dashboard />
              </template>
              工作台
            </a-doption>
            <a-doption @click="viewProfile">
              <template #icon>
                <icon-user />
              </template>
              个人资料
            </a-doption>
            <a-doption @click="viewSettings">
              <template #icon>
                <icon-settings />
              </template>
              系统管理
            </a-doption>
            <a-doption @click="showLogoutConfirm" class="logout-option">
              <template #icon>
                <icon-logout />
              </template>
              退出登录
            </a-doption>
          </template>
        </a-dropdown>
      </div>
    </a-layout-header>

    <!-- 主体布局 -->
    <a-layout>
      <!-- 左侧菜单 -->
      <a-layout-sider class="sider" :width="240">
        <a-menu
          :default-selected-keys="[currentMenu]"
          :default-open-keys="openMenus"
          :style="{ width: '100%' }"
          @menu-item-click="handleMenuClick"
        >
          <!-- 工作台 -->
          <a-menu-item key="dashboard">
            <template #icon>
              <icon-dashboard />
            </template>
            审核工作台
          </a-menu-item>
          
          <!-- 风险审查 -->
          <a-sub-menu key="risk-audit">
            <template #icon>
              <icon-shield />
            </template>
            <template #title>风险审核</template>
            <a-menu-item key="realtime">
              <template #icon>
                <icon-radar-chart />
              </template>
              实时监控
            </a-menu-item>
            <a-menu-item key="violation-review">
              <template #icon>
                <icon-file-search />
              </template>
              违规审核
            </a-menu-item>
          </a-sub-menu>
          
          <!-- 标准中心 -->
          <a-sub-menu key="sop">
            <template #icon>
              <icon-book />
            </template>
            <template #title>审核标准</template>
            <a-menu-item key="standards">
              <template #icon>
                <icon-line-chart />
              </template>
              红线标准
            </a-menu-item>
            <a-menu-item key="rules">
              <template #icon>
                <icon-settings />
              </template>
              业务规则
            </a-menu-item>
          </a-sub-menu>
          
          <!-- 影子审计大屏（仅主管可见） -->
          <a-menu-item 
            key="supervisor/shadow-audit" 
            v-if="userInfo.role === 'supervisor'"
            route="/supervisor/shadow-audit"
          >
            <template #icon>
              <icon-eye />
            </template>
            👁️ 统帅大屏
          </a-menu-item>
          
          <!-- 系统管理 -->
          <a-menu-item key="settings" v-if="isAdmin">
            <template #icon>
              <icon-settings />
            </template>
            系统管理
          </a-menu-item>
        </a-menu>
        
        <!-- 底部系统信息 -->
        <div class="sider-footer">
          <div class="system-status">
            <a-tag color="green" size="small">在线</a-tag>
            <span class="status-text">审核系统运行正常</span>
          </div>
          <div class="version-info">
            <icon-tag size="12" />
            <span>v1.0.0</span>
          </div>
        </div>
      </a-layout-sider>

      <!-- 主要内容区域 -->
      <a-layout-content class="content">
        <!-- 面包屑导航 -->
        <div class="breadcrumb" v-if="showBreadcrumb">
          <a-breadcrumb>
            <a-breadcrumb-item>
              <icon-home />
            </a-breadcrumb-item>
            <a-breadcrumb-item v-for="item in breadcrumbItems" :key="item">
              {{ item }}
            </a-breadcrumb-item>
          </a-breadcrumb>
        </div>
        
        <!-- 页面内容 -->
        <div class="page-content">
          <router-view />
        </div>
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Message, Modal } from '@arco-design/web-vue'
import { auth } from '@/utils/auth'

const router = useRouter()
const route = useRoute()

// 用户信息
const userInfo = ref<{
  username: string
  full_name: string
  email: string
  is_admin: boolean
  role?: string
}>({
  username: 'admin',
  full_name: '系统管理员',
  email: 'admin@ahdunyi.com',
  is_admin: true,
  role: ''
})

// 计算属性
const userAvatar = computed(() => userInfo.value.username.charAt(0).toUpperCase())
const userColor = computed(() => '#165dff')
const userName = computed(() => userInfo.value.full_name)
const userRole = computed(() => {
  if (userInfo.value.role === 'supervisor') return '主管'
  if (userInfo.value.role === 'shift_leader') return '组长'
  if (userInfo.value.role === 'auditor') return '审核员'
  return userInfo.value.is_admin ? '管理员' : '审核员'
})
const isAdmin = computed(() => userInfo.value.is_admin || userInfo.value.role === 'supervisor')

// 面包屑
const breadcrumbItems = computed(() => {
  const path = route.path.split('/').filter(Boolean)
  return path.map(item => {
    // 简单的路径转中文
    const map: Record<string, string> = {
      'dashboard': '工作台',
      'risk-audit': '风险审核',
      'realtime': '实时监控',
      'violation-review': '违规审核',
      'sop': '审核标准',
      'settings': '系统管理',
      'supervisor': '主管',
      'shadow-audit': '统帅大屏'
    }
    return map[item] || item
  })
})

const showBreadcrumb = computed(() => route.path !== '/dashboard')
const currentMenu = computed(() => {
  // 路由名称到菜单key的映射
  const routeToMenuMap: Record<string, string> = {
    'Dashboard': 'dashboard',
    'RealTimePatrol': 'realtime',
    'ViolationReview': 'violation-review',
    'SOPStandards': 'standards',
    'SOPRules': 'rules',
    'Settings': 'settings',
    'ShadowAuditDashboard': 'supervisor/shadow-audit'
  }
  
  return routeToMenuMap[route.name as string] || 'dashboard'
})
const openMenus = computed(() => {
  const menus: string[] = []
  if (route.path.includes('risk-audit')) menus.push('risk-audit')
  if (route.path.includes('sop')) menus.push('sop')
  return menus
})

// 生命周期
onMounted(async () => {
  // 从本地存储加载用户信息（优先使用新键名）
  let storedUser = localStorage.getItem('ahdunyi_user_info')
  if (!storedUser) {
    // 降级处理：使用旧键名
    storedUser = localStorage.getItem('user_info')
  }
  
  if (storedUser) {
    try {
      userInfo.value = JSON.parse(storedUser)
    } catch (error) {
      console.error('加载用户信息失败:', error)
    }
  }
  
  // 如果还是没找到，尝试使用auth工具
  if (!userInfo.value) {
    try {
      const { auth } = await import('@/utils/auth')
      const user = auth.getUserInfo()
      if (user) {
        userInfo.value = user
      }
    } catch (error) {
      console.warn('使用auth工具失败:', error)
    }
  }
})

// 菜单点击处理
const handleMenuClick = (key: string) => {
  const routeMap: Record<string, string> = {
    'dashboard': '/dashboard',
    'realtime': '/risk-audit/realtime',
    'violation-review': '/risk-audit/violation-review',
    'standards': '/sop/standards',
    'rules': '/sop/rules',
    'settings': '/settings',
    'supervisor/shadow-audit': '/supervisor/shadow-audit'  // 新增：影子审计路由
  }
  
  if (routeMap[key]) {
    router.push(routeMap[key])
  }
}

// 用户操作
const goToDashboard = () => {
  router.push('/dashboard')
}

const viewProfile = () => {
  Message.info('个人资料功能开发中')
}

const viewSettings = () => {
  router.push('/settings')
}

const showLogoutConfirm = () => {
   Modal.confirm({
    title: '确认退出登录',
    content: '您确定要退出当前账号吗？',
    okText: '确认退出',
    cancelText: '取消',
    onOk: () => {
      // 🚀 调用刚才重构的 auth 工具，执行真正的“焦土政策”清理！
      auth.clearLoginData()
      
      Message.success('已安全退出系统')
      router.push('/login')
    }
  })
}
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
}

/* Header 样式 */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 64px;
  background: var(--color-bg-2);
  border-bottom: 1px solid var(--color-border);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-1);
}

.logo-text {
  white-space: nowrap;
}

/* 右侧用户信息 */
.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.user-info:hover {
  background: var(--color-bg-3);
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 500;
  color: var(--color-text-1);
}

.user-role {
  font-size: 12px;
  color: var(--color-text-3);
}

.dropdown-icon {
  color: var(--color-text-3);
  font-size: 12px;
}

/* Sider 样式 */
.sider {
  background: var(--color-bg-2);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
}

.sider-footer {
  margin-top: auto;
  padding: 16px;
  border-top: 1px solid var(--color-border);
}

.system-status {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.version-info {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--color-text-3);
}

/* Content 样式 */
.content {
  padding: 24px;
  background: var(--color-bg-1);
  overflow-y: auto;
}

.breadcrumb {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border);
}

.page-content {
  background: var(--color-bg-2);
  border-radius: 8px;
  padding: 24px;
  min-height: calc(100vh - 180px);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .header {
    padding: 0 16px;
  }
  
  .logo-text {
    display: none;
  }
}
</style>