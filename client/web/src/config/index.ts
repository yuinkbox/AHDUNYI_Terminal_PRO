/**
 * 前端环境配置模块 - 支持双轨制部署
 */

// 环境类型
export type Environment = 'development' | 'test' | 'production'

// 配置接口
export interface AppConfig {
  // 环境
  env: Environment
  
  // API配置
  api: {
    baseUrl: string
    timeout: number
    prodUrl: string
    testUrl: string
  }
  
  // 应用配置
  app: {
    title: string
    version: string
    copyright: string
  }
  
  // 功能开关
  features: {
    debug: boolean
    enableMock: boolean
    consoleLog: boolean
  }
  
  // 客户端配置
  client: {
    type: 'web' | 'desktop'
    autoRefreshInterval: number
  }
  
  // 日志配置
  logging: {
    level: 'debug' | 'info' | 'warn' | 'error'
  }
}

// 从环境变量加载配置
const loadConfig = (): AppConfig => {
  const env = import.meta.env
  
  // 确定当前环境
  const environment = (env.VITE_ENV || 'development') as Environment
  
  // 根据环境选择API地址
  const getApiBaseUrl = () => {
    // 优先使用显式配置的URL
    if (env.VITE_API_BASE_URL) {
      return env.VITE_API_BASE_URL
    }
    
    // 根据环境选择默认URL
    switch (environment) {
      case 'production':
        return env.VITE_PROD_API_URL || 'http://106.15.32.246:8000'
      case 'test':
        return env.VITE_TEST_API_URL || 'http://106.15.32.246:8000'
      case 'development':
      default:
        return 'http://106.15.32.246:8000'
    }
  }
  
  return {
    env: environment,
    
    api: {
      baseUrl: getApiBaseUrl(),
      timeout: parseInt(env.VITE_API_TIMEOUT || '10000', 10),
      prodUrl: env.VITE_PROD_API_URL || 'http://106.15.32.246:8000',
      testUrl: env.VITE_TEST_API_URL || 'http://106.15.32.246:8000'
    },
    
    app: {
      title: env.VITE_APP_TITLE || 'AHDUNYI 风控审核中台',
      version: env.VITE_APP_VERSION || '2.0.0',
      copyright: env.VITE_APP_COPYRIGHT || '© 2026 AHDUNYI'
    },
    
    features: {
      debug: env.VITE_DEBUG === 'true',
      enableMock: env.VITE_ENABLE_MOCK === 'true',
      consoleLog: env.VITE_CONSOLE_LOG !== 'false'
    },
    
    client: {
      type: (env.VITE_CLIENT_TYPE || 'web') as 'web' | 'desktop',
      autoRefreshInterval: parseInt(env.VITE_AUTO_REFRESH_INTERVAL || '5000', 10)
    },
    
    logging: {
      level: (env.VITE_LOG_LEVEL || 'info') as 'debug' | 'info' | 'warn' | 'error'
    }
  }
}

// 全局配置实例
const config = loadConfig()

// 环境判断函数
export const isProduction = (): boolean => config.env === 'production'
export const isTest = (): boolean => config.env === 'test'
export const isDevelopment = (): boolean => config.env === 'development'

export const getEnvironmentDisplay = (): string => {
  const envMap: Record<Environment, string> = {
    production: '正式服',
    test: '体验服',
    development: '开发环境'
  }
  return envMap[config.env] || '未知环境'
}

// 获取当前服务器地址（用于客户端配置）
export const getCurrentServerUrl = (): string => {
  return config.api.baseUrl
}

// 获取API配置（用于axios实例）
export const getApiConfig = () => ({
  baseURL: config.api.baseUrl,
  timeout: config.api.timeout
})

// 日志函数（根据配置控制输出）
export const logger = {
  debug: (...args: any[]) => {
    if (config.features.consoleLog && config.logging.level === 'debug') {
      console.debug('[DEBUG]', ...args)
    }
  },
  
  info: (...args: any[]) => {
    if (config.features.consoleLog && ['debug', 'info'].includes(config.logging.level)) {
      console.info('[INFO]', ...args)
    }
  },
  
  warn: (...args: any[]) => {
    if (config.features.consoleLog && ['debug', 'info', 'warn'].includes(config.logging.level)) {
      console.warn('[WARN]', ...args)
    }
  },
  
  error: (...args: any[]) => {
    if (config.features.consoleLog) {
      console.error('[ERROR]', ...args)
    }
  }
}

// 启动时打印配置信息
if (config.features.consoleLog) {
  console.log('='.repeat(60))
  console.log(`🚀 ${config.app.title} - ${getEnvironmentDisplay()}`)
  console.log(`📊 环境: ${config.env}`)
  console.log(`🌐 API地址: ${config.api.baseUrl}`)
  console.log(`📱 客户端类型: ${config.client.type}`)
  console.log(`🔧 调试模式: ${config.features.debug ? '开启' : '关闭'}`)
  console.log('='.repeat(60))
}

export default config