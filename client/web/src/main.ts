import { createApp } from 'vue'
import ArcoVue from '@arco-design/web-vue'
import ArcoVueIcon from '@arco-design/web-vue/es/icon'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import '@arco-design/web-vue/dist/arco.css'
import './styles/index.css'
import { isDesktopMode, getBridge } from '@/bridge/qt_channel'
import { usePermissionStore } from '@/stores/permission'
import { auth } from '@/utils/auth'

// Enable dark theme
document.body.setAttribute('arco-theme', 'dark')

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)
app.use(ArcoVue)
app.use(ArcoVueIcon)
app.mount('#app')

const permissionStore = usePermissionStore()

/**
 * Apply a token_info payload to localStorage and Pinia, then navigate
 * to Dashboard if currently on the login/root page.
 */
function _applyTokenInfo(tokenInfo: any): void {
  try {
    const token: string = tokenInfo.access_token ?? ''
    const user = tokenInfo.user ?? {
      username: tokenInfo.username ?? tokenInfo.sub ?? '',
      full_name: tokenInfo.full_name ?? '',
      role: tokenInfo.role ?? '',
      is_superuser: tokenInfo.is_superuser ?? false,
    }
    if (!token) {
      console.warn('[App] tokenInfo has no access_token:', tokenInfo)
      return
    }

    auth.saveLoginData(token, user)

    // permissions may be at top-level or inside a nested object
    const permData = tokenInfo.permissions
      ? tokenInfo
      : (JSON.parse(localStorage.getItem('ahdunyi_permissions') || 'null') ?? {})

    permissionStore.bootstrap({
      role: user.role ?? tokenInfo.role ?? '',
      permissions: permData.permissions ?? [],
      role_meta: permData.role_meta ?? {
        label: user.role ?? '',
        color: 'gray',
        dashboard_view: 'auditor',
      },
    })

    console.info('[App] Token applied: user=%s role=%s', user.username, user.role)

    // Navigate away from login page
    const current = router.currentRoute.value
    if (
      current.name === 'Login' ||
      current.path === '/' ||
      current.path === '/login'
    ) {
      router.push({ name: 'Dashboard' })
    }
  } catch (err) {
    console.error('[App] _applyTokenInfo error:', err)
  }
}

if (isDesktopMode()) {
  // --------------------------------------------------------------------------
  // Desktop (PyQt6 WebEngine) mode
  //
  // Strategy A (primary): Python injects token into localStorage via
  //   runJavaScript on loadFinished, then fires 'ahdunyi:token-ready' event.
  //   This is timing-safe: the event arrives AFTER the page is fully loaded.
  //
  // Strategy B (fallback): QWebChannel bridge.getTokenInfo() polled once
  //   after bridge is ready, in case the event was missed.
  // --------------------------------------------------------------------------

  // Strategy A: listen for the custom event dispatched by Python runJavaScript
  window.addEventListener('ahdunyi:token-ready', (e: Event) => {
    const detail = (e as CustomEvent).detail ?? {}
    console.info('[App] ahdunyi:token-ready received')

    // localStorage already written by Python; just need to bootstrap Pinia
    const token = localStorage.getItem('ahdunyi_access_token') ?? ''
    const userRaw = localStorage.getItem('ahdunyi_user_info')
    const permRaw = localStorage.getItem('ahdunyi_permissions')
    const user = userRaw ? JSON.parse(userRaw) : (detail.user ?? {})
    const perm = permRaw ? JSON.parse(permRaw) : (detail.permissions ?? {})

    if (token && user) {
      auth.saveLoginData(token, user)
      permissionStore.bootstrap({
        role: perm.role ?? user.role ?? '',
        permissions: perm.permissions ?? [],
        role_meta: perm.role_meta ?? { label: '', color: 'gray', dashboard_view: 'auditor' },
      })
      console.info('[App] Pinia bootstrapped from localStorage (Strategy A)')
      const current = router.currentRoute.value
      if (current.name === 'Login' || current.path === '/' || current.path === '/login') {
        router.push({ name: 'Dashboard' })
      }
    }
  })

  // Strategy B: QWebChannel bridge fallback
  getBridge().then(async (bridge) => {
    if (!bridge) {
      console.warn('[App] QWebChannel bridge unavailable.')
      return
    }
    console.info('[App] QWebChannel bridge ready.')

    // Subscribe to future token updates (e.g. token refresh)
    bridge.tokenInfoChanged.connect((raw: string) => {
      try {
        _applyTokenInfo(JSON.parse(raw))
      } catch (err) {
        console.warn('[App] tokenInfoChanged parse error:', err)
      }
    })

    // If localStorage already has token (Strategy A succeeded), skip
    if (auth.getToken()) {
      console.info('[App] Token already in localStorage, bridge fallback skipped.')
      return
    }

    // Otherwise try to get token from bridge directly
    try {
      const raw = await bridge.getTokenInfo()
      if (raw && raw !== '{}') {
        console.info('[App] Strategy B: got token from bridge.getTokenInfo()')
        _applyTokenInfo(JSON.parse(raw))
      }
    } catch (err) {
      console.warn('[App] bridge.getTokenInfo() error:', err)
    }
  })

} else {
  // Browser / web mode: restore from localStorage + API refresh
  console.info('[App] Running in browser/web mode.')
  permissionStore.restore()
}
