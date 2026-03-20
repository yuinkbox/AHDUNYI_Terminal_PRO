/**
 * RBAC权限与任务派发API封装
 */

import api from './index'

// 用户角色类型
export enum UserRole {
  SUPERVISOR = 'supervisor',
  SHIFT_LEADER = 'shift_leader',
  AUDITOR = 'auditor'
}

// 班次类型
export enum ShiftType {
  MORNING = 'morning',
  AFTERNOON = 'afternoon',
  NIGHT = 'night'
}

// 任务通道
export enum TaskChannel {
  IMAGE = 'image',
  CHAT = 'chat',
  VIDEO = 'video',
  LIVE = 'live'
}

// 接口请求/响应类型
export interface UserInfo {
  id: number
  username: string
  email: string
  full_name: string
  role: UserRole
  is_admin: boolean
  created_at: string
}

export interface TaskAssignment {
  user_id: number
  username: string
  full_name: string
  task_channel: TaskChannel
  historical_count: number
}

export interface DispatchRequest {
  shift_date: string  // ISO日期格式
  shift_type: ShiftType
  user_ids: number[]
  required_channels: TaskChannel[]
}

export interface DispatchResponse {
  shift_date: string
  shift_type: ShiftType
  assignments: TaskAssignment[]
  summary: {
    total_assignments: number
    channel_distribution: Record<string, number>
    algorithm: string
    timestamp: string
  }
}

export interface UserTaskResponse {
  today_tasks: Array<{
    id: number
    shift_date: string
    shift_type: string
    task_channel: string
    user_id: number
    is_completed: boolean
    reviewed_count: number
    violation_count: number
    work_duration: number
    user_info?: {
      username: string
      full_name: string
      role: string
    }
  }>
  historical_tasks: Array<any>
  weekly_stats: {
    total_reviewed: number
    total_violations: number
    total_duration: number
    task_count: number
    week: number
    year: number
  }
}

export interface TeamInsightRequest {
  start_date: string
  end_date: string
  user_ids?: number[]
  channels?: TaskChannel[]
}

export interface TeamInsightResponse {
  period: {
    start: string
    end: string
  }
  user_stats: Array<{
    user_id: number
    username: string
    full_name: string
    total_tasks: number
    total_reviewed: number
    total_violations: number
    total_duration: number
    channels: Record<string, {
      count: number
      reviewed: number
      violations: number
    }>
  }>
  channel_stats: Array<{
    channel: string
    total_tasks: number
    total_reviewed: number
    total_violations: number
    avg_reviewed_per_task: number
    unique_users: number
  }>
  overall_stats: {
    period_start: string
    period_end: string
    total_tasks: number
    total_users: number
    total_reviewed: number
    total_violations: number
    total_duration: number
    avg_reviewed_per_user: number
    channels_covered: number
  }
}

export interface ActiveUser {
  id: number
  username: string
  email: string
  full_name: string
  role: UserRole
  is_active: boolean
  is_admin: boolean
}

// API函数
export const rbacApi = {
  // 获取用户今日任务
  async getMyTasks(): Promise<UserTaskResponse> {
    const response = await api.get('/api/task/my')
    return response as any
  },

  // 自动任务派发
  async dispatchTasks(request: DispatchRequest): Promise<DispatchResponse> {
    const response = await api.post('/api/dispatch/auto', request)
    return response as any
  },

  // 获取团队数据洞察
  async getTeamInsight(request: TeamInsightRequest): Promise<TeamInsightResponse> {
    // 转换参数格式：数组转换为逗号分隔的字符串
    const params: any = {
      start_date: request.start_date,
      end_date: request.end_date
    }
    
    if (request.user_ids && request.user_ids.length > 0) {
      params.user_ids = request.user_ids.join(',')
    }
    
    if (request.channels && request.channels.length > 0) {
      params.channels = request.channels.join(',')
    }
    
    const response = await api.get('/api/team/insight', { params })
    return response as any
  },

  // 获取活跃用户列表
  async getActiveUsers(role?: UserRole): Promise<{ users: ActiveUser[], count: number, filter_role: string }> {
    const params = role ? { role } : {}
    const response = await api.get('/api/users/active', { params })
    return response as any
  },

  // 记录操作日志（每次按键）
  async logAction(action: string, details: string, duration?: number, taskId?: number): Promise<void> {
    try {
      await api.post('/api/log/action', {
        action,
        details,
        duration,
        task_id: taskId,
        timestamp: new Date().toISOString()
      })
    } catch (error) {
      console.error('记录操作日志失败:', error)
      // 失败不影响主流程
    }
  },

  // 更新用户角色（主管专用）
  async updateUserRole(userId: number, newRole: string): Promise<{ success: boolean; message: string; user: any }> {
    const response = await api.put(`/api/users/${userId}/role`, { role: newRole })
    return response as any
  },

  // 获取用户详细统计（主管专用）
  async getUserDetailedStats(userId: number, startDate?: string, endDate?: string): Promise<any> {
    const params: any = {}
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    
    const response = await api.get(`/api/team/user/${userId}/stats`, { params })
    return response as any
  },

  // 更新任务进度
  async updateTaskProgress(taskId: number, data: {
    reviewed_count?: number
    violation_count?: number
    work_duration?: number
    is_completed?: boolean
  }): Promise<void> {
    try {
      await api.patch(`/api/task/${taskId}/progress`, data)
    } catch (error) {
      console.error('更新任务进度失败:', error)
    }
  },

  // 完成任务
  async completeTask(taskId: number): Promise<void> {
    try {
      await api.post(`/api/task/${taskId}/complete`)
    } catch (error) {
      console.error('完成任务失败:', error)
    }
  },

  // 获取用户统计
  async getUserStats(userId: number, startDate?: string, endDate?: string): Promise<any> {
    try {
      const params: any = {}
      if (startDate) params.start_date = startDate
      if (endDate) params.end_date = endDate
      
      const response = await api.get(`/api/user/${userId}/stats`, { params })
      return response
    } catch (error) {
      console.error('获取用户统计失败:', error)
      return null
    }
  }
}

