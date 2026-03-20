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
      <!-- 卡片头部 -->
      <template #cover>
        <div class="card-header">
          <div class="logo">
            <icon-terminal size="32" />
            <span class="logo-text">AHDUNYI</span>
          </div>
          <a-typography-title :level="3" class="welcome-text">
            AHDUNYI 审核工作台
          </a-typography-title>
          <a-typography-text type="secondary" class="subtitle">
            欢迎登录 AHDUNYI
          </a-typography-text>
        </div>
      </template>
      
      <!-- 登录表单 -->
      <div class="login-form">
        <!-- 用户名输入 -->
        <div class="form-item">
          <a-typography-text strong class="form-label">
            <icon-user />
            用户名
          </a-typography-text>
          <a-input
            v-model="username"
            placeholder="请输入用户名"
            size="large"
            :style="{ width: '100%' }"
            allow-clear
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <icon-user />
            </template>
          </a-input>
        </div>
        
        <!-- 密码输入 -->
        <div class="form-item">
          <a-typography-text strong class="form-label">
            <icon-lock />
            密码
          </a-typography-text>
          <a-input-password
            v-model="password"
            placeholder="请输入密码"
            size="large"
            :style="{ width: '100%' }"
            allow-clear
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <icon-lock />
            </template>
          </a-input-password>
        </div>
        
        <!-- RBAC测试快捷方式 -->
        <div class="form-item quick-login-section">
          <a-typography-text type="secondary" class="quick-login-label">
            <icon-thunderbolt />
            测试快捷登录
          </a-typography-text>
          <div class="quick-login-buttons">
            <a-button 
              size="small" 
              type="outline" 
              status="danger"
              @click="quickLogin('supervisor')"
              :disabled="loginLoading"
            >
              <icon-crown />
              主管登入
            </a-button>
            <a-button 
              size="small" 
              type="outline" 
              status="warning"
              @click="quickLogin('leader_morning')"
              :disabled="loginLoading"
            >
              <icon-team />
              组长登入
            </a-button>
            <a-button 
              size="small" 
              type="outline" 
              status="success"
              @click="quickLogin('auditor_001')"
              :disabled="loginLoading"
            >
              <icon-user-group />
              审核员登入
            </a-button>
          </div>
          <div class="quick-login-hint">
            密码统一为: <code>123456</code>
          </div>
        </div>
        
        <!-- 记住登录 -->
        <div class="form-item remember-item">
          <a-checkbox v-model="rememberMe">
            记住登录状态
          </a-checkbox>
          <a-link @click="showForgetPassword">
            忘记密码？
          </a-link>
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
          <template #icon>
            <icon-login v-if="!loginLoading" />
          </template>
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
        <div class="backend-status">
          <a-alert 
            v-if="!backendConnected"
            type="warning"
            show-icon
            closable
            @close="hideBackendWarning"
          >
            <template #icon>
              <icon-wifi />
            </template>
            后端服务未连接
            <template #content>
              请确保 AHDUNYI 后端服务正在运行 (http://106.15.32.246:8000)
              <a-link @click="checkBackend">点击重试</a-link>
            </template>
          </a-alert>
        </div>
        
        <!-- 版本信息 -->
        <div class="version-info">
          <a-typography-text type="secondary">
            © 2026 AHDUNYI
          </a-typography-text>
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

// 路由相关
const router = useRouter()
const route = useRoute()

// 响应式数据
const username = ref<string>('')
const password = ref('')
const rememberMe = ref(false)
const loginLoading = ref(false)
const backendConnected = ref(true)

// API 状态
interface ApiStatus {
  type: 'success' | 'warning' | 'error' | 'info'
  title: string
  content: string
}

const apiStatus = ref<ApiStatus | null>(null)

// RBAC测试账户配置
const rbacTestAccounts = {
  supervisor: {
    username: 'supervisor',
    password: '123456',
    label: '系统主管',
    role: 'supervisor'
  },
  leader_morning: {
    username: 'leader_morning',
    password: '123456',
    label: '早班组长',
    role: 'shift_leader'
  },
  leader_afternoon: {
    username: 'leader_afternoon',
    password: '123456',
    label: '中班组长',
    role: 'shift_leader'
  },
  auditor_001: {
    username: 'auditor_001',
    password: '123456',
    label: '审核员001',
    role: 'auditor'
  },
  auditor_002: {
    username: 'auditor_002',
    password: '123456',
    label: '审核员002',
    role: 'auditor'
  },
  auditor_003: {
    username: 'auditor_003',
    password: '123456',
    label: '审核员003',
    role: 'auditor'
  },
  auditor_004: {
    username: 'auditor_004',
    password: '123456',
    label: '审核员004',
    role: 'auditor'
  }
}

// 计算属性
const canLogin = computed(() => {
  return username.value.trim() && password.value.length >= 6
})

// 生命周期
onMounted(() => {
  console.log('🔐 RBAC登录页面已加载')
  document.title = 'AHDUNYI RBAC巡查终端 - 登录'
  
  // 检查是否有重定向参数
  const redirect = route.query.redirect as string
  if (redirect) {
    console.log('检测到重定向:', redirect)
  }
  
  // 加载记住的账户
  loadRememberedAccount()
  
  // 检查后端连接
  checkBackend()
})

// 检查后端连接
const checkBackend = async () => {
  try {
    const response = await api.system.healthCheck()
    if (response.status === 'healthy') {
      backendConnected.value = true
      console.log('✅ 后端服务连接正常')
    } else {
      backendConnected.value = false
      console.warn('⚠️ 后端服务状态异常')
    }
  } catch (error) {
    backendConnected.value = false
    console.error('❌ 后端服务连接失败:', error)
  }
}

const hideBackendWarning = () => {
  backendConnected.value = true
}

// 加载记住的账户
const loadRememberedAccount = () => {
  import('@/utils/auth').then(({ auth }) => {
    const lastUsername = auth.getLastUsername()
    if (lastUsername) {
      username.value = lastUsername
      rememberMe.value = true
    }
  }).catch(error => {
    console.error('加载auth工具失败:', error)
    // 降级处理
    const lastUsername = localStorage.getItem('lastUsername')
    if (lastUsername) {
      username.value = lastUsername
      rememberMe.value = true
    }
  })
}

// 快捷登录
const quickLogin = (accountType: keyof typeof rbacTestAccounts) => {
  const account = rbacTestAccounts[accountType]
  if (!account) return
  
  username.value = account.username
  password.value = account.password
  
  Message.info({
    content: `已选择${account.label}账户`,
    duration: 2000
  })
  
  // 自动聚焦到登录按钮
  setTimeout(() => {
    const loginButton = document.querySelector('.login-button') as HTMLElement
    if (loginButton) {
      loginButton.focus()
    }
  }, 100)
}

// 核心登录函数 - 调用真实后端API
const handleLogin = async () => {
  if (!canLogin.value) return
  
  loginLoading.value = true
  
  try {
    console.log('🔐 正在登录...', {
      username: username.value,
      passwordLength: password.value.length
    })
    
    // 调用真实后端API登录接口
    const loginData = await api.auth.login(username.value, password.value)
    
    console.log('✅ 登录响应:', loginData)
    
    // 登录成功
    Message.success({
      content: `登录成功！欢迎回来，${loginData.user.full_name}`,
      duration: 3000
    })
    
    // 保存 token 和用户信息（使用统一管理）
    import('@/utils/auth').then(({ auth }) => {
      auth.saveLoginData(
        loginData.access_token,
        loginData.user,
        rememberMe.value,
        username.value
      )
    }).catch(error => {
      console.error('加载auth工具失败:', error)
      // 降级处理
      localStorage.setItem('access_token', loginData.access_token)
      localStorage.setItem('user_info', JSON.stringify(loginData.user))
      if (rememberMe.value) {
        localStorage.setItem('lastUsername', username.value)
      }
    })
    
    // 显示成功信息
    apiStatus.value = {
      type: 'success',
      title: 'RBAC登录成功',
      content: `欢迎 ${loginData.user.full_name} (${loginData.user.role})，正在跳转到工作台...`
    }
    
    // 重置密码字段
    password.value = ''
    
    // 2秒后跳转到目标页面
    setTimeout(() => {
      const redirect = route.query.redirect as string
      if (redirect) {
        router.push(redirect)
      } else {
        router.push('/dashboard')
      }
    }, 2000)
    
  } catch (error: any) {
    console.error('❌ 登录失败:', error)
    
    // 处理不同类型的错误
    if (error.response) {
      // 服务器返回错误
      const status = error.response.status
      const data = error.response.data
      
      if (status === 401) {
        Message.error('账号或密码错误')
        apiStatus.value = {
          type: 'error',
          title: '认证失败',
          content: data.detail || '用户名或密码不正确'
        }
      } else if (status === 403) {
        Message.error('用户已被禁用')
        apiStatus.value = {
          type: 'warning',
          title: '账户被禁用',
          content: '请联系管理员激活账户'
        }
      } else if (status === 422) {
        Message.error('请求参数错误')
        apiStatus.value = {
          type: 'error',
          title: '参数错误',
          content: '请检查输入的用户名和密码格式'
        }
      } else {
        Message.error(`服务器错误: ${status}`)
        apiStatus.value = {
          type: 'error',
          title: '服务器错误',
          content: `错误代码: ${status} - ${data.detail || '未知错误'}`
        }
      }
    } else if (error.request) {
      // 请求发送但无响应
      Message.error('无法连接到后端服务器')
      apiStatus.value = {
        type: 'error',
        title: '连接失败',
        content: `请确保 FastAPI 后端正在运行 (${config.api.baseUrl})`
      }
      backendConnected.value = false
    } else {
      // 其他错误
      Message.error('登录请求失败')
      apiStatus.value = {
        type: 'error',
        title: '请求失败',
        content: error.message || '未知错误'
      }
    }
    
    // 清空密码（安全考虑）
    password.value = ''
    
  } finally {
    loginLoading.value = false
  }
}

// 其他功能（占位）
const showForgetPassword = () => {
  Message.info('忘记密码功能开发中...')
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
  background: #141414;
}

.background-decoration {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  z-index: 0;
}

.gradient-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.15;
}

