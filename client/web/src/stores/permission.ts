/**
 * Permission Store — Single Source of Truth for all access control.
 *
 * Design:
 * - The backend owns the role→permission matrix.
 * - This store is a pure consumer: it receives permissions from the login
 *   response (or a /api/auth/permissions refresh) and exposes helpers.
 * - Vue components NEVER check role strings directly.  They call can().
 * - Adding a new role or permission requires ZERO frontend changes.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

// ---------------------------------------------------------------------------
// Types (mirrors backend PermissionsResponse)
// ---------------------------------------------------------------------------
export interface RoleMeta {
  label: string        // e.g. "风控经理"
  color: string        // arco-design colour token, e.g. "red"
  dashboard_view: string  // "supervisor" | "leader" | "auditor"
}

export interface RoleDescriptor {
  value: string
  label: string
  color: string
  dashboard_view: string
}

// ---------------------------------------------------------------------------
// Store
// ---------------------------------------------------------------------------
export const usePermissionStore = defineStore('permission', () => {
  // ---- state ----------------------------------------------------------------
  const permissions = ref<string[]>([])
  const role = ref<string>('')
  const roleMeta = ref<RoleMeta>({
    label: '',
    color: 'gray',
    dashboard_view: 'auditor',
  })
  const allRoles = ref<RoleDescriptor[]>([])
  const hydrated = ref(false)   // true once permissions have been loaded

  // ---- getters --------------------------------------------------------------
  const roleLabel = computed(() => roleMeta.value.label || role.value)
  const roleColor = computed(() => roleMeta.value.color || 'gray')
  const dashboardView = computed(() => roleMeta.value.dashboard_view || 'auditor')

  // ---- core helpers ---------------------------------------------------------
  /**
   * Check whether the current user holds a specific permission point.
   *
   * @param permission - e.g. "view:shadow_audit"
   * @returns true if the permission is granted
   */
  function can(permission: string): boolean {
    return permissions.value.includes(permission)
  }

  /**
   * Check whether the current user holds ANY of the listed permissions.
   */
  function canAny(...perms: string[]): boolean {
    return perms.some(p => permissions.value.includes(p))
  }

  /**
   * Check whether the current user holds ALL of the listed permissions.
   */
  function canAll(...perms: string[]): boolean {
    return perms.every(p => permissions.value.includes(p))
  }

  // ---- bootstrap (called once after login) ----------------------------------
  /**
   * Hydrate the store from a login response payload.
   * Call this immediately after a successful login.
   */
  function bootstrap(data: {
    role: string
    permissions: string[]
    role_meta: RoleMeta
  }): void {
    role.value = data.role
    permissions.value = data.permissions
    roleMeta.value = data.role_meta
    hydrated.value = true
    // persist for page-reload recovery
    localStorage.setItem('ahdunyi_permissions', JSON.stringify(data))
  }

  /**
   * Re-hydrate from localStorage (called on app startup / page reload).
   * Falls back to fetching from the API if localStorage is stale.
   */
  async function restore(): Promise<void> {
    // 1. Try localStorage first (instant, no network)
    const cached = localStorage.getItem('ahdunyi_permissions')
    if (cached) {
      try {
        const data = JSON.parse(cached)
        role.value = data.role
        permissions.value = data.permissions
        roleMeta.value = data.role_meta
        hydrated.value = true
      } catch {
        localStorage.removeItem('ahdunyi_permissions')
      }
    }

    // 2. Always refresh from API in the background to pick up role changes
    const token = localStorage.getItem('ahdunyi_access_token')
    if (token) {
      try {
        const resp = await api.get('/api/auth/permissions') as any
        bootstrap({
          role: resp.role,
          permissions: resp.permissions,
          role_meta: resp.role_meta,
        })
      } catch (err) {
        console.warn('[PermissionStore] Background refresh failed:', err)
        // Even if API fails, mark as hydrated so UI can render with cached/default data
        hydrated.value = true
      }
    } else {
      // No token, mark as hydrated with default state
      hydrated.value = true
    }
  }

  /**
   * Load all available roles from the backend (for admin dropdowns).
   * Result is cached in allRoles; call once per session.
   */
  async function fetchAllRoles(): Promise<RoleDescriptor[]> {
    if (allRoles.value.length > 0) return allRoles.value
    try {
      const resp = await api.get('/api/auth/roles') as any
      allRoles.value = resp.roles
    } catch (err) {
      console.warn('[PermissionStore] fetchAllRoles failed:', err)
    }
    return allRoles.value
  }

  /** Clear all permission data on logout. */
  function clear(): void {
    permissions.value = []
    role.value = ''
    roleMeta.value = { label: '', color: 'gray', dashboard_view: 'auditor' }
    allRoles.value = []
    hydrated.value = false
    localStorage.removeItem('ahdunyi_permissions')
  }

  return {
    // state
    permissions,
    role,
    roleMeta,
    allRoles,
    hydrated,
    // getters
    roleLabel,
    roleColor,
    dashboardView,
    // helpers
    can,
    canAny,
    canAll,
    // lifecycle
    bootstrap,
    restore,
    fetchAllRoles,
    clear,
  }
})
