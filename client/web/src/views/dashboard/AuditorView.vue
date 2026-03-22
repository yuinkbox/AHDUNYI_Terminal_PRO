<template>
  <div class="auditor-view">

    <!-- 顶部欢迎横幅 -->
    <div class="welcome-banner">
      <div class="banner-left">
        <div class="greeting">
          <span class="greeting-text">{{ greetingText }}，{{ userFullName }}</span>
          <a-tag class="role-badge" color="blue">审核员</a-tag>
        </div>
        <div class="banner-sub">{{ todayDateStr }} · 今日工作概览</div>
      </div>
      <div class="banner-right">
        <div v-if="todayTask" class="shift-info">
          <div class="shift-item">
            <span class="shift-label">当前任务</span>
            <a-tag :color="channelColorMap[todayTask.task_channel] || 'blue'" size="medium">
              {{ getTaskChannelLabel(todayTask.task_channel) }}
            </a-tag>
          </div>
          <div class="shift-item">
            <span class="shift-label">班次</span>
            <a-tag :color="shiftColorMap[todayTask.shift_type] || 'gray'" size="medium">
              {{ getShiftTypeLabel(todayTask.shift_type) }}
            </a-tag>
          </div>
        </div>
        <div v-else-if="!taskLoading" class="no-shift">
          <icon-calendar />
          <span>今日暂未分配任务</span>
        </div>
      </div>
    </div>

    <!-- 今日核心数据 -->
    <div class="section-title">
      <icon-thunderbolt />
      <span>今日数据</span>
      <a-spin v-if="taskLoading" :size="14" style="margin-left:8px" />
    </div>

    <div class="metrics-grid">
      <!-- 已审场次 -->
      <div class="metric-card">
        <div class="metric-icon green">
          <icon-check-circle />
        </div>
        <div class="metric-body">
          <div class="metric-value">{{ todayTask?.reviewed_count ?? 0 }}</div>
          <div class="metric-label">已审场次</div>
        </div>
        <div class="metric-trend">
          <icon-arrow-rise class="trend-up" />
        </div>
      </div>

      <!-- 违规拦截 -->
      <div class="metric-card">
        <div class="metric-icon red">
          <icon-exclamation-circle />
        </div>
        <div class="metric-body">
          <div class="metric-value red">{{ todayTask?.violation_count ?? 0 }}</div>
          <div class="metric-label">违规拦截</div>
        </div>
        <div class="metric-trend">
          <icon-arrow-rise class="trend-up" />
        </div>
      </div>

      <!-- 在岗时长 -->
      <div class="metric-card wide">
        <div class="metric-icon blue">
          <icon-clock-circle />
        </div>
        <div class="metric-body">
          <div class="metric-value blue mono">{{ formatDurationHMS(todayTask?.work_duration ?? 0) }}</div>
          <div class="metric-label">今日直播巡查时长</div>
        </div>
        <div class="goto-patrol" @click="goToPatrol">
          <icon-live-broadcast />
          <span>前往直播巡查计时</span>
          <icon-arrow-right class="arrow-icon" />
        </div>
      </div>
    </div>

    <!-- 本周统计 -->
    <div class="section-title">
      <icon-bar-chart />
      <span>本周统计</span>
    </div>

    <div class="weekly-grid">
      <div class="weekly-card">
        <div class="weekly-header">
          <icon-check-circle class="icon-green" />
          <span>已审场次</span>
        </div>
        <div class="weekly-value">{{ weeklyStats.total_reviewed }}</div>
        <div class="weekly-sub">本周累计</div>
        <div class="weekly-bar">
          <div class="weekly-bar-fill green" :style="{ width: weeklyBarWidth(weeklyStats.total_reviewed, 200) }"></div>
        </div>
      </div>

      <div class="weekly-card">
        <div class="weekly-header">
          <icon-exclamation-circle class="icon-red" />
          <span>违规拦截</span>
        </div>
        <div class="weekly-value red">{{ weeklyStats.total_violations }}</div>
        <div class="weekly-sub">本周累计</div>
        <div class="weekly-bar">
          <div class="weekly-bar-fill red" :style="{ width: weeklyBarWidth(weeklyStats.total_violations, 50) }"></div>
        </div>
      </div>

      <div class="weekly-card">
        <div class="weekly-header">
          <icon-clock-circle class="icon-blue" />
          <span>在岗时长</span>
        </div>
        <div class="weekly-value blue">{{ Math.round(weeklyStats.total_duration / 60) }}</div>
        <div class="weekly-sub">分钟 · 本周累计</div>
        <div class="weekly-bar">
          <div class="weekly-bar-fill blue" :style="{ width: weeklyBarWidth(weeklyStats.total_duration / 60, 3000) }"></div>
        </div>
      </div>

      <div class="weekly-card">
        <div class="weekly-header">
          <icon-file-list class="icon-purple" />
          <span>完成任务</span>
        </div>
        <div class="weekly-value purple">{{ weeklyStats.task_count }}</div>
        <div class="weekly-sub">本周累计</div>
        <div class="weekly-bar">
          <div class="weekly-bar-fill purple" :style="{ width: weeklyBarWidth(weeklyStats.task_count, 20) }"></div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Message } from '@arco-design/web-vue'
