<template>
  <a-layout class="main-layout" :class="{ 'mini-layout': isMiniMode }">

    <!-- 顶部 Header（迷你模式完全隐藏） -->
    <a-layout-header v-if="!isMiniMode" class="header">
      <div class="header-left">
        <!-- 侧边栏折叠按钮 -->
        <button class="sidebar-toggle-btn" @click="sidebarCollapsed = !sidebarCollapsed" :title="sidebarCollapsed ? '展开菜单' : '收起菜单'">
          <icon-menu-fold v-if="!sidebarCollapsed" />
          <icon-menu-unfold v-else />
        </button>
        <div class="logo">
          <icon-computer :size="22" />
          <span class="logo-text">HuiInsight 徽鉴</span>
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
              <template #icon><icon-team /></template>人事权限
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
      <!-- 侧边栏（迷你模式完全隐藏，正常模式平滑折叠） -->
      <div
        v-if="!isMiniMode"
        class="sider-wrap"
        :class="{ 'sider-collapsed': sidebarCollapsed }"
      >
        <a-layout-sider
          class="sider"
          :width="220"
        >
          <a-menu
            :selected-keys="[currentMenu]"
            :default-open-keys="openMenus"
            :style="{ width: '100%', flex: 1 }"
            @menu-item-click="handleMenuClick"
          >
            <a-sub-menu key="dashboard-group">
              <template #icon><icon-dashboard /></template>
              <template #title>工作概览</template>
              <a-menu-item key="dashboard">
                <template #icon><icon-home /></template>概览主页
              </a-menu-item>
              <a-menu-item key="hr" v-if="permissionStore.can('view:settings')">
                <template #icon><icon-user-group /></template>人事权限
              </a-menu-item>
            </a-sub-menu>

            <a-sub-menu key="risk-audit">
              <template #icon><icon-shield /></template>
              <template #title>实时监看</template>
              <a-menu-item key="realtime">
                <template #icon><icon-radar-chart /></template>直播监测
              </a-menu-item>
              <a-menu-item key="violation-review">
                <template #icon><icon-file-search /></template>内容审核
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

            <a-menu-item key="supervisor/shadow-audit" v-if="permissionStore.can('view:shadow_audit')">
              <template #icon><icon-eye /></template>管理大屏
            </a-menu-item>
          </a-menu>

        </a-layout-sider>
      </div>

      <!-- 内容区：内层 div 为实际滚动容器，供回顶/去底导航绑定 -->
      <a-layout-content class="layout-content-root">
        <div
          id="main-layout-scroll"
          ref="contentScrollRef"
          class="content"
          @scroll.passive="updateScrollNav"
        >
          <div class="breadcrumb" v-if="showBreadcrumb && !isMiniMode && !sidebarCollapsed">
            <a-breadcrumb>
              <a-breadcrumb-item><icon-home /></a-breadcrumb-item>
              <a-breadcrumb-item v-for="item in breadcrumbItems" :key="item">
                {{ item }}
              </a-breadcrumb-item>
            </a-breadcrumb>
          </div>
          <div :class="['page-content', { 'page-content-mini': isMiniMode }]">
            <router-view />
          </div>
        </div>
      </a-layout-content>
    </a-layout>

    <!-- 长页面滚动快捷导航：Teleport 到 body，避免在主布局层叠上下文中误挡滚动/点击 -->
    <Teleport to="body">
      <div
        v-show="scrollNavEnabled"
        class="main-scroll-nav"
        :class="{ 'main-scroll-nav--mini': isMiniMode }"
        aria-label="页面滚动快捷操作"
      >
        <div class="main-scroll-nav__inner">
          <span class="main-scroll-nav__slot" title="回到顶部">
            <a-back-top
              target-container="#main-layout-scroll"
              :visible-height="200"
              :duration="480"
              easing="quartOut"
            />
          </span>
          <button
            v-if="showScrollToBottom"
            type="button"
            class="scroll-nav-fab"
            title="直达底部"
            aria-label="滚动到底部"
            @click="scrollContentToBottom"
          >
            <icon-to-bottom />
          </button>
        </div>
      </div>
    </Teleport>

    <!-- 全局底部状态栏（迷你模式下隐藏） -->
    <div v-if="!isMiniMode" class="global-statusbar">
      <div class="statusbar-left">
        <span class="statusbar-dot online"></span>
        <span class="statusbar-text">服务连接正常</span>
      </div>
      <div class="statusbar-right">
        <span class="statusbar-version">HuiInsight 徽鉴 · V1.0</span>
      </div>
    </div>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Message, Modal } from '@arco-design/web-vue'
