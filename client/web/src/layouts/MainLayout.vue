<template>
  <a-layout class="main-layout">
    <!-- 顶部 Header -->
    <a-layout-header class="header">
      <div class="header-left">
        <div class="logo">
          <icon-computer :size="22" />
          <span class="logo-text">AHDUNYI 风控审核中台</span>
        </div>
      </div>

      <div class="header-right">
        <a-dropdown trigger="click" position="br">
          <div class="user-info">
            <a-avatar :size="32" :style="{ backgroundColor: '#165dff' }">
              {{ userAvatar }}
            </a-avatar>
            <div class="user-details">
              <div class="user-name">{{ userName }}</div>
              <div class="user-role"><a-tag :color="permissionStore.roleColor" size="small">{{ userRole }}</a-tag></div>
            </div>
            <icon-down class="dropdown-icon" />
          </div>

          <template #content>
            <a-doption @click="goToDashboard">
              <template #icon><icon-dashboard /></template>工作台
            </a-doption>
            <a-doption @click="viewProfile">
              <template #icon><icon-user /></template>个人资料
            </a-doption>
            <a-doption v-if="permissionStore.can('view:settings')" @click="viewSettings">
              <template #icon><icon-settings /></template>系统管理
            </a-doption>
            <a-divider :margin="4" />
            <a-doption @click="showLogoutConfirm" class="logout-option">
              <template #icon><icon-logout /></template>退出登录
            </a-doption>
          </template>
        </a-dropdown>
      </div>
    </a-layout-header>

    <!-- 主体 -->
    <a-layout>
      <!-- 侧边栏 -->
      <a-layout-sider class="sider" :width="240">
        <a-menu
          :selected-keys="[currentMenu]"
          :default-open-keys="openMenus"
          :style="{ width: '100%', flex: 1 }"
          @menu-item-click="handleMenuClick"
        >
          <a-menu-item key="dashboard">
            <template #icon><icon-dashboard /></template>审核工作台
          </a-menu-item>

          <a-sub-menu key="risk-audit">
            <template #icon><icon-shield /></template>
            <template #title>风险审核</template>
            <a-menu-item key="realtime">
              <template #icon><icon-radar-chart /></template>实时监控
            </a-menu-item>
            <a-menu-item key="violation-review">
              <template #icon><icon-file-search /></template>违规审核
            </a-menu-item>
          </a-sub-menu>

          <a-sub-menu key="sop">
            <template #icon><icon-book /></template>
            <template #title>审核标准</template>
            <a-menu-item key="standards">
              <template #icon><icon-line-chart /></template>红线标准
            </a-menu-item>
            <a-menu-item key="rules">
              <template #icon><icon-unordered-list /></template>业务规则
            </a-menu-item>
          </a-sub-menu>

          <a-menu-item
            key="supervisor/shadow-audit"
            v-if="permissionStore.can('view:shadow_audit')"
          >
            <template #icon><icon-eye /></template>统帅大屏
          </a-menu-item>

          <a-menu-item key="settings" v-if="permissionStore.can('view:settings')">
            <template #icon><icon-settings /></template>系统管理
          </a-menu-item>
        </a-menu>

        <div class="sider-footer">
          <div class="system-status">
            <a-badge status="success" />
            <span class="status-text">系统运行正常</span>
          </div>
          <div class="version-info">
            <icon-tag :size="12" />
            <span>v9.0.0</span>
          </div>
        </div>
      </a-layout-sider>

      <!-- 内容区 -->
      <a-layout-content class="content">
        <div class="breadcrumb" v-if="showBreadcrumb">
          <a-breadcrumb>
            <a-breadcrumb-item><icon-home /></a-breadcrumb-item>
            <a-breadcrumb-item v-for="item in breadcrumbItems" :key="item">
              {{ item }}
            </a-breadcrumb-item>
          </a-breadcrumb>
        </div>
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
import { usePermissionStore } from '@/stores/permission'

const router          = useRouter()
const route           = useRoute()
const permissionStore = usePermissionStore()

// ---- 用户信息（从 auth 工具读取，已在 main.ts 水合） --------------------
interface StoredUser {
  username: string
  full_name: string
  role: string
  is_superuser: boolean
}

const userInfo = ref<StoredUser>({
  username:     '',
  full_name:    '',
  role:         '',
  is_superuser: false,
})

