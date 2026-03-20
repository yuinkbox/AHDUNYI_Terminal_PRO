/**
 * RBAC ????? API ??
 *
 * ????:
 * - UserRole ???????? server/constants/roles.py ??
 * - ?????????? usePermissionStore().can() ??????????
 * - ?????????? + API ????
 */

import api from './index'

// ---------------------------------------------------------------------------
// ???? ? ?????? UserRole ???
// ---------------------------------------------------------------------------
export enum UserRole {
  MANAGER       = 'manager',
  TEAM_LEADER   = 'team_leader',
  QA_SPECIALIST = 'qa_specialist',
  ADMIN_SUPPORT = 'admin_support',
  AUDITOR       = 'auditor',
}

// ---------------------------------------------------------------------------
// ????
// ---------------------------------------------------------------------------
export enum ShiftType {
  MORNING   = 'morning',
  AFTERNOON = 'afternoon',
  NIGHT     = 'night',
}

export enum TaskChannel {
  IMAGE = 'image',
  CHAT  = 'chat',
  VIDEO = 'video',
  LIVE  = 'live',
}

// ---------------------------------------------------------------------------
// ????
// ---------------------------------------------------------------------------
export interface UserInfo {
  id: number
  username: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at?: string
}

export interface TaskAssignment {
  user_id: number
  username: string
  full_name: string
  task_channel: string
  historical_count: number
}

export interface DispatchRequest {
  shift_date: string
  shift_type: ShiftType
  user_ids: number[]
  required_channels: TaskChannel[]
}

export interface DispatchResponse {
  shift_date: string
  shift_type: string
  assignments: TaskAssignment[]
  summary: {
    total_assignments: number
    channel_distribution: Record<string, number>
    algorithm: string
    timestamp: string
  }
}

export interface TaskItem {
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
}

export interface UserTaskResponse {
  today_tasks: TaskItem[]
  historical_tasks: TaskItem[]
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
  period: { start: string; end: string }
  user_stats: Array<{
    user_id: number
    username: string
    full_name: string
    total_tasks: number
    total_reviewed: number
    total_violations: number
    total_duration: number
    violation_rate: number
    channels: Record<string, { count: number; reviewed: number; violations: number }>
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
  role: string
  is_active: boolean
  is_superuser: boolean
}

export interface ActionLogItem {
  id: number
  user_id: number
  username: string
  action: string
  details: string
  task_id?: number
  duration?: number
  timestamp: string
}

// ---------------------------------------------------------------------------
// API ????
// ---------------------------------------------------------------------------
export const rbacApi = {
  /** ?????????? */
  async getMyTasks(): Promise<UserTaskResponse> {
    return api.get('/api/task/my') as any
  },

  /** ?????? */
  async dispatchTasks(request: DispatchRequest): Promise<DispatchResponse> {
    return api.post('/api/dispatch/auto', request) as any
  },

  /** ???????? */
  async getTeamInsight(request: TeamInsightRequest): Promise<TeamInsightResponse> {
    const params: Record<string, string> = {
      start_date: request.start_date,
      end_date: request.end_date,
    }
    if (request.user_ids?.length) params.user_ids = request.user_ids.join(',')
    if (request.channels?.length) params.channels = request.channels.join(',')
    return api.get('/api/team/insight', { params }) as any
  },

  /** ???????? */
  async getActiveUsers(role?: string): Promise<{ users: ActiveUser[]; count: number; filter_role: string }> {
    const params = role ? { role } : {}
    return api.get('/api/users/active', { params }) as any
  },

  /** ??????????????????? */
  async logAction(action: string, details: string, duration?: number, taskId?: number): Promise<void> {
    try {
      await api.post('/api/log/action', {
        action,
        details,
        duration,
        task_id: taskId,
        timestamp: new Date().toISOString(),
      })
    } catch {
      // ?????????????
    }
  },

  /** ?????????????? */
  async updateUserRole(userId: number, newRole: string): Promise<{ success: boolean; message: string; user: UserInfo }> {
    return api.put(`/api/users/${userId}/role`, { role: newRole }) as any
  },

  /** ???????? */
  async getUserDetailedStats(userId: number, startDate?: string, endDate?: string): Promise<any> {
    const params: Record<string, string> = {}
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    return api.get(`/api/team/user/${userId}/stats`, { params }) as any
  },

  /** ?????? */
  async updateTaskProgress(
    taskId: number,
    data: { reviewed_count?: number; violation_count?: number; work_duration?: number; is_completed?: boolean },
  ): Promise<void> {
    try {
      await api.patch(`/api/task/${taskId}/progress`, data)
    } catch {
      // ????
    }
  },

  /** ???? */
  async completeTask(taskId: number): Promise<void> {
    try {
      await api.post(`/api/task/${taskId}/complete`)
    } catch {
      // ????
    }
  },

  /** ?????????????? */
  async getActionLogs(params?: {
    user_id?: number
    action?: string
    start_time?: string
    end_time?: string
    page?: number
    page_size?: number
  }): Promise<{ items: ActionLogItem[]; total: number; page: number; page_size: number }> {
    return api.get('/api/log/list', { params }) as any
  },
}

// ---------------------------------------------------------------------------
// ???? ? ???????????
// ---------------------------------------------------------------------------
export function getTaskChannelLabel(channel: string): string {
  const labels: Record<string, string> = {
    image: '????',
    chat:  '????',
    video: '????',
    live:  '?????',
  }
  return labels[channel] ?? channel
}

export function getShiftTypeLabel(shiftType: string): string {
  const labels: Record<string, string> = {
    morning:   '??',
    afternoon: '??',
    night:     '??',
  }
  return labels[shiftType] ?? shiftType
}

export function formatDuration(seconds: number): string {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  return [
    h.toString().padStart(2, '0'),
    m.toString().padStart(2, '0'),
    s.toString().padStart(2, '0'),
  ].join(':')
}
