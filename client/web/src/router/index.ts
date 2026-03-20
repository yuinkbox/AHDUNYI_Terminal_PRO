/**
 * 路由配置 - 严格鉴权版本
 */

import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { Message } from '@arco-design/web-vue'
import { auth } from '@/utils/auth' // ✅ 直接在顶部同步导入

import MainLayout from '@/layouts/MainLayout.vue'

const LoginPage = () => import('@/views/LoginPage.vue')
const DashboardPage = () => import('@/views/DashboardPage.vue')
const RealTimePatrolPage = () => import('@/views/RealTimePatrolPage.vue')
const ViolationReviewPage = () => import('@/views/ViolationReviewPage.vue')
const SOPPage = () => import('@/views/SOPPage.vue')
const SettingsPage = () => import('@/views/SettingsPage.vue')
const NotFoundPage = () => import('@/views/NotFoundPage.vue')
const ShadowAuditDashboard = () => import('@/views/supervisor/ShadowAuditDashboard.vue')

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/login' },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: { title: '登录', requiresAuth: false, hideLayout: true }
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
        meta: { title: '审核工作台', icon: 'icon-dashboard', menu: true, requiresAuth: true }
      },
      {
        path: 'risk-audit',
        name: 'RiskAudit',
        redirect: '/risk-audit/realtime',
        meta: { title: '风险审核', icon: 'icon-shield', menu: true, requiresAuth: true },
        children: [
          { path: 'realtime', name: 'RealTimePatrol', component: RealTimePatrolPage, meta: { title: '实时监控', requiresAuth: true } },
          { path: 'violation-review', name: 'ViolationReview', component: ViolationReviewPage, meta: { title: '违规审核', requiresAuth: true } }
        ]
      },
      {
        path: 'sop',
        name: 'SOP',
        redirect: '/sop/standards',
        meta: { title: '审核标准', icon: 'icon-book', menu: true, requiresAuth: true },
        children: [
          { path: 'standards', name: 'SOPStandards', component: SOPPage, meta: { title: '红线标准', requiresAuth: true } },
          { path: 'rules', name: 'SOPRules', component: () => import('@/views/SOPRulesPage.vue'), meta: { title: '业务规则', requiresAuth: true } }
        ]
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
          requiresSupervisor: true  // 新增：需要主管权限
        }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: SettingsPage,
        meta: { title: '系统管理', icon: 'icon-settings', menu: true, requiresAuth: true, requiresAdmin: true }
      }
    ]
  },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFoundPage, meta: { title: '页面未找到', hideLayout: true } }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior: (_to2, _from2, savedPosition) => savedPosition || { top: 0 }
})

// ✅ 移除所有花里胡哨的异步逻辑，回归最坚固的同步校验
router.beforeEach((to, _from, next) => {  // eslint-disable-line @typescript-eslint/no-unused-vars
  if (to.meta.title) document.title = `${to.meta.title} - AHDUNYI 巡查终端`

  const token = auth.getToken()
  const user = auth.getUserInfo()
  const isLoggedIn = !!(token && user)

  if (to.meta.requiresAuth) {
    if (!isLoggedIn) {
      if (to.path !== '/login') {
        Message.error('请先登录系统')
        next({ name: 'Login', query: { redirect: to.fullPath } })
        return
      }
      next()
      return
    }

    // 管理员权限验证保护
    if (to.meta.requiresAdmin && user.role !== 'supervisor') {
      Message.error('需要系统主管权限')
      next({ name: 'Dashboard' })
      return
    }
    
    // 主管权限验证保护（影子审计大屏）
    if (to.meta.requiresSupervisor && user.role !== 'supervisor') {
      Message.error('需要主管权限才能访问影子审计大屏')
      next({ name: 'Dashboard' })
      return
    }
  }

  // 拦截已登录用户重复访问登录页
  if (to.name === 'Login' && isLoggedIn) {
    next({ name: 'Dashboard' })
    return
  }

  next()
})

export default router