import { rbacApi, getTaskChannelLabel, getShiftTypeLabel } from '@/api/rbac'
import { auth } from '@/utils/auth'

const router = useRouter()

const todayTask   = ref<any>(null)
const taskLoading = ref(false)
const weeklyStats = ref({ total_reviewed: 0, total_violations: 0, total_duration: 0, task_count: 0 })

const channelColorMap: Record<string, string> = {
  image: 'blue', chat: 'cyan', video: 'purple', live: 'orange',
}
const shiftColorMap: Record<string, string> = {
  morning: 'gold', afternoon: 'lime', night: 'blue',
}

const userFullName = computed(() => auth.getUserInfo()?.full_name || '同学')

const greetingText = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return '早上好'
  if (h < 18) return '下午好'
  return '晚上好'
})

const todayDateStr = computed(() => {
  const d = new Date()
  const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日 ${days[d.getDay()]}`
})

const formatDurationHMS = (seconds: number): string => {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

const weeklyBarWidth = (value: number, max: number): string => {
  const pct = Math.min(Math.round((value / max) * 100), 100)
  return `${Math.max(pct, 4)}%`
}

const goToPatrol = () => router.push('/risk-audit/realtime')

const loadData = async () => {
  taskLoading.value = true
  try {
    const res = await rbacApi.getMyTasks()
    todayTask.value = res.today_tasks?.[0] ?? null
    if (res.weekly_stats) weeklyStats.value = res.weekly_stats
  } catch {
    Message.error('加载任务信息失败')
  } finally {
    taskLoading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.auditor-view {
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ============================
   欢迎横幅
   ============================ */
.welcome-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 28px;
  border-radius: 12px;
  background: linear-gradient(135deg, #1664ff 0%, #0e42d2 60%, #5b3de8 100%);
  color: #fff;
  box-shadow: 0 4px 20px rgba(22, 100, 255, 0.30);
  flex-wrap: wrap;
  gap: 16px;
}

.greeting {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.greeting-text {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 0.3px;
}

.role-badge {
  background: rgba(255, 255, 255, 0.2) !important;
  border-color: rgba(255, 255, 255, 0.3) !important;
  color: #fff !important;
  font-size: 12px;
}

.banner-sub {
  font-size: 13px;
  opacity: 0.75;
  margin-top: 2px;
}

.banner-right {
  display: flex;
  align-items: center;
}

.shift-info {
  display: flex;
  gap: 24px;
  align-items: center;
}

.shift-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.shift-label {
  font-size: 11px;
  opacity: 0.7;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.no-shift {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  opacity: 0.8;
}

/* ============================
   小节标题
   ============================ */
.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-1);
  padding-left: 4px;
}

/* ============================
   今日指标卡片
   ============================ */
.metrics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 2fr;
  gap: 16px;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  background: var(--color-bg-2);
  border-radius: 12px;
  border: 1px solid var(--color-border-1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: box-shadow 0.2s, transform 0.2s;
  position: relative;
  overflow: hidden;
}

.metric-card:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.10);
  transform: translateY(-2px);
}

.metric-card.wide {
  cursor: pointer;
}

.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}

.metric-icon.green  { background: rgba(22, 100, 255, 0.12); color: #1664ff; }
.metric-icon.red    { background: rgba(245, 63, 63, 0.12);  color: #f53f3f; }
.metric-icon.blue   { background: rgba(22, 100, 255, 0.12); color: #1664ff; }

.metric-body { flex: 1; }

.metric-value {
  font-size: 36px;
  font-weight: 700;
  color: var(--color-text-1);
  line-height: 1.1;
}

.metric-value.red   { color: #f53f3f; }
.metric-value.blue  { color: #1664ff; }
.metric-value.blue.mono { color: #1664ff; }
.metric-value.mono  {
  font-family: 'SF Mono', 'Cascadia Code', Monaco, monospace;
  font-size: 28px;
}

.metric-label {
  font-size: 13px;
  color: var(--color-text-3);
  margin-top: 4px;
}

.metric-trend {
  font-size: 20px;
  color: var(--color-text-4);
}

.trend-up { color: #1664ff; }

.goto-patrol {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  background: #1664ff;
  padding: 10px 18px;
  border-radius: 8px;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.2s, box-shadow 0.2s, transform 0.15s;
  flex-shrink: 0;
  box-shadow: 0 4px 14px rgba(22, 100, 255, 0.40);
  letter-spacing: 0.2px;
}

.goto-patrol:hover {
  background: #0e42d2;
  box-shadow: 0 6px 20px rgba(22, 100, 255, 0.55);
  transform: translateY(-1px);
}

.goto-patrol:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(22, 100, 255, 0.35);
}

.arrow-icon {
  font-size: 14px;
  margin-left: 2px;
}

/* ============================
   本周统计卡片
   ============================ */
.weekly-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.weekly-card {
  padding: 20px 20px 16px;
  background: var(--color-bg-2);
  border-radius: 12px;
  border: 1px solid var(--color-border-1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: box-shadow 0.2s, transform 0.2s;
}

.weekly-card:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.10);
  transform: translateY(-2px);
}

.weekly-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--color-text-2);
  margin-bottom: 12px;
  font-weight: 500;
}

.icon-green  { color: #1664ff; }
.icon-red    { color: #f53f3f; }
.icon-blue   { color: #1664ff; }
.icon-purple { color: #1664ff; }

.weekly-value {
  font-size: 40px;
  font-weight: 700;
  color: var(--color-text-1);
  line-height: 1;
  margin-bottom: 4px;
}

.weekly-value.red    { color: #f53f3f; }
.weekly-value.blue   { color: #1664ff; }
.weekly-value.purple { color: #1664ff; }

.weekly-sub {
  font-size: 12px;
  color: var(--color-text-4);
  margin-bottom: 14px;
}

.weekly-bar {
  height: 4px;
  background: var(--color-fill-3);
  border-radius: 2px;
  overflow: hidden;
}

.weekly-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.weekly-bar-fill.green  { background: #1664ff; }
.weekly-bar-fill.red    { background: #f53f3f; }
.weekly-bar-fill.blue   { background: #1664ff; }
.weekly-bar-fill.purple { background: #1664ff; }

/* 响应式 */
@media (max-width: 1100px) {
  .metrics-grid { grid-template-columns: 1fr 1fr; }
  .metric-card.wide { grid-column: span 2; }
  .weekly-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 680px) {
  .metrics-grid { grid-template-columns: 1fr; }
  .metric-card.wide { grid-column: unset; }
  .weekly-grid { grid-template-columns: repeat(2, 1fr); }
  .welcome-banner { flex-direction: column; align-items: flex-start; }
  .shift-info { flex-wrap: wrap; gap: 16px; }
}
</style>