import { auth } from '@/utils/auth'
import { usePermissionStore } from '@/stores/permission'
import { useWorkflowStore } from '@/stores/workflow'
import { isMiniMode } from '@/composables/useMiniMode'

const router          = useRouter()
const route           = useRoute()
const permissionStore = usePermissionStore()
const workflowStore   = useWorkflowStore()

const sidebarCollapsed = ref(false)

/** 主内容区滚动快捷导航（与 #main-layout-scroll 同步，不改变任何业务数据流） */
const contentScrollRef = ref<HTMLElement | null>(null)
const scrollNavEnabled = ref(false)
const showScrollToBottom = ref(false)
let contentResizeObserver: ResizeObserver | null = null

function onWindowResizeForScrollNav() {
  nextTick(updateScrollNav)
}

function updateScrollNav() {
  const el = contentScrollRef.value
  if (!el) return
  const { scrollTop, scrollHeight, clientHeight } = el
  const maxScroll = Math.max(0, scrollHeight - clientHeight)
  const threshold = 72
  scrollNavEnabled.value = maxScroll > threshold
  showScrollToBottom.value = maxScroll > threshold && scrollTop < maxScroll - threshold
}

function scrollContentToBottom() {
  const el = contentScrollRef.value
  if (!el) return
  el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' })
}

function bindScrollNavObservers() {
  const el = contentScrollRef.value
  if (!el) return
  contentResizeObserver = new ResizeObserver(() => {
    nextTick(updateScrollNav)
  })
  contentResizeObserver.observe(el)
  const pageInner = el.querySelector('.page-content')
  if (pageInner) contentResizeObserver.observe(pageInner)
  updateScrollNav()
}

function unbindScrollNavObservers() {
  contentResizeObserver?.disconnect()
  contentResizeObserver = null
}

watch(
  () => route.fullPath,
  () => nextTick(updateScrollNav),
)

interface StoredUser {
  username: string
  full_name: string
  role: string
  is_superuser: boolean
}

const userInfo = ref<StoredUser>({ username: '', full_name: '', role: '', is_superuser: false })

onMounted(() => {
  const stored = auth.getUserInfo() as StoredUser | null
  if (stored) userInfo.value = stored
  window.addEventListener('resize', onWindowResizeForScrollNav, { passive: true })
  nextTick(() => bindScrollNavObservers())
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onWindowResizeForScrollNav)
  unbindScrollNavObservers()
})

const userAvatar = computed(() =>
  (userInfo.value.full_name || userInfo.value.username || 'U').charAt(0).toUpperCase(),
)
const userName = computed(() => userInfo.value.full_name || userInfo.value.username || '用户')
const userRole = computed(() => permissionStore.roleLabel)

const breadcrumbMap: Record<string, string> = {
  dashboard: '工作概览', 'dashboard-group': '工作概览', hr: '人事权限',
  'risk-audit': '实时监看', realtime: '直播监测',
  'violation-review': '内容审核', sop: '审核标准', settings: '人事权限',
  supervisor: '主管', 'shadow-audit': '管理大屏', standards: '红线标准', rules: '业务规则',
}

const breadcrumbItems = computed(() =>
  route.path.split('/').filter(Boolean).map(seg => breadcrumbMap[seg] ?? seg),
)
const showBreadcrumb = computed(() => route.path !== '/dashboard')

