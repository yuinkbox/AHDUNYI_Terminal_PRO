<template>
  <div :class="['realtime-page', { 'mini-active': isMiniMode }]">

    <!-- ===== 迷你浮窗模式 ===== -->
    <template v-if="isMiniMode">
      <div class="mini-panel">

        <!-- 顶栏：状态 + 控制 -->
        <div class="mini-header">
          <div class="mini-status-row">
            <span class="mini-dot" :class="`dot-${workStatus}`"></span>
            <span class="mini-status-text">{{ statusText }}</span>
            <span class="mini-task-chip" v-if="todayTask">
              {{ getTaskChannelLabel(todayTask.task_channel) }}
            </span>
          </div>
          <div class="mini-controls">
            <button
              class="mini-icon-btn"
              :class="{ 'active-pin': isAlwaysOnTop }"
              @click="toggleAlwaysOnTop"
              :title="isAlwaysOnTop ? '取消置顶' : '窗口置顶'"
            ><icon-pushpin /></button>
            <button class="mini-icon-btn" @click="exitMiniMode" title="还原窗口">
              <icon-expand />
            </button>
          </div>
        </div>

        <!-- 房间号 + 用户ID -->
        <div v-if="currentRoomId || currentUserId" class="mini-ids-row">
          <div v-if="currentRoomId" class="mini-room-card" @click="copyRoomId">
            <icon-live-broadcast :size="12" class="mini-room-icon" />
            <span class="mini-room-label">房间</span>
            <span class="mini-room-id">#{{ currentRoomId }}</span>
          </div>
          <div v-if="currentUserId" class="mini-room-card mini-user-card" @click="copyUserId">
            <icon-user :size="12" class="mini-room-icon" />
            <span class="mini-room-label">主播</span>
            <span class="mini-room-id">#{{ currentUserId }}</span>
          </div>
        </div>
        <div v-else class="mini-room-empty">
          <icon-desktop :size="12" />
          <span>未检测到直播间</span>
        </div>

        <!-- 计时器 -->
        <div class="mini-timer-wrap">
          <div class="mini-timer">{{ formatTime(totalSeconds) }}</div>
          <div class="mini-timer-label">当班计时</div>
        </div>

        <!-- 计数行 -->
        <div class="mini-stats-row">
          <div class="mini-stat-box">
            <div class="mini-stat-num">{{ reviewedCount }}</div>
            <div class="mini-stat-label">已审场次</div>
          </div>
          <div class="mini-stat-sep"></div>
          <div class="mini-stat-box">
            <div class="mini-stat-num danger">{{ violationCount }}</div>
            <div class="mini-stat-label">违规拦截</div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="mini-actions">
          <a-button type="primary" long @click="switchRoom"
            :disabled="!canSwitchRoom || isCoolingDown" class="mini-btn">
            <icon-swap />
            切房审查
            <span class="mini-shortcut">Alt+空格</span>
          </a-button>

          <a-button v-if="!isHandlingViolation" type="primary" status="danger" long
            @click="markViolation" :disabled="!canMarkViolation" class="mini-btn">
            <icon-flag />违规处置<span class="mini-shortcut">Alt+1</span>
          </a-button>
          <a-button v-else type="outline" status="success" long
            @click="completeViolation" class="mini-btn">
            <icon-check-circle />处置完成<span class="mini-shortcut">Alt+1</span>
          </a-button>

          <a-button v-if="!isSuspended" type="outline" status="warning" long
            @click="suspendWork" :disabled="!canSuspend" class="mini-btn">
            <icon-pause-circle />挂起休整<span class="mini-shortcut">Alt+2</span>
          </a-button>
          <a-button v-else type="primary" status="warning" long
            @click="resumeWork" class="mini-btn">
            <icon-play-circle />恢复工作<span class="mini-shortcut">Alt+2</span>
          </a-button>

          <div class="mini-stop-row">
            <a-button type="text" status="danger" long @click="stopWorkflow" class="mini-stop-btn">
              <icon-stop />结束工作流
            </a-button>
          </div>
        </div>

      </div>
    </template>

    <!-- ===== 正常模式 ===== -->
    <template v-else>
      <!-- 页头 -->
    <div class="page-header">
        <div class="header-left">
          <icon-eye :size="24" />
          <span class="page-title">直播监测</span>
          <a-badge
            :status="monitorStatus === 'running' ? 'processing' : 'default'"
            :text="monitorStatus === 'running' ? '运行中' : '已暂停'"
          />
        </div>
        <a-space>
          <!-- 置顶开关按钮（始终可见） -->
          <a-tooltip :content="isAlwaysOnTop ? '取消置顶' : '窗口置顶'">
            <a-button
              :class="['pin-toggle-btn', { 'pin-toggle-active': isAlwaysOnTop }]"
              @click="toggleAlwaysOnTop"
            >
              <template #icon><icon-pushpin /></template>
              {{ isAlwaysOnTop ? '已置顶' : '置顶' }}
            </a-button>
          </a-tooltip>
          <!-- 巡查中时显示"进入迷你浮窗"按钮 -->
          <a-button
            v-if="isWorking"
            @click="enterMiniMode"
            class="mini-enter-btn"
          >
            <template #icon><icon-shrink /></template>
            迷你浮窗
          </a-button>
          <a-button @click="loadTasks" :loading="loading">
            <template #icon><icon-refresh /></template>刷新
          </a-button>
          <a-button
            v-if="permissionStore.can('action:dispatch_task')"
            type="primary"
            @click="showDispatchModal"
          >
            <template #icon><icon-send /></template>派发任务
          </a-button>
      </a-space>
    </div>

      <!-- 计件器 -->
      <div class="blind-checker">
        <!-- 当班任务信息条 -->
        <div class="task-banner" v-if="todayTask && todayTask.task_channel">
          <div class="task-info-bar">
            <div class="task-info-left">
              <div class="task-dot"></div>
              <icon-file-list :size="13" class="task-biz-icon" />
              <span class="task-label">今日当班业务</span>
              <a-tag :color="channelColor(todayTask.task_channel)" size="medium" class="task-channel-tag">
                {{ getTaskChannelLabel(todayTask.task_channel) }}
              </a-tag>
              <div class="task-divider"></div>
              <span class="task-meta" v-if="todayTask.shift_type">
                <icon-clock-circle :size="13" />
                {{ getShiftTypeLabel(todayTask.shift_type) }}
              </span>
              <span class="task-meta" v-if="todayTask.is_completed">
                <icon-check-circle :size="13" style="color:#00b42a" />
                已完成
              </span>
              <span class="task-meta" v-else>
                <icon-loading :size="13" style="color:#1664ff" />
                进行中
              </span>
            </div>
            <div class="task-info-right" v-if="todayTask.reviewed_count > 0 || todayTask.violation_count > 0">
              <span class="task-stat">已审 <strong>{{ todayTask.reviewed_count }}</strong> 场</span>
              <span class="task-stat-sep">·</span>
              <span class="task-stat">违规 <strong style="color:#f53f3f">{{ todayTask.violation_count }}</strong> 次</span>
            </div>
          </div>
        </div>

        <!-- 主卡片：计时区 + 操作区 -->
        <div class="main-card">

          <!-- 上半区：状态 + 计时 + 计数 -->
          <div class="main-top">
            <div class="top-left">
              <!-- 状态行：状态徽标 + 房间号 -->
              <div class="status-row">
                <div class="status-badge" :class="`status-${workStatus}`">
                  <span class="status-dot-ring"></span>
                  <span class="status-badge-text">{{ statusText }}</span>
                </div>
                <!-- 房间号 -->
                <div class="room-id-display" v-if="currentRoomId" @click="copyRoomId" title="点击复制房间号">
                  <icon-live-broadcast :size="14" class="room-icon" />
                  <span class="room-label">房间</span>
                  <span class="room-number">#{{ currentRoomId }}</span>
                  <icon-copy :size="12" class="room-copy" />
                </div>
                <!-- 用户ID -->
                <div class="room-id-display user-id-display" v-if="currentUserId" @click="copyUserId" title="点击复制用户ID">
                  <icon-user :size="14" class="room-icon" />
                  <span class="room-label">主播</span>
                  <span class="room-number">#{{ currentUserId }}</span>
                  <icon-copy :size="12" class="room-copy" />
                </div>
                <div class="room-id-empty" v-if="!currentRoomId">
                  <icon-desktop :size="13" />
                  <span>未检测到直播间</span>
                </div>
              </div>
              <!-- 大计时器 -->
              <div class="big-timer">{{ formatTime(totalSeconds) }}</div>
              <div class="timer-hint">{{ statusDesc }}</div>
            </div>

            <div class="top-right">
              <div class="count-box">
                <div class="count-num">{{ reviewedCount }}</div>
                <div class="count-lbl">已审场次</div>
                <div class="count-hint">切房审查 +1</div>
              </div>
              <div class="count-sep"></div>
              <div class="count-box">
                <div class="count-num danger">{{ violationCount }}</div>
                <div class="count-lbl">违规拦截</div>
                <div class="count-hint">违规处置 +1</div>
              </div>
            </div>
          </div>

          <!-- 分割线 -->
          <div class="main-divider"></div>

          <!-- 下半区：操作按钮 -->
          <div class="main-actions">
            <!-- 接入/结束 -->
            <div class="act-col act-col-workflow">
              <a-button v-if="!isWorking" type="primary" size="large" long
                @click="startWorkflow" :loading="startingWorkflow" class="act-btn act-btn-start">
                <icon-play-circle /> 接入工作流
              </a-button>
              <a-button v-else type="outline" status="danger" size="large" long
                @click="stopWorkflow" class="act-btn">
                <icon-stop /> 结束工作流
              </a-button>
              <div class="act-hint">接入后开始计时，结束时自动上报</div>
            </div>

            <!-- 切房 -->
            <div class="act-col">
              <a-button type="primary" size="large" long @click="switchRoom"
                :disabled="!canSwitchRoom || isCoolingDown" class="act-btn act-btn-switch">
                <icon-swap />
                切房审查
                <span class="act-shortcut">Alt+空格</span>
              </a-button>
              <div class="act-hint">
                已审 +1
                <span v-if="isCoolingDown" class="cooling-tag">冷却中</span>
              </div>
            </div>

            <!-- 违规 -->
            <div class="act-col">
              <a-button v-if="!isHandlingViolation" type="primary" status="danger" size="large" long
                @click="markViolation" :disabled="!canMarkViolation" class="act-btn">
                <icon-flag />违规处置<span class="act-shortcut">Alt+1</span>
              </a-button>
              <a-button v-else type="outline" status="success" size="large" long
                @click="completeViolation" class="act-btn">
                <icon-check-circle />处置完成<span class="act-shortcut">Alt+1</span>
              </a-button>
              <div class="act-hint">切为处置时违规 +1，完成后回到巡查</div>
            </div>

            <!-- 挂起 -->
            <div class="act-col">
              <a-button v-if="!isSuspended" type="outline" status="warning" size="large" long
                @click="suspendWork" :disabled="!canSuspend" class="act-btn">
                <icon-pause-circle />挂起休整<span class="act-shortcut">Alt+2</span>
              </a-button>
              <a-button v-else type="primary" status="warning" size="large" long
                @click="resumeWork" class="act-btn">
                <icon-play-circle />恢复工作<span class="act-shortcut">Alt+2</span>
              </a-button>
              <div class="act-hint">挂起时计时器暂停</div>
            </div>
          </div>

          <!-- 操作时间轴日志 -->
          <div class="timeline-section" v-if="actionLog.length">
            <div class="timeline-header">
              <icon-history :size="14" />
              <span>操作记录</span>
              <span class="timeline-count">{{ actionLog.length }} 条</span>
            </div>
            <div class="timeline-list">
              <div v-for="item in actionLog" :key="item.id" class="timeline-item">
                <span class="tl-dot" :class="`tl-dot-${getActionColor(item.action)}`"></span>
                <span class="tl-time">{{ item.timestamp }}</span>
                <a-tag :color="getActionColor(item.action)" size="small" class="tl-action">{{ item.action }}</a-tag>
                <span class="tl-detail">{{ item.details }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 今日汇总 + 任务列表 -->
      <div class="bottom-section">
        <!-- 汇总数字条 -->
        <div class="summary-bar">
          <div class="summary-item">
            <icon-file-list :size="16" class="summary-icon" />
            <span class="summary-val">{{ stats.totalTasks }}</span>
            <span class="summary-lbl">今日任务</span>
          </div>
          <div class="summary-sep"></div>
          <div class="summary-item">
            <icon-check-circle :size="16" class="summary-icon blue" />
            <span class="summary-val blue">{{ stats.totalReviewed }}</span>
            <span class="summary-lbl">已审核</span>
          </div>
          <div class="summary-sep"></div>
          <div class="summary-item">
            <icon-exclamation-circle :size="16" class="summary-icon red" />
            <span class="summary-val red">{{ stats.totalViolations }}</span>
            <span class="summary-lbl">违规拦截</span>
          </div>
          <div class="summary-sep"></div>
          <div class="summary-item">
            <icon-clock-circle :size="16" class="summary-icon" />
            <span class="summary-val">{{ Math.round(stats.totalDuration / 60) }}</span>
            <span class="summary-lbl">在岗分钟</span>
          </div>
        </div>

        <!-- 今日任务列表 -->
        <a-card class="table-card">
          <template #title>
            <div class="table-title">
              <icon-unordered-list :size="15" />
              <span>今日任务列表</span>
            </div>
          </template>
          <a-table :data="todayTasks" :loading="loading" :pagination="false" row-key="id" stripe size="small">
            <template #columns>
              <a-table-column title="审核通道" data-index="task_channel">
                <template #cell="{ record }">
                  <a-tag :color="channelColor(record.task_channel)" size="small">{{ channelLabel(record.task_channel) }}</a-tag>
                </template>
              </a-table-column>
              <a-table-column title="班次" data-index="shift_type">
                <template #cell="{ record }">{{ shiftLabel(record.shift_type) }}</template>
              </a-table-column>
              <a-table-column title="已审" data-index="reviewed_count" :width="70" />
              <a-table-column title="违规" data-index="violation_count" :width="70" />
              <a-table-column title="状态" :width="90">
                <template #cell="{ record }">
                  <a-badge :status="record.is_completed ? 'success' : 'processing'"
                    :text="record.is_completed ? '已完成' : '进行中'" />
                </template>
              </a-table-column>
              <a-table-column title="" :width="80">
                <template #cell="{ record }">
                  <a-button v-if="!record.is_completed" type="text" size="mini"
                    @click="completeTask(record.id)">完成</a-button>
                </template>
              </a-table-column>
            </template>
          </a-table>
          <div v-if="!loading && todayTasks.length === 0" class="empty-state">
            <a-empty description="今日暂无分配任务">
              <template #image><icon-inbox :size="40" /></template>
            </a-empty>
          </div>
        </a-card>
      </div>
    </template>

    <!-- 派发 / 违规弹窗：须挂在迷你与正常模式之外，否则迷你窗内未挂载无法显示 -->
    <a-modal v-model:visible="dispatchModal.visible" title="智能任务派发" :width="600" @ok="submitDispatch" :ok-loading="dispatchModal.loading" ok-text="开始派发">
      <a-form :model="dispatchForm" layout="vertical">
        <a-form-item label="派发日期" required><a-input v-model="dispatchForm.shift_date" placeholder="YYYY-MM-DD" /></a-form-item>
        <a-form-item label="班次" required>
          <a-radio-group v-model="dispatchForm.shift_type" type="button">
            <a-radio value="morning">早班</a-radio><a-radio value="afternoon">中班</a-radio><a-radio value="night">晚班</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-form-item label="审核通道" required>
          <a-checkbox-group v-model="dispatchForm.required_channels">
            <a-checkbox value="image">图片审核</a-checkbox><a-checkbox value="chat">单聊审核</a-checkbox>
            <a-checkbox value="video">视频审核</a-checkbox><a-checkbox value="live">直播巡查</a-checkbox>
          </a-checkbox-group>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 违规处置弹窗：使用 teleport 挂载到 body，避免被迷你窗口挤占 -->
    <teleport to="body">
      <a-modal
        v-model:visible="violationModal.visible"
        title="违规处置上报"
        :width="520"
        @ok="submitViolation"
        :ok-loading="violationModal.loading"
        ok-text="确认处置"
        cancel-text="取消"
        :mask-closable="false"
      >
        <a-form :model="violationForm" layout="vertical">
          <a-form-item label="房间号">
            <a-input v-model="violationForm.room_id" placeholder="自动识别或手动输入">
              <template #prefix><icon-live-broadcast /></template>
            </a-input>
          </a-form-item>
          <a-form-item label="违规主播ID">
            <a-input v-model="violationForm.user_id" placeholder="自动识别或手动输入">
              <template #prefix><icon-user /></template>
            </a-input>
          </a-form-item>
          <a-form-item label="违规原因" required>
            <a-textarea
              v-model="violationForm.reason"
              placeholder="请描述违规行为（如：涉黄、低俗、诱导未成年人等）"
              :max-length="200"
              show-word-limit
              :auto-size="{ minRows: 3, maxRows: 5 }"
            />
          </a-form-item>
          <a-form-item label="处罚动作" required>
            <a-radio-group v-model="violationForm.action" type="button" size="large">
              <a-radio value="ban">
                <icon-stop /> 封禁
              </a-radio>
              <a-radio value="mute">
                <icon-mute /> 禁言
              </a-radio>
              <a-radio value="close_room">
                <icon-poweroff /> 关播
              </a-radio>
            </a-radio-group>
          </a-form-item>
        </a-form>
      </a-modal>
    </teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import { rbacApi, type TaskItem, getTaskChannelLabel, getShiftTypeLabel } from '@/api/rbac'
import { usePermissionStore } from '@/stores/permission'
import { useWorkflowStore } from '@/stores/workflow'
import { getBridge, isDesktopMode, onRoomInfoChanged, onViolationSubmitted } from '@/bridge/qt_channel'
import api from '@/api'
import { isMiniMode } from '@/composables/useMiniMode'
import { auth } from '@/utils/auth'

const permissionStore = usePermissionStore()
const workflowStore   = useWorkflowStore()

// ---- 房间/用户 ID 实时监测 ---------------------------------------------------
const currentRoomId = ref('')
const currentUserId = ref('')

async function initRoomMonitor() {
  // 仅在工作流激活后才允许更新 ID（阀门：未接入工作流时丢弃底层推送）
  await onRoomInfoChanged((raw: string) => {
    if (!isWorking.value) return  // 未接入工作流，拒绝更新
    try {
      const info = JSON.parse(raw)
      const newRoomId = info.room_id || ''
      const newUserId = info.user_id || ''
      if (newRoomId && newRoomId !== currentRoomId.value) {
        isHandlingViolation.value = false
      }
      currentRoomId.value = newRoomId
      currentUserId.value = newUserId
    } catch { /* 忽略解析失败 */ }
  })
}

function copyToClipboard(text: string, label: string) {
  if (!text) return
  const el = document.createElement('textarea')
  el.value = text
  el.style.cssText = 'position:fixed;top:0;left:0;opacity:0;pointer-events:none'
  document.body.appendChild(el)
  el.focus()
  el.select()
  let ok = false
  try { ok = document.execCommand('copy') } catch { /* ignore */ }
  document.body.removeChild(el)
  if (ok) {
    Message.success(`已复制${label}: ${text}`)
  } else {
    navigator.clipboard?.writeText(text)
      .then(() => Message.success(`已复制${label}: ${text}`))
      .catch(() => Message.error('复制失败，请手动记录'))
  }
}

function copyRoomId() { copyToClipboard(currentRoomId.value, '房间号') }
function copyUserId() { copyToClipboard(currentUserId.value, '用户ID') }

// ---- 违规处置弹窗 -----------------------------------------------------------
const violationModal = ref({ visible: false, loading: false })
const violationForm = ref({
  room_id: '',
  user_id: '',
  reason: '',
  action: 'ban' as 'ban' | 'mute' | 'close_room',
})

async function openViolationModal() {
  if (isDesktopMode() && isMiniMode.value) {
    const b = await getBridge()
    b?.openViolationPopup()
    return
  }
  violationForm.value.room_id = currentRoomId.value
  violationForm.value.user_id = currentUserId.value
  violationForm.value.reason = ''
  violationForm.value.action = 'ban'
  violationModal.value.visible = true
}

async function submitViolation() {
  const form = violationForm.value
  if (!form.reason.trim()) {
    Message.warning('请填写违规原因')
    return
  }

  violationModal.value.loading = true
  try {
    const userInfo = auth.getUserInfo()
    await api.post('/api/violation/report', {
      room_id:   form.room_id,
      user_id:   form.user_id,
      reason:    form.reason.trim(),
      action:    form.action,
      operator:  userInfo?.full_name || userInfo?.username || '未知',
      timestamp: new Date().toISOString(),
    })

    violationModal.value.visible = false
    workStatus.value = 'handling'
    isHandlingViolation.value = true
    violationCount.value++

    const actionLabel = { ban: '封禁', mute: '禁言', close_room: '关播' }[form.action]
    await addLog('违规处置', `房间${form.room_id} 用户${form.user_id} ${actionLabel} - ${form.reason}`)
    Message.success('违规处置已提交，已通知飞书群')
  } catch {
    Message.error('违规上报失败，请稍后重试')
  } finally {
    violationModal.value.loading = false
  }
}

// ---- 迷你模式 & 置顶 -------------------------------------------------------
const isAlwaysOnTop = ref(false)

async function enterMiniMode() {
  isMiniMode.value = true
  if (isDesktopMode()) {
    const bridge = await getBridge()
    bridge?.setMiniMode(true)
  }
}

async function exitMiniMode() {
  isMiniMode.value = false
  if (isDesktopMode()) {
    const bridge = await getBridge()
    bridge?.setMiniMode(false)
  }
}


async function toggleAlwaysOnTop() {
  isAlwaysOnTop.value = !isAlwaysOnTop.value
  if (isDesktopMode()) {
    const bridge = await getBridge()
    bridge?.setAlwaysOnTop(isAlwaysOnTop.value)
  }
}

// ---- 任务列表状态 -----------------------------------------------------------
const loading       = ref(false)
const todayTasks    = ref<TaskItem[]>([])
const monitorStatus = ref<'running' | 'paused'>('running')

const dispatchModal = ref({ visible: false, loading: false })
const dispatchForm  = ref({
  shift_date: new Date().toISOString().slice(0, 10),
  shift_type: 'morning',
  required_channels: [] as string[],
})

const stats = computed(() => ({
  totalTasks:      todayTasks.value.length,
  totalReviewed:   todayTasks.value.reduce((s, t) => s + t.reviewed_count, 0),
  totalViolations: todayTasks.value.reduce((s, t) => s + t.violation_count, 0),
  totalDuration:   todayTasks.value.reduce((s, t) => s + t.work_duration, 0),
}))

const channelLabel = (ch: string) => getTaskChannelLabel(ch)
const shiftLabel   = (st: string) => getShiftTypeLabel(st)
const channelColor = (ch: string): string =>
  ({ image: 'blue', chat: 'cyan', video: 'purple', live: 'orange' })[ch] ?? 'gray'

async function loadTasks() {
  loading.value = true
  try {
    // 直播巡查是审核员默认日常任务，无需派发，自动创建今日任务记录
    const liveTask = await rbacApi.getOrCreateLivePatrolTask()
    todayTask.value = liveTask
    workflowStore.todayTaskId = liveTask.id

    // 如果当前未在工作流中，从数据库恢复上次进度（断线续传）
    if (!isWorking.value) {
      workflowStore.reviewedCount  = liveTask.reviewed_count  || 0
      workflowStore.violationCount = liveTask.violation_count || 0
      workflowStore.totalSeconds   = liveTask.work_duration   || 0
    }

    // 同时加载完整任务列表（用于任务面板展示）
    const res = await rbacApi.getMyTasks()
    todayTasks.value = res.today_tasks
  } catch (err) {
    console.error('[Patrol] loadTasks failed:', err)
    Message.error('加载任务失败，请检查后端连接')
  } finally {
    loading.value = false
  }
}

async function completeTask(taskId: number) {
  await rbacApi.completeTask(taskId)
  Message.success('任务已标记完成')
  await loadTasks()
}

function showDispatchModal() { dispatchModal.value.visible = true }

async function submitDispatch() {
  if (!dispatchForm.value.required_channels.length) {
    Message.warning('请至少选择一个审核通道')
    return
  }
  dispatchModal.value.loading = true
  try {
    const res = await rbacApi.dispatchTasks({
      shift_date: dispatchForm.value.shift_date,
      shift_type: dispatchForm.value.shift_type as any,
      user_ids: [],
      required_channels: dispatchForm.value.required_channels as any,
    })
    Message.success(`派发完成：共 ${res.summary.total_assignments} 条任务`)
    dispatchModal.value.visible = false
    await loadTasks()
  } catch {
    Message.error('派发失败，请稍后重试')
  } finally {
    dispatchModal.value.loading = false
  }
}

// ---- 计件器状态 -------------------------------------------------------------
const MIN_STAY_TIME = 3000
const MAX_IDLE_TIME = 5 * 60 * 1000

// ---- 工作流核心状态（来自全局 Store，路由切换不丢失）--------------------
const workStatus          = computed({ get: () => workflowStore.workStatus,          set: v => { workflowStore.workStatus = v } })
const totalSeconds        = computed({ get: () => workflowStore.totalSeconds,        set: v => { workflowStore.totalSeconds = v } })
const reviewedCount       = computed({ get: () => workflowStore.reviewedCount,       set: v => { workflowStore.reviewedCount = v } })
const violationCount      = computed({ get: () => workflowStore.violationCount,      set: v => { workflowStore.violationCount = v } })
const isHandlingViolation = computed({ get: () => workflowStore.isHandlingViolation, set: v => { workflowStore.isHandlingViolation = v } })
const isSuspended         = computed({ get: () => workflowStore.isSuspended,         set: v => { workflowStore.isSuspended = v } })
const lastActionTime      = computed({ get: () => workflowStore.lastActionTime,      set: v => { workflowStore.lastActionTime = v } })

const startingWorkflow    = ref(false)
const isCoolingDown       = ref(false)
const afkTimer            = ref<ReturnType<typeof setInterval> | null>(null)
const todayTask           = ref<any>(null)

let workTimer: ReturnType<typeof setInterval> | null = null

const actionLog = ref<Array<{ id: number; timestamp: string; action: string; details: string }>>([])

const statusText = computed(() => workflowStore.statusText)
const statusColor = computed(() => ({ offline: 'gray', patrolling: 'green', handling: 'red', suspended: 'yellow' })[workflowStore.workStatus])
const statusDesc = computed(() => ({
  offline: '未接入工作流', patrolling: '正在巡查直播间', handling: '处理违规内容', suspended: '暂停计时，临时休整',
})[workflowStore.workStatus])

const isWorking        = computed(() => workflowStore.isWorking)
const canSwitchRoom    = computed(() => workflowStore.workStatus === 'patrolling')
const canMarkViolation = computed(() => workflowStore.workStatus === 'patrolling')
const canSuspend       = computed(() => workflowStore.workStatus === 'patrolling')

const formatTime = (seconds: number) => {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

const getCurrentTime = () => {
  const now = new Date()
  return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
}

const getActionColor = (action: string): string =>
  ({ '开始巡查': 'green', '结束巡查': 'gray', '切房审查': 'blue', '违规标记': 'red', '处置完成': 'green', '挂起休整': 'yellow', '恢复工作': 'blue' })[action] ?? 'gray'

const updateLastActionTime = () => { workflowStore.lastActionTime = Date.now() }

const checkCoolingDown = (): boolean => {
  const timeSince = Date.now() - lastActionTime.value
  if (timeSince < MIN_STAY_TIME) {
    isCoolingDown.value = true
    Message.warning(`巡查切换过快，请保证单场审核质量 (冷却中，还需${Math.ceil((MIN_STAY_TIME - timeSince) / 1000)}秒)`)
    setTimeout(() => { isCoolingDown.value = false }, MIN_STAY_TIME - timeSince)
    return true
  }
  return false
}

const startAFKDetection = () => {
  if (afkTimer.value) clearInterval(afkTimer.value)
  afkTimer.value = setInterval(() => {
    if (workflowStore.workStatus === 'patrolling' && !workflowStore.isSuspended) {
      if (Date.now() - workflowStore.lastActionTime > MAX_IDLE_TIME) {
        workflowStore.workStatus = 'suspended'
        workflowStore.isSuspended = true
        Modal.warning({ title: '防挂机检测', content: '检测到长时间未操作，已自动挂起并暂停计时！', okText: '知道了', hideCancel: true })
        addLog('自动挂起', '系统检测到长时间未操作，自动暂停计时')
      }
    }
  }, 30000)
}

const stopAFKDetection = () => {
  if (afkTimer.value) { clearInterval(afkTimer.value); afkTimer.value = null }
}

const addLog = async (action: string, details: string) => {
  actionLog.value.unshift({ id: Date.now(), timestamp: getCurrentTime(), action, details })
  if (actionLog.value.length > 50) actionLog.value = actionLog.value.slice(0, 50)
  updateLastActionTime()
  await rbacApi.logAction(action, details)
}

const startTimer = () => {
  if (workTimer) clearInterval(workTimer)
  workTimer = setInterval(() => {
    if (!workflowStore.isSuspended) {
      workflowStore.totalSeconds++
      if (workflowStore.totalSeconds % 10 === 0 && todayTask.value) updateTaskProgress()
    }
  }, 1000)
}

const stopTimer = () => {
  if (workTimer) { clearInterval(workTimer); workTimer = null }
}

const updateTaskProgress = async () => {
  if (!todayTask.value) {
    console.warn('[Patrol] updateTaskProgress skipped: todayTask is null')
    return
  }
  try {
    await rbacApi.updateTaskProgress(todayTask.value.id, {
      reviewed_count: workflowStore.reviewedCount,
      violation_count: workflowStore.violationCount,
      work_duration: workflowStore.totalSeconds,
      is_completed: workflowStore.workStatus === 'offline',
    })
  } catch (err) {
    console.error('[Patrol] updateTaskProgress failed:', err)
  }
}

const startWorkflow = async () => {
  startingWorkflow.value = true
  setTimeout(async () => {
    workflowStore.workStatus = 'patrolling'
    workflowStore.isSuspended = false
    workflowStore.isHandlingViolation = false
    // 记录当前任务 ID 到 Store，供路由切换后恢复
    workflowStore.todayTaskId = todayTask.value?.id ?? null
    startingWorkflow.value = false
    workflowStore.lastActionTime = Date.now()
    startTimer()
    startAFKDetection()
    await addLog('开始巡查', '接入工作流，开始计时')
    Message.success('工作流已接入，开始计时')
    enterMiniMode()
  }, 300)
}

const stopWorkflow = () => {
  Modal.confirm({
    title: '结束工作流', content: '确定要结束当前工作流吗？所有计时将停止。',
    okText: '确认结束', cancelText: '取消',
    onOk: async () => {
      stopTimer()
      stopAFKDetection()
      await addLog('结束巡查', `本次巡查总时长: ${formatTime(workflowStore.totalSeconds)}`)
      if (todayTask.value) {
        await rbacApi.updateTaskProgress(todayTask.value.id, {
          reviewed_count: workflowStore.reviewedCount,
          violation_count: workflowStore.violationCount,
          work_duration: workflowStore.totalSeconds,
          is_completed: true,
        })
      }
      // 标记工作流为 offline，但保留数据供本页面继续展示
      // 不调用 reset()，避免数据瞬间清零
      workflowStore.workStatus = 'offline'
      workflowStore.isSuspended = false
      workflowStore.isHandlingViolation = false
      workflowStore.clearPersist()
      localStorage.removeItem('blind_checker_log')
      currentRoomId.value = ''
      currentUserId.value = ''
      Message.success('工作流已结束')
      exitMiniMode()
      if (isAlwaysOnTop.value) {
        isAlwaysOnTop.value = false
        const bridge = await getBridge()
        bridge?.setAlwaysOnTop(false)
      }
    },
  })
}

const switchRoom = async () => {
  if (!canSwitchRoom.value || checkCoolingDown()) return
  workflowStore.reviewedCount++
  await addLog('切房审查', `已审场次: ${workflowStore.reviewedCount}`)
  Message.success(`切房完成，已审场次: ${workflowStore.reviewedCount}`)
}

const markViolation = () => {
  if (!canMarkViolation.value) return
  void openViolationModal()
}

const completeViolation = async () => {
  workflowStore.workStatus = 'patrolling'
  workflowStore.isHandlingViolation = false
  await addLog('处置完成', '违规处置完成')
  Message.success('违规处置完成，返回巡查状态')
}

const suspendWork = async () => {
  if (!canSuspend.value) return
  workflowStore.workStatus = 'suspended'
  workflowStore.isSuspended = true
  // 挂起时强制同步进度到后端
  if (todayTask.value) {
    try {
      await rbacApi.updateTaskProgress(todayTask.value.id, {
        reviewed_count: workflowStore.reviewedCount,
        violation_count: workflowStore.violationCount,
        work_duration: workflowStore.totalSeconds,
        is_completed: false,
      })
    } catch { /* 静默 */ }
  }
  workflowStore.persist()
  await addLog('挂起休整', '暂停计时，临时休整')
  Message.info('工作已挂起，计时器暂停')
}

const resumeWork = async () => {
  workflowStore.workStatus = 'patrolling'
  workflowStore.isSuspended = false
  await addLog('恢复工作', '恢复计时，继续巡查')
  Message.success('已恢复工作，继续计时')
}

const handleKeyDown = (event: KeyboardEvent) => {
  if (workStatus.value !== 'patrolling' && workStatus.value !== 'handling') return
  if (event.altKey && event.code === 'Space') { event.preventDefault(); if (canSwitchRoom.value) switchRoom() }
  if (event.altKey && event.code === 'Digit1') { event.preventDefault(); if (isHandlingViolation.value) completeViolation(); else if (canMarkViolation.value) markViolation() }
  if (event.altKey && event.code === 'Digit2') { event.preventDefault(); if (isSuspended.value) resumeWork(); else if (canSuspend.value) suspendWork() }
  updateLastActionTime()
}

onMounted(async () => {
  // ── 工作流状态兼容逻辑 ───────────────────────────────────────────
  // 尝试从 Store 恢复活跃工作流（路由切换回来场景）
  // 如果 Store 中已有激活状态（isWorking），直接复用，不清零
  // 如果 Store 无活跃工作流，再尝试从 localStorage 恢复（页面刷新场景）
  // 如果都没有，则强制重置为干净状态（新登录场景）
  const hasActiveWorkflow = workflowStore.isWorking || workflowStore.restore()

  if (!hasActiveWorkflow) {
    // 新登录或无工作流：强制重置
    workflowStore.reset()
    currentRoomId.value = ''
    currentUserId.value = ''
    actionLog.value = []
    localStorage.removeItem('blind_checker_log')
  } else {
    // 有活跃工作流：恢复计时器
    if (workflowStore.workStatus === 'patrolling' && !workflowStore.isSuspended) {
      startTimer()
      startAFKDetection()
    }
    // 恢复操作日志
    const savedLog = localStorage.getItem('blind_checker_log')
    if (savedLog) { try { actionLog.value = JSON.parse(savedLog) } catch { /* ignore */ } }
  }

  await loadTasks()

  // 若工作流已激活但 todayTask 未绑定，尝试从 store 恢复任务 ID
  if (hasActiveWorkflow && !todayTask.value && workflowStore.todayTaskId) {
    const res = await rbacApi.getMyTasks().catch(() => null)
    if (res) {
      todayTask.value = [...res.today_tasks, ...res.historical_tasks]
        .find(t => t.id === workflowStore.todayTaskId) ?? res.today_tasks?.[0] ?? null
    }
  }

  initRoomMonitor()
  await onViolationSubmitted((payload: string) => {
    try {
      const data = JSON.parse(payload) as { type?: string; logDetails?: string }
      if (data.type !== 'submitted' || !data.logDetails) return
      if (!isWorking.value) return
      workflowStore.workStatus = 'handling'
      workflowStore.isHandlingViolation = true
      workflowStore.violationCount++
      void addLog('违规处置', data.logDetails)
    } catch { /* ignore */ }
  })
  window.addEventListener('keydown', handleKeyDown)

  // 定时持久化（每5秒）
  setInterval(() => {
    if (!isWorking.value) return
    workflowStore.persist()
    localStorage.setItem('blind_checker_log', JSON.stringify(actionLog.value))
  }, 5000)
})

onUnmounted(async () => {
  stopTimer()
  stopAFKDetection()
  window.removeEventListener('keydown', handleKeyDown)
  // 离开页面时强制同步一次进度到后端，防止数据流失
  if (isWorking.value && todayTask.value) {
    try {
      await rbacApi.updateTaskProgress(todayTask.value.id, {
        reviewed_count: workflowStore.reviewedCount,
        violation_count: workflowStore.violationCount,
        work_duration: workflowStore.totalSeconds,
        is_completed: false,
      })
    } catch { /* 静默 */ }
  }
  // 持久化当前状态到 Store（路由切换后可恢复）
  workflowStore.persist()
  // 离开页面时清理迷你模式状态
  if (isMiniMode.value) {
    await exitMiniMode()
  }
})
</script>

<style scoped>
.realtime-page { padding: 0; }

/* ═══════════════════════════════════════════
   迷你浮窗
   ═══════════════════════════════════════════ */
.mini-active { padding: 0 !important; }

.mini-panel {
  display: flex;
  flex-direction: column;
  gap: 0;
  height: 100vh;
  background: var(--color-bg-1);
  overflow-y: auto;
}

/* 顶栏 */
.mini-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px 10px;
  background: var(--color-bg-2);
  border-bottom: 1px solid var(--color-border-1);
}

.mini-status-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mini-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.dot-offline    { background: #555; }
.dot-patrolling { background: #00b42a; box-shadow: 0 0 6px rgba(0, 180, 42, 0.7); animation: dotPulse 1.8s ease-in-out infinite; }
.dot-handling   { background: #f53f3f; box-shadow: 0 0 6px rgba(245, 63, 63, 0.7); }
.dot-suspended  { background: #ff7d00; }
@keyframes dotPulse {
  0%,100% { opacity: 1; } 50% { opacity: 0.5; }
}

.mini-status-text { font-size: 13px; font-weight: 600; color: var(--color-text-1); }

/* 迷你浮窗 ID 行 */
.mini-ids-row {
  display: flex;
  gap: 6px;
  margin: 0 14px 4px;
}

.mini-room-card {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  padding: 6px 10px;
  border-radius: 6px;
  background: var(--color-fill-2);
  border: 1px solid var(--color-border-2);
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
  user-select: none;
}
.mini-room-card:hover {
  background: var(--color-fill-3);
  border-color: var(--color-border-3);
}
.mini-room-card:active { background: var(--color-fill-4); }

.mini-user-card {
  background: rgba(114, 46, 209, 0.10);
  border-color: rgba(114, 46, 209, 0.20);
}
.mini-user-card:hover {
  background: rgba(114, 46, 209, 0.18);
  border-color: rgba(114, 46, 209, 0.35);
}
.mini-user-card .mini-room-icon { color: #722ed1; }
.mini-user-card .mini-room-id { color: #9254de; }

.mini-room-card:not(.mini-user-card) .mini-room-icon { color: var(--color-text-2); }
.mini-room-label { font-size: 10px; color: var(--color-text-4); }
.mini-room-id {
  font-family: 'SF Mono', 'Cascadia Code', Monaco, monospace;
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text-1);
  letter-spacing: 0.5px;
}

.mini-room-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin: 0 14px 4px;
  padding: 7px 14px;
  font-size: 12px;
  color: var(--color-text-4);
}

.mini-task-chip {
  font-size: 11px;
  padding: 1px 8px;
  border-radius: 10px;
  background: rgba(22, 100, 255, 0.12);
  color: #6ea6ff;
  font-weight: 500;
}

.mini-controls { display: flex; gap: 2px; }

.mini-icon-btn {
  width: 30px; height: 30px;
  border: none; background: transparent;
  border-radius: 7px;
  display: flex; align-items: center; justify-content: center;
  color: var(--color-text-3); font-size: 15px;
  cursor: pointer; transition: background 0.15s, color 0.15s; padding: 0;
}
.mini-icon-btn:hover { background: var(--color-fill-3); color: var(--color-text-1); }
.mini-icon-btn.active-pin { color: #1664ff; background: rgba(22, 100, 255, 0.12); }

/* 计时器区 */
.mini-timer-wrap {
  text-align: center;
  padding: 20px 0 14px;
}

.mini-timer {
  font-family: 'SF Mono', 'Cascadia Code', Monaco, monospace;
  font-size: 46px;
  font-weight: 700;
  color: #1664ff;
  line-height: 1;
  letter-spacing: 3px;
}

.mini-timer-label {
  font-size: 11px;
  color: var(--color-text-4);
  margin-top: 6px;
  letter-spacing: 0.5px;
}

/* 计数行 */
.mini-stats-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  padding: 0 16px 16px;
}

.mini-stat-box { flex: 1; text-align: center; }

.mini-stat-num {
  font-size: 30px;
  font-weight: 700;
  color: var(--color-text-1);
  line-height: 1;
}
.mini-stat-num.danger { color: #f53f3f; }

.mini-stat-label { font-size: 11px; color: var(--color-text-3); margin-top: 4px; }

.mini-stat-sep {
  width: 1px; height: 36px;
  background: var(--color-border-2);
  flex-shrink: 0;
}

/* 操作按钮 */
.mini-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 0 14px;
  flex: 1;
}

.mini-btn {
  height: 42px;
  font-size: 13px;
  font-weight: 500;
  display: flex; align-items: center; justify-content: center; gap: 8px;
}

.mini-shortcut {
  font-size: 10px; font-weight: normal; opacity: 0.55;
  margin-left: auto; padding: 1px 5px;
  background: var(--color-bg-3); border-radius: 3px;
}

.mini-stop-row { margin-top: 4px; padding-bottom: 16px; }

.mini-stop-btn {
  height: 36px;
  font-size: 12px;
  color: var(--color-text-3) !important;
  border: 1px dashed var(--color-border-2) !important;
}
.mini-stop-btn:hover { color: #f53f3f !important; border-color: rgba(245,63,63,0.4) !important; }

/* 正常模式页头置顶按钮 */
.pin-toggle-btn {
  border-color: var(--color-border-1) !important;
  color: var(--color-text-2) !important;
  transition: all 0.15s;
}
.pin-toggle-btn:hover {
  border-color: #1664ff !important;
  color: #1664ff !important;
}
.pin-toggle-active {
  background: rgba(22, 100, 255, 0.10) !important;
  border-color: #1664ff !important;
  color: #1664ff !important;
  font-weight: 600;
}

/* ═══════════════════════════════════════════
   迷你浮窗入口按钮（巡查中时在页头显示）
   ═══════════════════════════════════════════ */
.mini-enter-btn {
  background: linear-gradient(135deg, #1664ff, #0e42d2) !important;
  border-color: transparent !important;
  color: #fff !important;
  font-weight: 600;
  box-shadow: 0 2px 10px rgba(22, 100, 255, 0.40);
  animation: miniPulse 2s ease-in-out infinite;
}
@keyframes miniPulse {
  0%,100% { box-shadow: 0 2px 10px rgba(22,100,255,0.40); }
  50%      { box-shadow: 0 2px 18px rgba(22,100,255,0.70); }
}

/* ═══════════════════════════════════════════
   正常模式 - 页头
   ═══════════════════════════════════════════ */
.page-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 16px;
}
.header-left { display: flex; align-items: center; gap: 12px; }
.page-title { font-size: 20px; font-weight: 600; color: var(--color-text-1); }

/* ═══════════════════════════════════════════
   任务信息条
   ═══════════════════════════════════════════ */
.blind-checker { margin-bottom: 20px; }
.task-banner { margin-bottom: 14px; }

.task-info-bar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 9px 16px; border-radius: 10px;
  background: var(--color-bg-2);
  border: 1px solid var(--color-border-1);
  border-left: 3px solid #1664ff;
  gap: 12px;
}
.task-info-left { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.task-dot { width: 7px; height: 7px; border-radius: 50%; background: #1664ff; box-shadow: 0 0 6px rgba(22,100,255,0.6); flex-shrink: 0; }
.task-biz-icon { color: #1664ff; flex-shrink: 0; }
.task-label { font-size: 12px; font-weight: 600; color: var(--color-text-2); letter-spacing: 0.3px; white-space: nowrap; }
.task-channel-tag { font-weight: 600; }
.task-divider { width: 1px; height: 14px; background: var(--color-border-2); }
.task-meta { display: flex; align-items: center; gap: 4px; font-size: 13px; color: var(--color-text-2); white-space: nowrap; }
.task-info-right { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }
.task-stat { font-size: 13px; color: var(--color-text-2); }
.task-stat strong { font-weight: 700; color: var(--color-text-1); }
.task-stat-sep { color: var(--color-text-4); font-size: 13px; }

/* ═══════════════════════════════════════════
   主卡片
   ═══════════════════════════════════════════ */
.main-card {
  background: var(--color-bg-2);
  border-radius: 12px;
  border: 1px solid var(--color-border-1);
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  overflow: hidden;
}

/* 上半：状态+计时 / 计数 */
.main-top {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 0;
  padding: 24px 28px 20px;
  align-items: center;
}

.top-left { display: flex; flex-direction: column; gap: 10px; }

/* 状态徽标 */
.status-badge {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 4px 12px 4px 8px;
  border-radius: 20px;
  width: fit-content;
  font-size: 13px; font-weight: 600;
}
.status-offline   { background: rgba(100,100,100,0.12); color: #888; }
.status-patrolling { background: rgba(0,180,42,0.12); color: #00b42a; }
.status-handling  { background: rgba(245,63,63,0.12);  color: #f53f3f; }
.status-suspended { background: rgba(255,125,0,0.12);  color: #ff7d00; }

.status-dot-ring {
  width: 8px; height: 8px; border-radius: 50%;
  flex-shrink: 0;
  background: currentColor;
}
.status-patrolling .status-dot-ring { animation: dotPulse 1.8s ease-in-out infinite; }
.status-badge-text { white-space: nowrap; }

/* 状态行 + 房间号 */
.status-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.room-id-display {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 6px;
  background: var(--color-fill-2);
  border: 1px solid var(--color-border-2);
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
  user-select: none;
}
.room-id-display:hover {
  background: var(--color-fill-3);
  border-color: var(--color-border-3);
}

.room-id-display:not(.user-id-display) .room-icon { color: var(--color-text-2); flex-shrink: 0; }

.room-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-3);
  letter-spacing: 0.3px;
}

.user-id-display {
  background: rgba(114, 46, 209, 0.10);
  border-color: rgba(114, 46, 209, 0.20);
}
.user-id-display:hover {
  background: rgba(114, 46, 209, 0.18);
  border-color: rgba(114, 46, 209, 0.35);
}
.user-id-display .room-icon { color: #722ed1; }
.user-id-display .room-number { color: #9254de; }
.user-id-display:hover .room-copy { color: #722ed1; }

.room-id-display:not(.user-id-display) .room-number {
  color: var(--color-text-1);
}
.room-number {
  font-family: 'SF Mono', 'Cascadia Code', Monaco, monospace;
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.room-copy {
  color: var(--color-text-4);
  transition: color 0.15s;
}
.room-id-display:not(.user-id-display):hover .room-copy { color: var(--color-text-2); }

.room-id-empty {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--color-text-4);
  padding: 4px 10px;
  border-radius: 6px;
  background: var(--color-fill-1);
}

.big-timer {
  font-family: 'SF Mono', 'Cascadia Code', Monaco, monospace;
  font-size: 52px;
  font-weight: 700;
  color: #1664ff;
  line-height: 1;
  letter-spacing: 3px;
}

.timer-hint { font-size: 12px; color: var(--color-text-4); }

/* 右侧计数 */
.top-right {
  display: flex;
  align-items: center;
  gap: 0;
  padding: 16px 20px;
  background: var(--color-fill-1);
  border-radius: 10px;
  min-width: 200px;
}

.count-box { flex: 1; text-align: center; }

.count-num {
  font-size: 36px;
  font-weight: 700;
  color: var(--color-text-1);
  line-height: 1;
}
.count-num.danger { color: #f53f3f; }

.count-lbl { font-size: 12px; color: var(--color-text-3); margin-top: 4px; }
.count-hint { font-size: 11px; color: var(--color-text-4); margin-top: 2px; }

.count-sep { width: 1px; height: 48px; background: var(--color-border-2); margin: 0 8px; }

.main-divider { height: 1px; background: var(--color-border-1); margin: 0 28px; }

/* 下半：操作按钮 */
.main-actions {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0;
  padding: 20px 24px;
}

.act-col {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 0 6px;
  border-right: 1px solid var(--color-border-1);
}
.act-col:first-child { padding-left: 0; }
.act-col:last-child  { padding-right: 0; border-right: none; }

.act-btn {
  height: 54px;
  font-size: 15px;
  font-weight: 600;
  display: flex; align-items: center; justify-content: center; gap: 8px;
}

.act-btn-start {
  background: linear-gradient(135deg, #1664ff, #0e42d2) !important;
  border: none !important;
  box-shadow: 0 3px 12px rgba(22,100,255,0.35);
}

.act-btn-switch { letter-spacing: 0.3px; }

.act-shortcut {
  font-size: 11px; font-weight: normal; opacity: 0.6;
  margin-left: auto; padding: 2px 7px;
  background: rgba(0,0,0,0.15); border-radius: 4px;
}

.act-hint {
  font-size: 11px;
  color: var(--color-text-4);
  line-height: 1.4;
  text-align: center;
}

.cooling-tag {
  display: inline-block;
  background: rgba(255,125,0,0.15);
  color: #ff7d00;
  font-size: 10px;
  padding: 0 5px;
  border-radius: 4px;
  margin-left: 4px;
}

/* ═══════════════════════════════════════════
   时间轴日志
   ═══════════════════════════════════════════ */
.timeline-section {
  padding: 0 28px 20px;
  margin-top: 4px;
}

.timeline-header {
  display: flex; align-items: center; gap: 6px;
  font-size: 13px; font-weight: 600; color: var(--color-text-2);
  margin-bottom: 10px; padding-top: 16px;
  border-top: 1px solid var(--color-border-1);
}

.timeline-count {
  font-size: 11px; font-weight: normal;
  color: var(--color-text-4);
  background: var(--color-fill-2);
  padding: 1px 7px; border-radius: 8px;
}

.timeline-list {
  display: flex; flex-direction: column; gap: 0;
  max-height: 180px; overflow-y: auto;
}

.timeline-item {
  display: flex; align-items: center; gap: 10px;
  padding: 5px 0;
  border-bottom: 1px solid var(--color-border-1);
  font-size: 12px;
}
.timeline-item:last-child { border-bottom: none; }

.tl-dot {
  width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0;
}
.tl-dot-green  { background: #00b42a; }
.tl-dot-red    { background: #f53f3f; }
.tl-dot-blue   { background: #1664ff; }
.tl-dot-yellow { background: #ff7d00; }
.tl-dot-gray   { background: #888; }

.tl-time {
  font-family: 'SF Mono', Monaco, monospace;
  font-size: 11px; color: var(--color-text-4);
  flex-shrink: 0; width: 60px;
}

.tl-action { flex-shrink: 0; }

.tl-detail { color: var(--color-text-3); flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* ═══════════════════════════════════════════
   底部：汇总条 + 任务表格
   ═══════════════════════════════════════════ */
.bottom-section { display: flex; flex-direction: column; gap: 14px; margin-top: 20px; }

/* 汇总条 */
.summary-bar {
  display: flex; align-items: center;
  background: var(--color-bg-2);
  border: 1px solid var(--color-border-1);
  border-radius: 10px;
  padding: 12px 20px;
  gap: 0;
}

.summary-item {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 8px;
}

.summary-icon { color: var(--color-text-3); flex-shrink: 0; }
.summary-icon.blue { color: #1664ff; }
.summary-icon.red  { color: #f53f3f; }

.summary-val {
  font-size: 22px; font-weight: 700;
  color: var(--color-text-1); line-height: 1;
}
.summary-val.blue { color: #1664ff; }
.summary-val.red  { color: #f53f3f; }

.summary-lbl { font-size: 12px; color: var(--color-text-3); }

.summary-sep { width: 1px; height: 28px; background: var(--color-border-2); flex-shrink: 0; }

/* 任务表格 */
.table-card { border-radius: 10px; }

.table-title { display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 600; }

.empty-state { padding: 32px 0; display: flex; justify-content: center; }

@media (max-width: 1100px) {
  .main-actions { grid-template-columns: repeat(2, 1fr); }
  .act-col { border-right: none; border-bottom: 1px solid var(--color-border-1); padding: 0 0 12px; }
  .act-col:nth-child(2n) { border-right: none; }
  .act-col:last-child { border-bottom: none; }
}

@media (max-width: 700px) {
  .main-top { grid-template-columns: 1fr; }
  .top-right { justify-content: center; }
  .big-timer { font-size: 40px; }
  .summary-bar { flex-wrap: wrap; gap: 12px; }
}
</style>
