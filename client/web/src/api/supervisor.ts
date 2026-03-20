/**
 * 主管大屏API客户端
 */

import api from './index'
import type { RealtimeStatusResponse } from '@/types/supervisor'

export const supervisorApi = {
  /**
   * 获取实时状态数据
   */
  async getRealtimeStatus(): Promise<RealtimeStatusResponse> {
    const response = await api.get('/api/supervisor/realtime-status')
    return response as any
  },

  /**
   * 启动主管大屏GUI
   */
  async launchDashboard(): Promise<{
    success: boolean
    message: string
    gui_available: boolean
    launch_config?: any
    launch_command?: any
  }> {
    const response = await api.post('/api/supervisor/launch-dashboard')
    return response as any
  },

  /**
   * 获取RoomMonitor状态
   */
  async getRoomMonitorStatus(): Promise<{
    available: boolean
    running: boolean
    target_running: boolean
    current_room_id: string | null
    stats: any
    config: any
  }> {
    const response = await api.get('/api/system/room-monitor/status')
    return response as any
  },

  /**
   * 控制RoomMonitor
   */
  async controlRoomMonitor(action: 'start' | 'stop' | 'restart'): Promise<{
    success: boolean
    message: string
  }> {
    const response = await api.post('/api/system/room-monitor/control', { action })
    return response as any
  }
}

export default supervisorApi