.circle-1 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #165dff, #00b42a);
  top: -200px;
  right: -200px;
}

.circle-2 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #ff7d00, #f53f3f);
  bottom: -150px;
  left: -150px;
}

.circle-3 {
  width: 200px;
  height: 200px;
  background: linear-gradient(135deg, #722ed1, #eb2f96);
  top: 50%;
  left: 10%;
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  z-index: 1;
  transition: all 0.3s ease;
}

.login-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.4);
}

.card-header {
  text-align: center;
  padding: 32px 24px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 16px;
}

.logo-text {
  font-size: 24px;
  font-weight: 600;
  background: linear-gradient(135deg, #165dff, #00b42a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-text {
  margin: 0;
  color: var(--color-text-1);
}

.subtitle {
  display: block;
  margin-top: 8px;
}

.login-form {
  padding: 32px 24px;
}

.form-item {
  margin-bottom: 24px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  color: var(--color-text-1);
}

/* 快捷登录区域 */
.quick-login-section {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.quick-login-label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 14px;
}

.quick-login-buttons {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.quick-login-buttons .arco-btn {
  flex: 1;
  min-width: 100px;
}

.quick-login-hint {
  font-size: 12px;
  color: var(--color-text-3);
  text-align: center;
}

.quick-login-hint code {
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
  color: #ff7d00;
}

.remember-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32px;
}

.login-button {
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.login-button:not(:disabled):hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(22, 93, 255, 0.3);
}

.api-status {
  margin-top: 16px;
  animation: fadeIn 0.5s ease;
}

.backend-status {
  margin-top: 16px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.version-info {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-page {
    padding: 16px;
  }
  
  .login-card {
    max-width: 100%;
  }
  
  .card-header {
    padding: 24px 16px 16px;
  }
  
  .login-form {
    padding: 24px 16px;
  }
  
  .quick-login-buttons {
    flex-direction: column;
  }
  
  .quick-login-buttons .arco-btn {
    width: 100%;
  }
}
</style>