// 工具函数
export async function getUserRole(): Promise<UserRole | null> { // eslint-disable-line @typescript-eslint/no-unused-vars
  try {
    // 尝试使用新的统一auth工具
    const { auth } = await import('@/utils/auth')
    const userInfo = auth.getUserInfo()
    if (!userInfo) return null
    
    return userInfo.role as UserRole
  } catch (error) {
    console.warn('使用auth工具失败，尝试降级方案:', error)
    // 降级处理：使用旧的键名
    try {
      const userInfo = localStorage.getItem('user_info') || localStorage.getItem('ahdunyi_user_info')
      if (!userInfo) return null
      
      const user = JSON.parse(userInfo)
      return user.role as UserRole
    } catch (parseError) {
      console.error('获取用户角色失败:', parseError)
      return null
    }
  }
}

export async function getCurrentUserInfo(): Promise<UserInfo | null> {
  try {
    // 尝试使用新的统一auth工具
    const { auth } = await import('@/utils/auth')
    return auth.getUserInfo() as UserInfo | null
  } catch (error) {
    console.warn('使用auth工具失败，尝试降级方案:', error)
    // 降级处理：使用旧的键名
    try {
      const userInfo = localStorage.getItem('user_info') || localStorage.getItem('ahdunyi_user_info')
      if (!userInfo) return null
      
      return JSON.parse(userInfo) as UserInfo
    } catch (parseError) {
      console.error('获取用户信息失败:', parseError)
      return null
    }
  }
}

// 同步版本（兼容旧代码）
export function getUserRoleSync(): UserRole | null {
  try {
    const userInfo = localStorage.getItem('user_info') || localStorage.getItem('ahdunyi_user_info')
    if (!userInfo) return null
    
    const user = JSON.parse(userInfo)
    return user.role as UserRole
  } catch (error) {
    console.error('获取用户角色失败:', error)
    return null
  }
}

export function getCurrentUserInfoSync(): UserInfo | null {
  try {
    const userInfo = localStorage.getItem('user_info') || localStorage.getItem('ahdunyi_user_info')
    if (!userInfo) return null
    
    return JSON.parse(userInfo) as UserInfo
  } catch (error) {
    console.error('获取用户信息失败:', error)
    return null
  }
}

export function getTaskChannelLabel(channel: TaskChannel): string {
  const labels: Record<TaskChannel, string> = {
    [TaskChannel.IMAGE]: '图片审核',
    [TaskChannel.CHAT]: '单聊审核',
    [TaskChannel.VIDEO]: '视频审核',
    [TaskChannel.LIVE]: '直播间巡查'
  }
  return labels[channel] || channel
}

export function getShiftTypeLabel(shiftType: ShiftType): string {
  const labels: Record<ShiftType, string> = {
    [ShiftType.MORNING]: '早班',
    [ShiftType.AFTERNOON]: '中班',
    [ShiftType.NIGHT]: '晚班'
  }
  return labels[shiftType] || shiftType
}

export function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

export function getRoleLabel(role: UserRole): string {
  const labels: Record<UserRole, string> = {
    [UserRole.SUPERVISOR]: '主管',
    [UserRole.SHIFT_LEADER]: '组长',
    [UserRole.AUDITOR]: '审核员'
  }
  return labels[role] || role
}

export function getRoleColor(role: UserRole): string {
  const colors: Record<UserRole, string> = {
    [UserRole.SUPERVISOR]: 'red',
    [UserRole.SHIFT_LEADER]: 'orange',
    [UserRole.AUDITOR]: 'green'
  }
  return colors[role] || 'gray'
}

// 权限检查函数
export function hasPermission(requiredRole: UserRole, userRole?: UserRole): boolean {
  if (!userRole) {
    userRole = getUserRoleSync() ?? undefined
  }
  
  if (!userRole) return false
  
  // 权限等级：主管 > 组长 > 审核员
  const roleLevels: Record<UserRole, number> = {
    [UserRole.SUPERVISOR]: 3,
    [UserRole.SHIFT_LEADER]: 2,
    [UserRole.AUDITOR]: 1
  }
  
  const userLevel = roleLevels[userRole]
  const requiredLevel = roleLevels[requiredRole]
  
  return userLevel >= requiredLevel
}

// 检查是否是主管
export function isSupervisor(userRole?: UserRole): boolean {
  if (!userRole) {
    userRole = getUserRoleSync() ?? undefined
  }
  return userRole === UserRole.SUPERVISOR
}

// 检查是否是组长
export function isShiftLeader(userRole?: UserRole): boolean {
  if (!userRole) {
    userRole = getUserRoleSync() ?? undefined
  }
  return userRole === UserRole.SHIFT_LEADER
}

// 检查是否是审核员
export function isAuditor(userRole?: UserRole): boolean {
  if (!userRole) {
    userRole = getUserRoleSync() ?? undefined
  }
  return userRole === UserRole.AUDITOR
}