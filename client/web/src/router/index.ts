/**
 * 路由配置 - 权限点驱动版本
 *
 * 路由守卫不再硬编码角色名。每条需要特殊权限的路由在 meta 中
 * 声明所需的权限点字符串（如 "view:shadow_audit"），守卫统一
 * 调用 permissionStore.can(permission) 进行校验。
 *
 * 新增角色或调整权限：只需修改后端 permissions.py，前端零改动。
 */

import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { Message } from '@arco-design/web-vue'
import { auth } from '@/utils/auth'
import { usePermissionStore } from '@/stores/permission'
import { isDesktopMode } from '@/bridge/qt_channel'

import MainLayout from '@/layouts/MainLayout.vue'

const LoginPage            = () => import('@/views/LoginPage.vue')
const DashboardPage        = () => import('@/views/DashboardPage.vue')
const RealTimePatrolPage   = () => import('@/views/RealTimePatrolPage.vue')
const ViolationReviewPage  = () => import('@/views/ViolationReviewPage.vue')
const SOPPage              = () => import('@/views/SOPPage.vue')
const SettingsPage         = () => import('@/views/SettingsPage.vue')
const NotFoundPage         = () => import('@/views/NotFoundPage.vue')
const ShadowAuditDashboard = () => import('@/views/supervisor/ShadowAuditDashboard.vue')

// ---------------------------------------------------------------------------
// Route table
// meta.permission  — if set, user must hold this permission point
// meta.requiresAuth — if true, user must be logged in
// ---------------------------------------------------------------------------
const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/login' },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: { title: '登录', requiresAuth: false, hideLayout: true },
  },
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: DashboardPage,
        meta: {
          title: '审核工作台',
          icon: 'icon-dashboard',
          menu: true,
          requiresAuth: true,
          permission: 'view:dashboard',
        },
      },
      {
        path: 'risk-audit',
        name: 'RiskAudit',
        redirect: '/risk-audit/realtime',
        meta: { title: '风险审核', icon: 'icon-shield', menu: true, requiresAuth: true },
        children: [
          {
            path: 'realtime',
            name: 'RealTimePatrol',
            component: RealTimePatrolPage,
            meta: { title: '实时监控', requiresAuth: true, permission: 'view:realtime' },
          },
          {
            path: 'violation-review',
            name: 'ViolationReview',
            component: ViolationReviewPage,
            meta: { title: '违规审核', requiresAuth: true, permission: 'view:violations' },
          },
        ],
      },
      {
        path: 'sop',
        name: 'SOP',
        redirect: '/sop/standards',
        meta: { title: '审核标准', icon: 'icon-book', menu: true, requiresAuth: true },
        children: [
          {
            path: 'standards',
            name: 'SOPStandards',
            component: SOPPage,
            meta: { title: '红线标准', requiresAuth: true, permission: 'view:sop' },
          },
          {
            path: 'rules',
            name: 'SOPRules',
            component: () => import('@/views/SOPRulesPage.vue'),
            meta: { title: '业务规则', requiresAuth: true, permission: 'view:sop' },
          },
        ],
      },
      {
        path: 'supervisor/shadow-audit',
        name: 'ShadowAuditDashboard',
        component: ShadowAuditDashboard,
        meta: {
          title: '统帅大屏',
          icon: 'icon-eye',
          menu: true,
          requiresAuth: true,
          permission: 'view:shadow_audit',   // only manager in matrix
        },
      },
      {
        path: 'settings',
        name: 'Settings',
        component: SettingsPage,
        meta: {
          title: '系统管理',
          icon: 'icon-settings',
          menu: true,
          requiresAuth: true,
          permission: 'view:settings',
        },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFoundPage,
    meta: { title: '页面未找到', hideLayout: true },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior: (_to, _from, savedPosition) => savedPosition || { top: 0 },
})

// ---------------------------------------------------------------------------
// Navigation guard — permission-point driven, role-agnostic
// ---------------------------------------------------------------------------
router.beforeEach((to, _from, next) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} - AHDUNYI 巡查终端`
  }

  // Desktop (PyQt6) mode: authentication is handled by the native Python
  // LoginWindow. The token is injected into localStorage via runJavaScript
  // AFTER the page loads. Skip all auth/permission guards and let the
  // page components handle token-readiness via the ahdunyi:token-ready event.
  if (isDesktopMode()) {
    // Only block routes that explicitly require a permission (not just auth)
    // and only after the permission store is hydrated.
    if (to.name === 'Login') {
      // In desktop mode never show the Vue login page — go to dashboard
      next({ name: 'Dashboard' })
      return
    }
    next()
    return
  }

  const token      = auth.getToken()
  const user       = auth.getUserInfo()
  const isLoggedIn = !!(token && user)

  // -- Auth check ----------------------------------------------------------
  if (to.meta.requiresAuth && !isLoggedIn) {
    if (to.path !== '/login') {
      Message.error('请先登录系统')
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
    next()
    return
  }

  // -- Permission check ----------------------------------------------------
  if (to.meta.permission && isLoggedIn) {
    const permissionStore = usePermissionStore()
    if (permissionStore.hydrated && !permissionStore.can(to.meta.permission as string)) {
      Message.error('您没有访问该页面的权限')
      next({ name: 'Dashboard' })
      return
    }
    // If store not yet hydrated (first load), let the page through;
    // the component itself can do a secondary guard via can() in template.
  }

  // -- Redirect logged-in users away from login ----------------------------
  if (to.name === 'Login' && isLoggedIn) {
    next({ name: 'Dashboard' })
    return
  }

  next()
})

export default router