const currentMenu = computed(() => {
  const map: Record<string, string> = {
    Dashboard: 'dashboard', RealTimePatrol: 'realtime', ViolationReview: 'violation-review',
    SOPStandards: 'standards', SOPRules: 'rules', Settings: 'hr',
    ShadowAuditDashboard: 'supervisor/shadow-audit',
  }
  return map[route.name as string] ?? 'dashboard'
})

const openMenus = computed(() => {
  const menus: string[] = []
  if (route.path.includes('risk-audit')) menus.push('risk-audit')
  if (route.path.includes('sop'))        menus.push('sop')
  if (route.path.includes('dashboard'))  menus.push('dashboard-group')
  return menus
})

const routeMap: Record<string, string> = {
  dashboard: '/dashboard', realtime: '/risk-audit/realtime',
  'violation-review': '/risk-audit/violation-review', standards: '/sop/standards',
  rules: '/sop/rules', hr: '/dashboard/hr',
  'supervisor/shadow-audit': '/supervisor/shadow-audit',
}

function handleMenuClick(key: string) {
  const path = routeMap[key]
  if (path) router.push(path)
}

function goToDashboard() { router.push('/dashboard') }
function viewProfile()   { Message.info('个人资料功能开发中') }
function viewSettings()  { router.push('/dashboard/hr') }

function showLogoutConfirm() {
  Modal.confirm({
    title: '确认退出登录', content: '您确定要退出当前账号吗？',
    okText: '确认退出', cancelText: '取消',
    onOk() {
      // 清空工作流相关的本地缓存，确保新账号进入是干净状态
      workflowStore.reset()
      workflowStore.clearPersist()
      localStorage.removeItem('blind_checker_state')
      localStorage.removeItem('blind_checker_log')
      auth.clearLoginData()
      permissionStore.clear()
      Message.success('已安全退出系统')
      router.push('/login')
    },
  })
}
</script>

<style scoped>
.main-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 内层为「侧栏 + 内容」横向排布，且必须 min-height:0，否则 flex 子项被内容撑开、主内容区无法出现独立滚动 */
.main-layout > .arco-layout {
  flex: 1;
  min-height: 0;
  min-width: 0;
  flex-direction: row;
  align-items: stretch;
  overflow: hidden;
}

/* ── Header ── */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 56px;
  background: var(--color-bg-2);
  border-bottom: 1px solid var(--color-border);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left { display: flex; align-items: center; gap: 12px; }

/* 侧边栏折叠按钮 */
.sidebar-toggle-btn {
  width: 32px; height: 32px;
  border: none; background: transparent;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  color: var(--color-text-2);
  font-size: 18px;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
  padding: 0; flex-shrink: 0;
}
.sidebar-toggle-btn:hover { background: var(--color-fill-3); color: var(--color-text-1); }

.logo {
  display: flex; align-items: center; gap: 10px;
  font-size: 16px; font-weight: 600;
  color: var(--color-text-1); white-space: nowrap;
}

