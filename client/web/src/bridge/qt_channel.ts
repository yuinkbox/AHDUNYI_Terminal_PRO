/**
 * QWebChannel bridge client for desktop (PyQt6) mode.
 *
 * Initialises the Qt WebChannel and exposes a typed wrapper around
 * the Python AppBridge object.  In web/browser mode (window.qt absent)
 * all methods return safe default values so the same Vue code runs in
 * both environments.
 *
 * Usage
 * -----
 * import { getBridge, onRoomIdChanged } from '@/bridge/qt_channel'
 *
 * const bridge = await getBridge()
 * const roomId = await bridge.getRoomId()
 *
 * onRoomIdChanged((id) => { console.log('new room:', id) })
 */

// The qwebchannel.js file is served automatically by QtWebEngine at
// the well-known URL qrc:///qtwebchannel/qwebchannel.js
// Vite cannot bundle it, so we declare the global type here.
declare global {
  interface Window {
    qt?: {
      webChannelTransport: object
    }
    QWebChannel?: new (
      transport: object,
      callback: (channel: { objects: Record<string, any> }) => void
    ) => void
  }
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface AppBridge {
  /** Return the currently monitored room ID, or empty string. */
  getRoomId(): Promise<string>
  /** Return a JSON string with system status. */
  getSystemStatus(): Promise<string>
  /** Return a JSON string with the logged-in user token payload. */
  getTokenInfo(): Promise<string>
  /** Forward a JS log message to Python logging. */
  logFromJS(message: string): void
  // Signals
  roomIdChanged:       { connect: (cb: (id: string) => void) => void }
  systemStatusChanged: { connect: (cb: (status: string) => void) => void }
  tokenInfoChanged:    { connect: (cb: (info: string) => void) => void }
}

// ---------------------------------------------------------------------------
// Internal state
// ---------------------------------------------------------------------------

let _bridge: AppBridge | null = null
let _initPromise: Promise<AppBridge | null> | null = null

// ---------------------------------------------------------------------------
// Desktop mode: load qwebchannel.js then initialise
// ---------------------------------------------------------------------------

function _loadQWebChannelScript(): Promise<void> {
  return new Promise((resolve, reject) => {
    if (typeof window.QWebChannel !== 'undefined') {
      resolve()
      return
    }
    const script = document.createElement('script')
    script.src = 'qrc:///qtwebchannel/qwebchannel.js'
    script.onload = () => resolve()
    script.onerror = () => reject(new Error('Failed to load qwebchannel.js'))
    document.head.appendChild(script)
  })
}

function _initDesktopBridge(): Promise<AppBridge | null> {
  return new Promise(async (resolve) => {
    try {
      await _loadQWebChannelScript()
      new window.QWebChannel!(window.qt!.webChannelTransport, (channel) => {
        _bridge = channel.objects.bridge as AppBridge
        console.info('[QTBridge] AppBridge connected.')
        resolve(_bridge)
      })
    } catch (err) {
      console.warn('[QTBridge] Desktop bridge init failed:', err)
      resolve(null)
    }
  })
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Get the AppBridge instance.  Returns null in browser/web mode.
 *
 * The first call performs async initialisation; subsequent calls
 * return the cached result immediately.
 */
export async function getBridge(): Promise<AppBridge | null> {
  if (_bridge !== null) return _bridge
  if (!window.qt)        return null   // browser / web mode

  if (!_initPromise) {
    _initPromise = _initDesktopBridge()
  }
  return _initPromise
}

/** True when running inside the PyQt6 WebEngine container. */
export function isDesktopMode(): boolean {
  return typeof window !== 'undefined' && Boolean(window.qt)
}

// ---------------------------------------------------------------------------
// Convenience signal helpers
// ---------------------------------------------------------------------------

/**
 * Subscribe to roomIdChanged signal (desktop only).
 * The callback is called with the new room ID string (empty = no room).
 */
export async function onRoomIdChanged(
  callback: (roomId: string) => void
): Promise<void> {
  const bridge = await getBridge()
  if (bridge) {
    bridge.roomIdChanged.connect(callback)
  }
}

/**
 * Subscribe to systemStatusChanged signal (desktop only).
 */
export async function onSystemStatusChanged(
  callback: (status: string) => void
): Promise<void> {
  const bridge = await getBridge()
  if (bridge) {
    bridge.systemStatusChanged.connect(callback)
  }
}

/**
 * Subscribe to tokenInfoChanged signal (desktop only).
 */
export async function onTokenInfoChanged(
  callback: (info: string) => void
): Promise<void> {
  const bridge = await getBridge()
  if (bridge) {
    bridge.tokenInfoChanged.connect(callback)
  }
}
