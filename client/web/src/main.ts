import { createApp } from 'vue'
import ArcoVue from '@arco-design/web-vue'
import ArcoVueIcon from '@arco-design/web-vue/es/icon'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import '@arco-design/web-vue/dist/arco.css'
import './styles/index.css'
import { isDesktopMode, getBridge } from '@/bridge/qt_channel'

// Enable dark theme
document.body.setAttribute('arco-theme', 'dark')

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ArcoVue)
app.use(ArcoVueIcon)
app.mount('#app')

// In desktop (PyQt6 WebEngine) mode, initialise the QWebChannel bridge.
// This is a fire-and-forget async call; Vue components use getBridge()
// directly and await it themselves.
if (isDesktopMode()) {
  getBridge().then((bridge) => {
    if (bridge) {
      console.info('[App] QWebChannel bridge ready.')
    } else {
      console.warn('[App] QWebChannel bridge unavailable.')
    }
  })
} else {
  console.info('[App] Running in browser/web mode.')
}
