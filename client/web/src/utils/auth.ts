/**
 * 统一认证管理工具
 * 确保Token存储和读取的一致性
 */

export const TOKEN_KEY = 'ahdunyi_access_token'
export const USER_INFO_KEY = 'ahdunyi_user_info'
export const LAST_USERNAME_KEY = 'ahdunyi_last_username'

export const auth = {
  saveLoginData: (accessToken: string, userInfo: any, rememberMe: boolean = false, lastUsername?: string) => {
    try {
      localStorage.setItem(TOKEN_KEY, accessToken)
      localStorage.setItem(USER_INFO_KEY, JSON.stringify(userInfo))
      if (rememberMe && lastUsername) {
        localStorage.setItem(LAST_USERNAME_KEY, lastUsername)
      } else {
        localStorage.removeItem(LAST_USERNAME_KEY)
      }
      return true
    } catch (error) {
      console.error('❌ 保存登录信息失败:', error)
      return false
    }
  },
  
  getToken: (): string | null => localStorage.getItem(TOKEN_KEY),
  
  getUserInfo: (): any | null => {
    try {
      const userInfo = localStorage.getItem(USER_INFO_KEY)
      return userInfo ? JSON.parse(userInfo) : null
    } catch (error) {
      return null
    }
  },
  
  getLastUsername: (): string | null => localStorage.getItem(LAST_USERNAME_KEY),
  
  clearLoginData: () => {
    // 清除新版统一键名
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_INFO_KEY)
    
    // 🔥 焦土政策：同时清除所有可能残留的旧版键名，斩草除根！
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_info')
    localStorage.removeItem('token')
    console.log('🗑️ 所有新旧登录凭证已彻底清除')
  },
  
  isLoggedIn: (): boolean => {
    const token = auth.getToken()
    const user = auth.getUserInfo()
    return !!(token && user && user.username && user.id)
  },
  
  getBearerToken: (): string => {
    const token = auth.getToken()
    return token ? `Bearer ${token}` : ''
  },
  
  validateToken: (token: string): boolean => {
    if (!token || token.length < 10) return false
    return true
  }
}

export default auth