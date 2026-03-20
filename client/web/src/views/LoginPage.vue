<template>
  <div class="login-page">
    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="gradient-circle circle-1"></div>
      <div class="gradient-circle circle-2"></div>
      <div class="gradient-circle circle-3"></div>
    </div>

    <!-- 登录卡片 -->
    <a-card class="login-card" :bordered="false">
      <template #cover>
        <div class="card-header">
          <div class="logo">
            <icon-computer size="32" />
            <span class="logo-text">AHDUNYI</span>
          </div>
          <a-typography-title :level="3" class="welcome-text">
            AHDUNYI 审核工作台
          </a-typography-title>
          <a-typography-text type="secondary" class="subtitle">
            欢迎登录，请输入您的账号信息
          </a-typography-text>
        </div>
      </template>

      <div class="login-form">
        <!-- 用户名 -->
        <div class="form-item">
          <a-input
            v-model="username"
            placeholder="请输入用户名"
            size="large"
            allow-clear
            @keyup.enter="handleLogin"
          >
            <template #prefix><icon-user /></template>
          </a-input>
        </div>

        <!-- 密码 -->
        <div class="form-item">
          <a-input-password
            v-model="password"
            placeholder="请输入密码"
            size="large"
            allow-clear
            @keyup.enter="handleLogin"
          >
            <template #prefix><icon-lock /></template>
          </a-input-password>
        </div>

        <!-- 记住登录 -->
        <div class="form-item remember-item">
          <a-checkbox v-model="rememberMe">记住登录状态</a-checkbox>
          <a-link @click="showForgetPassword">忘记密码？</a-link>
        </div>

        <!-- 登录按钮 -->
        <a-button
          type="primary"
          size="large"
          long
          :loading="loginLoading"
          :disabled="!canLogin"
          @click="handleLogin"
          class="login-button"
        >
          <template #icon><icon-login v-if="!loginLoading" /></template>
          {{ loginLoading ? '登录中...' : '立即登录' }}
        </a-button>

        <!-- API 状态提示 -->
        <div v-if="apiStatus" class="api-status">
          <a-alert
            :type="apiStatus.type"
            :title="apiStatus.title"
            :content="apiStatus.content"
            show-icon
            closable
            @close="apiStatus = null"
          />
        </div>

        <!-- 后端连接状态 -->
        <div class="backend-status" v-if="!backendConnected">
          <a-alert type="warning" show-icon>
            <template #icon><icon-wifi /></template>
            后端服务未连接
            <template #content>
              请确保后端服务正在运行 ({{ apiBaseUrl }})
              <a-link @click="checkBackend"> 点击重试</a-link>
            </template>
          </a-alert>
        </div>

        <!-- 版本信息 -->
        <div class="version-info">
          <a-typography-text type="secondary">© 2026 AHDUNYI</a-typography-text>
        </div>
      </div>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Message } from '@arco-design/web-vue'
import api from '@/api'
import config from '@/config'
import { auth } from '@/utils/auth'
import { usePermissionStore } from '@/stores/permission'

const router = useRouter()
const route  = useRoute()
const permissionStore = usePermissionStore()

// ---- 响应式状态 ------------------------------------------------------------
const username        = ref('')
const password        = ref('')
const rememberMe      = ref(false)
const loginLoading    = ref(false)
const backendConnected = ref(true)
const apiBaseUrl      = config.api.baseUrl

interface ApiStatus {
  type: 'success' | 'warning' | 'error' | 'info'
  title: string
  content: string
}
const apiStatus = ref<ApiStatus | null>(null)

// ---- 计算属性 --------------------------------------------------------------
const canLogin = computed(() => username.value.trim().length > 0 && password.value.length >= 6)

// ---- 生命周期 --------------------------------------------------------------
onMounted(() => {
  document.title = 'AHDUNYI 巡查终端 - 登录'
  loadRememberedAccount()
  checkBackend()
})

// ---- 方法 ------------------------------------------------------------------