onMounted(() => {
  const stored = auth.getUserInfo() as StoredUser | null
  if (stored) userInfo.value = stored
})

// ---- 计算属性 -----------------------------------------------------------
const userAvatar = computed(() =>
  (userInfo.value.full_name || userInfo.value.username || 'U').charAt(0).toUpperCase(),
)
const userName = computed(() => userInfo.value.full_name || userInfo.value.username || '用户')
const userRole = computed(() => permissionStore.roleLabel)

const breadcrumbMap: Record<string, string> = {
  dashboard:        '工作台',
  'risk-audit':     '风险审核',
  realtime:         '实时监控',
  'violation-review': '违规审核',
  sop:              '审核标准',
  settings:         '系统管理',
  supervisor:       '主管',
  'shadow-audit':   '统帅大屏',
  standards:        '红线标准',
  rules:            '业务规则',
}

const breadcrumbItems = computed(() =>
  route.path.split('/').filter(Boolean).map(seg => breadcrumbMap[seg] ?? seg),
)
const showBreadcrumb = computed(() => route.path !== '/dashboard')

const currentMenu = computed(() => {
  const map: Record<string, string> = {
    Dashboard:            'dashboard',
    RealTimePatrol:       'realtime',
    ViolationReview:      'violation-review',
    SOPStandards:         'standards',
    SOPRules:             'rules',
    Settings:             'settings',
    ShadowAuditDashboard: 'supervisor/shadow-audit',
  }
  return map[route.name as string] ?? 'dashboard'
})

const openMenus = computed(() => {
  const menus: string[] = []
  if (route.path.includes('risk-audit')) menus.push('risk-audit')
  if (route.path.includes('sop'))        menus.push('sop')
  return menus
})

// ---- 菜单导航 -----------------------------------------------------------
const routeMap: Record<string, string> = {
  dashboard:               '/dashboard',
  realtime:                '/risk-audit/realtime',
  'violation-review':      '/risk-audit/violation-review',
  standards:               '/sop/standards',
  rules:                   '/sop/rules',
  settings:                '/settings',
  'supervisor/shadow-audit': '/supervisor/shadow-audit',
}

function handleMenuClick(key: string) {
  const path = routeMap[key]
  if (path) router.push(path)
}

// ---- 用户操作 -----------------------------------------------------------
function goToDashboard() { router.push('/dashboard') }
function viewProfile()   { Message.info('个人资料功能开发中') }
function viewSettings()  { router.push('/settings') }

function showLogoutConfirm() {
  Modal.confirm({
    title:      '确认退出登录',
    content:    '您确定要退出当前账号吗？',
    okText:     '确认退出',
    cancelText: '取消',
    onOk() {
      auth.clearLoginData()
      permissionStore.clear()
      Message.success('已安全退出系统')
      router.push('/login')
    },
  })
}
</script>

<style scoped>
.main-layout { min-height: 100vh; }

/* Header */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 64px;
  background: var(--color-bg-2);
  border-bottom: 1px solid var(--color-border);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 0;
  z-index: 100;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-1);
  white-space: nowrap;
}

.logo-text {
  background: linear-gradient(90deg, #165dff, #00b42a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-right { display: flex; align-items: center; }

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}
.user-info:hover { background: var(--color-fill-2); }

.user-details { display: flex; flex-direction: column; }
.user-name { font-weight: 500; font-size: 14px; color: var(--color-text-1); }
.user-role { font-size: 12px; margin-top: 2px; }
.dropdown-icon { color: var(--color-text-3); font-size: 12px; }

/* Sider */
.sider {
  background: var(--color-bg-2);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sider-footer {
  padding: 12px 16px;
  border-top: 1px solid var(--color-border);
  margin-top: auto;
}
.system-status { display: flex; align-items: center; gap: 6px; margin-bottom: 6px; }
.status-text { font-size: 12px; color: var(--color-text-3); }
.version-info { display: flex; align-items: center; gap: 4px; font-size: 12px; color: var(--color-text-3); }

/* Content */
.content {
  background: var(--color-bg-1);
  min-height: calc(100vh - 64px);
}

.breadcrumb {
  padding: 12px 24px 0;
  background: var(--color-bg-1);
}

.page-content { padding: 24px; }

.logout-option { color: var(--color-danger) !important; }
</style>
