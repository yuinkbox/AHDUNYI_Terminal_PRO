/**
 * API layer - dual-mode: QWebChannel (desktop) or HTTP (browser).
 *
 * Resolution order:
 *   1. If running inside PyQt6 WebEngine (window.qt present) -> use AppBridge.
 *   2. Otherwise -> use axios HTTP client (same as before).
 *
 * This file is the ONLY place that knows about the transport;  Vue
 * components always import from '@/api' and are transport-agnostic.
 */

import axios, { type AxiosInstance } from 'axios'
import { getBridge, isDesktopMode } from '@/bridge/qt_channel'
import config from '@/config'

// ---------------------------------------------------------------------------
// Axios HTTP client (browser / server mode)
// ---------------------------------------------------------------------------

const _http: AxiosInstance = axios.create({
  baseURL: config.api.baseUrl,
  timeout: config.api.timeout,
  headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
})

_http.interceptors.request.use((cfg) => {
  const token = localStorage.getItem('ahdunyi_access_token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

_http.interceptors.response.use(
  (r) => r.data,
  (err) => {
    const status: number = err.response?.status ?? 0
    if (status === 401) {
      localStorage.removeItem('ahdunyi_access_token')
      localStorage.removeItem('ahdunyi_user_info')
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  }
)

// ---------------------------------------------------------------------------
// Auth API
// ---------------------------------------------------------------------------

export const authAPI = {
  async login(username: string, password: string): Promise<any> {
    if (isDesktopMode()) {
      // In desktop mode login is handled by the Python LoginWindow.
      // The Vue app receives token_info via the tokenInfoChanged signal.
      // This method is kept for browser compatibility only.
      throw new Error(
        'In desktop mode authentication is handled by the native login window.'
      )
    }
    return _http.post('/api/auth/login', { username, password })
  },

  logout(): Promise<any> {
    return _http.post('/api/logout')
  },
}

// ---------------------------------------------------------------------------
// System API
// ---------------------------------------------------------------------------

export const systemAPI = {
  async healthCheck(): Promise<{ status: string }> {
    if (isDesktopMode()) {
      const bridge = await getBridge()
      if (bridge) {
        const raw = await bridge.getSystemStatus()
        return { status: 'healthy', ...JSON.parse(raw) }
      }
    }
    return _http.get('/api/health')
  },

  async getSystemStatus(): Promise<any> {
    if (isDesktopMode()) {
      const bridge = await getBridge()
      if (bridge) {
        const raw = await bridge.getSystemStatus()
        return JSON.parse(raw)
      }
    }
    return _http.get('/api/system/status')
  },
}

// ---------------------------------------------------------------------------
// Room API (desktop-first)
// ---------------------------------------------------------------------------

export const roomAPI = {
  async getCurrentRoomId(): Promise<string> {
    if (isDesktopMode()) {
      const bridge = await getBridge()
      if (bridge) return bridge.getRoomId()
    }
    const data = await _http.get('/api/room/current')
    return (data as any)?.room_id ?? ''
  },
}

// ---------------------------------------------------------------------------
// Patrol / audit API (HTTP only - routed to backend)
// ---------------------------------------------------------------------------

export const patrolAPI = {
  getDashboardData:    (): Promise<any> => _http.get('/api/dashboard'),
  getRiskAudits:       (params?: object): Promise<any> => _http.get('/api/risk-audits', { params }),
  getRealTimePatrols:  (): Promise<any> => _http.get('/api/patrols/realtime'),
  getViolationReviews: (): Promise<any> => _http.get('/api/violations/reviews'),
  getSOPList:          (): Promise<any> => _http.get('/api/sop'),
}

// ---------------------------------------------------------------------------
// Default export
// ---------------------------------------------------------------------------

export default {
  auth:   authAPI,
  system: systemAPI,
  room:   roomAPI,
  patrol: patrolAPI,
  get:    (url: string, config?: object) => _http.get(url, config),
  post:   (url: string, data?: any, config?: object) => _http.post(url, data, config),
  put:    (url: string, data?: any, config?: object) => _http.put(url, data, config),
  patch:  (url: string, data?: any, config?: object) => _http.patch(url, data, config),
  delete: (url: string, config?: object) => _http.delete(url, config),
}
