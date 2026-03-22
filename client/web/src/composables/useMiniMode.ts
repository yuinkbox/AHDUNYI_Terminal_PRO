/**
 * 全局迷你浮窗状态 — 模块级单例 ref。
 * 之所以不用 provide/inject（Vue 只支持父→子方向），
 * 而直接导出一个响应式 ref，使 MainLayout 和 RealTimePatrolPage
 * 都能读写同一个值。
 */
import { ref } from 'vue'

export const isMiniMode = ref(false)