.logo-text {
  background: linear-gradient(90deg, #165dff, #00b42a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-right { display: flex; align-items: center; }

.user-info {
  display: flex; align-items: center; gap: 10px;
  padding: 6px 12px; border-radius: 8px;
  cursor: pointer; transition: background 0.2s;
}
.user-info:hover { background: var(--color-fill-2); }
.user-details { display: flex; flex-direction: column; }
.user-name { font-weight: 500; font-size: 14px; color: var(--color-text-1); }
.user-role { font-size: 12px; margin-top: 2px; }
.dropdown-icon { color: var(--color-text-3); font-size: 12px; }

/* ── Sider ── */
.sider-wrap {
  /* 用 max-width + overflow:hidden 实现平滑的宽度折叠动画 */
  max-width: 220px;
  min-width: 220px;
  overflow: hidden;
  transition: max-width 0.28s cubic-bezier(0.4, 0, 0.2, 1),
              min-width 0.28s cubic-bezier(0.4, 0, 0.2, 1),
              opacity   0.22s ease;
  opacity: 1;
  flex-shrink: 0;
  /* 固定侧边栏高度，使其不随内容区滚动 */
  position: sticky;
  top: 0;
  height: calc(100vh - 56px - 26px);
  align-self: flex-start;
  overflow-y: auto;
}
.sider-wrap.sider-collapsed {
  max-width: 0;
  min-width: 0;
  opacity: 0;
}

.sider {
  width: 220px !important;
  background: var(--color-bg-2);
  border-right: 1px solid var(--color-border);
  display: flex; flex-direction: column;
  height: 100%;
  overflow-y: auto;
}

/* ── 全局底部状态栏 ── */
.global-statusbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 99;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 26px;
  padding: 0 16px;
  background: var(--color-bg-2);
  border-top: 1px solid var(--color-border);
}

.statusbar-left {
  display: flex;
  align-items: center;
  gap: 6px;
}

.statusbar-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}
.statusbar-dot.online { background: #00b42a; box-shadow: 0 0 4px rgba(0,180,42,0.6); }

.statusbar-text {
  font-size: 11px;
  color: var(--color-text-4);
}

.statusbar-version {
  font-size: 11px;
  color: var(--color-text-4);
  opacity: 0.7;
}

/* ── Content ── */
.layout-content-root {
  flex: 1;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  /* 与侧栏同高：在横向 flex 中由 align-items: stretch 拉满，不依赖 100vh 二次计算 */
  align-self: stretch;
}
.content {
  background: var(--color-bg-1);
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  scroll-behavior: smooth;
}
.breadcrumb { padding: 12px 24px 0; background: var(--color-bg-1); }
.page-content { padding: 24px 24px 50px; }
.page-content-mini { padding: 0; }

/* 迷你模式：无 header/sider，内容区单独占满视口高度 */
.mini-layout > .arco-layout {
  flex: 1;
  min-height: 0;
}
.mini-layout .content {
  flex: 1;
  min-height: 0;
  height: 100vh;
}

/* 悬浮滚动导航：固定一角、尺寸贴合按钮，绝不铺满视口 */
.main-scroll-nav {
  position: fixed;
  right: 20px;
  bottom: 42px;
  z-index: 100;
  width: fit-content;
  height: fit-content;
  max-width: 48px;
  pointer-events: none;
  margin: 0;
  padding: 0;
}
.main-scroll-nav--mini {
  bottom: 20px;
}
.main-scroll-nav__inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  pointer-events: none;
  width: fit-content;
}
.main-scroll-nav__inner :deep(.arco-back-top),
.main-scroll-nav__inner .scroll-nav-fab {
  pointer-events: auto;
}
.main-scroll-nav__slot {
  display: inline-flex;
  line-height: 0;
  width: 40px;
  min-height: 0;
}
/* 将 Arco BackTop 收进导航列，避免与自定义按钮错位 */
.main-scroll-nav :deep(.arco-back-top) {
  position: relative !important;
  right: auto !important;
  bottom: auto !important;
}
.main-scroll-nav :deep(.arco-back-top-btn) {
  width: 40px;
  height: 40px;
  background-color: rgba(var(--primary-6), 0.92);
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(6px);
}
.main-scroll-nav :deep(.arco-back-top-btn:hover) {
  background-color: rgb(var(--primary-5));
}
.scroll-nav-fab {
  width: 40px;
  height: 40px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-white);
  font-size: 14px;
  background-color: rgba(var(--primary-6), 0.55);
  border: 1px solid var(--color-border-2);
  border-radius: var(--border-radius-circle);
  cursor: pointer;
  outline: none;
  transition: background-color 0.2s cubic-bezier(0, 0, 1, 1), border-color 0.2s, transform 0.15s;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.28);
  backdrop-filter: blur(6px);
}
.scroll-nav-fab:hover {
  background-color: rgba(var(--primary-6), 0.85);
  border-color: rgb(var(--primary-6));
}
.scroll-nav-fab:active {
  transform: scale(0.96);
}

.logout-option { color: var(--color-danger) !important; }
</style>