/** 检查后端连接 */
async function checkBackend() {
  try {
    const res = await api.system.healthCheck()
    backendConnected.value = res.status === 'healthy' || res.status === 'ok'
  } catch {
    backendConnected.value = false
  }
}

/** 从 localStorage 恢复记住的账号 */
function loadRememberedAccount() {
  const lastUsername = auth.getLastUsername()
  if (lastUsername) {
    username.value  = lastUsername
    rememberMe.value = true
  }
}

/** 核心登录逻辑 */
async function handleLogin() {
  if (!canLogin.value) return
  loginLoading.value = true

  try {
    const loginData = await api.auth.login(username.value, password.value)

    // 1. 持久化 Token 和用户信息
    auth.saveLoginData(
      loginData.access_token,
      loginData.user,
      rememberMe.value,
      username.value,
    )

    // 2. 水合权限 Store（前端零角色硬编码的核心步骤）
    permissionStore.bootstrap({
      role:       loginData.user.role,
      permissions: loginData.permissions  ?? [],
      role_meta:  loginData.role_meta ?? {
        label:          loginData.user.role,
        color:          'gray',
        dashboard_view: 'auditor',
      },
    })

    Message.success(`欢迎回来，${loginData.user.full_name}`)
    password.value = ''

    // 3. 跳转
    const redirect = route.query.redirect as string
    setTimeout(() => {
      router.push(redirect || '/dashboard')
    }, 500)

  } catch (error: any) {
    password.value = ''
    const status = error?.response?.status
    const detail = error?.response?.data?.detail

    if (status === 401) {
      Message.error('账号或密码错误')
      apiStatus.value = { type: 'error', title: '认证失败', content: detail || '用户名或密码不正确' }
    } else if (status === 403) {
      Message.error('账户已被禁用')
      apiStatus.value = { type: 'warning', title: '账户禁用', content: '请联系管理员激活账户' }
    } else if (!error?.response) {
      Message.error('无法连接到后端服务')
      apiStatus.value = { type: 'error', title: '连接失败', content: `请确保后端正在运行 (${apiBaseUrl})` }
      backendConnected.value = false
    } else {
      Message.error('登录失败，请稍后重试')
      apiStatus.value = { type: 'error', title: '服务器错误', content: detail || '未知错误' }
    }
  } finally {
    loginLoading.value = false
  }
}

function showForgetPassword() {
  Message.info('请联系系统管理员重置密码')
}
</script>

<style scoped>
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 24px;
  position: relative;
  overflow: hidden;
  background: #0d0d0d;
}

.background-decoration {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

.gradient-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.12;
}

.circle-1 {
  width: 480px;
  height: 480px;
  background: radial-gradient(circle, #165dff, #00b42a);
  top: -240px;
  right: -240px;
}

.circle-2 {
  width: 360px;
  height: 360px;
  background: radial-gradient(circle, #ff7d00, #f53f3f);
  bottom: -180px;
  left: -180px;
}

.circle-3 {
  width: 240px;
  height: 240px;
  background: radial-gradient(circle, #722ed1, #eb2f96);
  top: 50%;
  left: 8%;
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.4);
  z-index: 1;
  transition: box-shadow 0.3s;
}

.login-card:hover {
  box-shadow: 0 12px 56px rgba(0, 0, 0, 0.5);
}

.card-header {
  text-align: center;
  padding: 36px 24px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 16px;
}

.logo-text {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 2px;
  background: linear-gradient(135deg, #165dff 0%, #00b42a 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-text { margin: 0; }
.subtitle { display: block; margin-top: 8px; }

.login-form { padding: 32px 24px; }

.form-item { margin-bottom: 20px; }

.remember-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
}

.login-button {
  height: 48px;
  font-size: 16px;
  font-weight: 500;
}

.api-status,
.backend-status { margin-top: 16px; }

.version-info {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  text-align: center;
}

@media (max-width: 480px) {
  .login-page { padding: 16px; }
  .login-card { max-width: 100%; }
  .card-header { padding: 24px 16px 16px; }
  .login-form { padding: 24px 16px; }
}
</style>
