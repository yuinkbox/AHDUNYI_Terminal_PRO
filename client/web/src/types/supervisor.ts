/**
 * 主管大屏相关类型定义
 */

// 审计状态枚举
export enum AuditStatus {
  NORMAL = 'normal',
  SUSPICIOUS = 'suspicious',
  SUDDEN_ISSUE = 'sudden_issue',
  RISK_TRACKING = 'risk_tracking',
  EXEMPTED = 'exempted'
}

// 活跃用户状态
export interface ActiveUserStatus {
  user_id: number
  username: string
  full_name: string
  room_id: string
  stay_duration: number  // 停留时长（秒）
  status: AuditStatus
  context_reason: string  // 异常原因
  exemption_checks?: Array<{
    check: string
    result: string
    [key: string]: any
  }>
  last_activity: string
}

// 系统统计信息
export interface SystemStats {
  total_active_users: number
  room_monitor_available: boolean
  audit_engine_available: boolean
  timestamp: string
}

// 审计引擎统计
export interface AuditStats {
  total_checks: number
  normal_count: number
  suspicious_count: number
  exempted_count: number
  error_count: number
  hopping_detected: number
  avg_response_time: number
  [key: string]: any
}

// RoomMonitor状态
export interface RoomMonitorStatus {
  running: boolean
  current_room_id: string | null
  stats: {
    total_scans: number
    room_changes: number
    last_change_time: number | null
    [key: string]: any
  }
}

// 实时状态响应
export interface RealtimeStatusResponse {
  success: boolean
  system: SystemStats
  active_users: ActiveUserStatus[]
  audit_stats: AuditStats
  room_monitor: RoomMonitorStatus
  timestamp: string
}

// 表格列定义
export interface RadarTableColumn {
  title: string
  dataIndex: string
  key: string
  width?: number
  align?: 'left' | 'center' | 'right'
  sorter?: boolean
  render?: (value: any, record: ActiveUserStatus) => any
}