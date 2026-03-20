<template>
  <div class="auditor-view">
    <!-- 今日任务Banner -->
    <div class="task-banner" v-if="todayTask && todayTask.task_channel">
      <a-alert type="info" show-icon class="task-alert">
        <template #icon>
          <icon-notification />
        </template>
        <div class="task-content">
          <div class="task-title">📢 你的当班任务</div>
          <div class="task-details">
            <a-tag color="blue" size="large">
              {{ getTaskChannelLabel(todayTask.task_channel) }}
            </a-tag>
            <span class="task-time" v-if="todayTask.shift_type">
              班次: {{ getShiftTypeLabel(todayTask.shift_type) }}
            </span>
            <span class="task-progress" v-if="todayTask.reviewed_count > 0">
              已审: {{ todayTask.reviewed_count }}场 | 违规: {{ todayTask.violation_count }}次
            </span>
          </div>
        </div>
      </a-alert>
    </div>

    <!-- 极简盲打计件器 -->
    <div class="blind-checker">
      <a-card class="main-card" :bordered="true">
        <div class="card-content">
          <!-- 左侧数据看板 -->
          <div class="data-panel">
            <!-- 当前状态 -->
            <div class="data-item">
              <div class="data-label">当前状态</div>
              <div class="data-value">
                <a-tag :color="statusColor" size="large">
                  {{ statusText }}
                </a-tag>
              </div>
              <div class="data-desc">
                {{ statusDesc }}
              </div>
            </div>

            <!-- 当班时长 -->
            <div class="data-item">
              <div class="data-label">当班时长</div>
              <div class="data-value time-value">
                {{ formatTime(totalSeconds) }}
              </div>
              <div class="data-desc">
                精确到秒，自动计时
              </div>
            </div>

            <!-- 已审场次 -->
            <div class="data-item">
              <div class="data-label">已审场次</div>
              <div class="data-value count-value">
                {{ reviewedCount }}
              </div>
              <div class="data-desc">
                点击"切房审查"自动 +1
              </div>
            </div>

            <!-- 违规拦截 -->
            <div class="data-item">
              <div class="data-label">违规拦截</div>
              <div class="data-value count-value">
                {{ violationCount }}
              </div>
              <div class="data-desc">
                点击"违规标记"自动 +1
              </div>
            </div>
          </div>

          <!-- 右侧操作面板 -->
          <div class="action-panel">
            <!-- 接入/结束工作流 -->
            <div class="action-group">
              <a-button
                v-if="!isWorking"
                type="primary"
                size="large"
                long
                @click="startWorkflow"
                :loading="startingWorkflow"
                class="action-button"
              >
                <icon-play-circle />
                接入工作流
              </a-button>
              <a-button
                v-else
                type="outline"
                status="danger"
                size="large"
                long
                @click="stopWorkflow"
                class="action-button"
              >
                <icon-stop />
                结束工作流
              </a-button>
              <div class="action-desc">
                点击后状态变为"巡查中"，时长开始计时
              </div>
            </div>

            <!-- 切房审查 -->
            <div class="action-group">
              <a-button
                type="primary"
                size="large"
                long
                @click="switchRoom"
                :disabled="!canSwitchRoom || isCoolingDown"
                class="action-button"
              >
                <icon-swap />
                切房审查
                <span class="shortcut">Alt+空格</span>
              </a-button>
              <div class="action-desc">
                触发后，【已审场次】+1
                <span v-if="isCoolingDown" class="cooling-warning">(冷却中)</span>
              </div>
            </div>

            <!-- 违规处置 -->
            <div class="action-group">
              <a-button
                v-if="!isHandlingViolation"
                type="primary"
                status="danger"
                size="large"
                long
                @click="markViolation"
                :disabled="!canMarkViolation"
                class="action-button"
              >
                <icon-flag />
                违规处置
                <span class="shortcut">Alt+1</span>
              </a-button>
              <a-button
                v-else
                type="outline"
                status="success"
                size="large"
                long
                @click="completeViolation"
                class="action-button"
              >
                <icon-check-circle />
                处置完成
                <span class="shortcut">Alt+1</span>
              </a-button>
              <div class="action-desc">
                状态在"处置中"和"巡查中"切换。切为处置时，【违规拦截】+1
              </div>
            </div>

            <!-- 挂起休整 -->
            <div class="action-group">
              <a-button
                v-if="!isSuspended"
                type="outline"
                status="warning"
                size="large"
                long
                @click="suspendWork"
                :disabled="!canSuspend"
                class="action-button"
              >
                <icon-pause-circle />
                挂起休整
                <span class="shortcut">Alt+2</span>
              </a-button>
              <a-button
                v-else
                type="primary"
                status="warning"
                size="large"
                long
                @click="resumeWork"
                class="action-button"
              >
                <icon-play-circle />
                恢复工作
                <span class="shortcut">Alt+2</span>
              </a-button>
              <div class="action-desc">
                触发后，状态变为"挂起"，计时器暂停
              </div>
            </div>
          </div>
        </div>

        <!-- 底部流水日志 -->
        <div class="log-section">
          <a-divider />
          <div class="log-header">
            <icon-file-text />
            <span>操作流水日志</span>
          </div>
          <a-table
            :data="actionLog"
            :pagination="false"
            :bordered="false"
            size="small"
            :scroll="{ y: 200 }"
          >
            <template #columns>
              <a-table-column title="时间" data-index="timestamp" :width="100">
                <template #cell="{ record }">
                  <div class="timestamp">
                    {{ record.timestamp }}
                  </div>
                </template>
              </a-table-column>
              <a-table-column title="动作" data-index="action" :width="120">
                <template #cell="{ record }">
                  <a-tag :color="getActionColor(record.action)" size="small">
                    {{ record.action }}
                  </a-tag>
                </template>
              </a-table-column>
              <a-table-column title="详情" data-index="details">
                <template #cell="{ record }">
                  {{ record.details }}
                </template>
              </a-table-column>
            </template>
          </a-table>
        </div>
      </a-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import { 
  rbacApi, 
  getTaskChannelLabel, 
  getShiftTypeLabel
} from '@/api/rbac'

// 防作弊常量
const MIN_STAY_TIME = 3000 // 3秒冷却时间
const MAX_IDLE_TIME = 5 * 60 * 1000 // 5分钟无操作检测

// 响应式数据
const workStatus = ref<'offline' | 'patrolling' | 'handling' | 'suspended'>('offline')
const totalSeconds = ref(0)
const reviewedCount = ref(0)
const violationCount = ref(0)
const isHandlingViolation = ref(false)
const isSuspended = ref(false)
const startingWorkflow = ref(false)

// 防作弊状态
const lastActionTime = ref<number>(0)
const isCoolingDown = ref(false)
const afkTimer = ref<NodeJS.Timeout | null>(null)

// 今日任务
const todayTask = ref<any>(null)
const taskLoading = ref(false)

// 计时器
let workTimer: NodeJS.Timeout | null = null

// 操作日志
const actionLog = ref<Array<{
  id: number
  timestamp: string
  action: string
  details: string
}>>([])

// 计算属性
const statusText = computed(() => {
  const texts = {
    'offline': '离线',
    'patrolling': '巡查中',
    'handling': '处置中',
    'suspended': '挂起'
  }
  return texts[workStatus.value]
})

const statusColor = computed(() => {
  const colors = {
    'offline': 'gray',
    'patrolling': 'green',
    'handling': 'red',
    'suspended': 'yellow'
  }
  return colors[workStatus.value]
})

const statusDesc = computed(() => {
  const descs = {
    'offline': '未接入工作流',
    'patrolling': '正在巡查直播间',
    'handling': '处理违规内容',
    'suspended': '暂停计时，临时休整'
  }
  return descs[workStatus.value]
})

const isWorking = computed(() => workStatus.value !== 'offline')
const canSwitchRoom = computed(() => workStatus.value === 'patrolling')
const canMarkViolation = computed(() => workStatus.value === 'patrolling')
const canSuspend = computed(() => workStatus.value === 'patrolling')

// 工具函数
const formatTime = (seconds: number) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const getCurrentTime = () => {
  const now = new Date()
  return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
}

const getActionColor = (action: string) => {
  const colors: Record<string, string> = {
    '开始巡查': 'green',
    '结束巡查': 'gray',
    '切房审查': 'blue',
    '违规标记': 'red',
    '处置完成': 'green',
    '挂起休整': 'yellow',
    '恢复工作': 'blue'
  }
  return colors[action] || 'gray'
}

// 防作弊函数
const updateLastActionTime = () => {
  lastActionTime.value = Date.now()
}

const checkCoolingDown = (): boolean => {
  const now = Date.now()
  const timeSinceLastAction = now - lastActionTime.value
  
  if (timeSinceLastAction < MIN_STAY_TIME) {
    isCoolingDown.value = true
    Message.warning(`巡查切换过快，请保证单场审核质量 (冷却中，还需${Math.ceil((MIN_STAY_TIME - timeSinceLastAction) / 1000)}秒)`)
    
    setTimeout(() => {
      isCoolingDown.value = false
    }, MIN_STAY_TIME - timeSinceLastAction)
    
    return true
  }
  
  return false
}

const startAFKDetection = () => {
  if (afkTimer.value) {
    clearInterval(afkTimer.value)
  }
  
  afkTimer.value = setInterval(() => {
    if (workStatus.value === 'patrolling' && !isSuspended.value) {
      const now = Date.now()
      const idleTime = now - lastActionTime.value
      
      if (idleTime > MAX_IDLE_TIME) {
        workStatus.value = 'suspended'
        isSuspended.value = true
        
        Modal.warning({
          title: '防挂机检测',
          content: '检测到长时间未操作，已自动挂起并暂停计时！',
          okText: '知道了',
          hideCancel: true
        })
        
        addLog('自动挂起', '系统检测到长时间未操作，自动暂停计时')
        Message.warning('系统检测到长时间未操作，已自动挂起')
      }
    }
  }, 30000)
}

const stopAFKDetection = () => {
  if (afkTimer.value) {
    clearInterval(afkTimer.value)
    afkTimer.value = null
  }
}

// 日志记录
const addLog = async (action: string, details: string) => {
  const timestamp = getCurrentTime()
  
  actionLog.value.unshift({
    id: Date.now(),
    timestamp,
    action,
    details
  })
  
  // 限制日志数量
  if (actionLog.value.length > 50) {
    actionLog.value = actionLog.value.slice(0, 50)
  }
  
  // 更新最后操作时间
  updateLastActionTime()
  
  // 记录到后端
  await rbacApi.logAction(action, details)
}

// 计时器控制
const startTimer = () => {
  if (workTimer) {
    clearInterval(workTimer)
  }
  
  workTimer = setInterval(() => {
    if (!isSuspended.value) {
      totalSeconds.value++
      
      // 每10秒更新任务进度
      if (totalSeconds.value % 10 === 0 && todayTask.value) {
        updateTaskProgress()
      }
    }
  }, 1000)
}

const stopTimer = () => {
  if (workTimer) {
    clearInterval(workTimer)
    workTimer = null
  }
}

// 任务进度更新
const updateTaskProgress = async () => {
  if (!todayTask.value) return
  
  try {
    await rbacApi.updateTaskProgress(todayTask.value.id, {
      reviewed_count: reviewedCount.value,
      violation_count: violationCount.value,
      work_duration: totalSeconds.value,
      is_completed: workStatus.value === 'offline'
    })
  } catch (error) {
    console.error('更新任务进度失败:', error)
  }
}

// 核心操作函数
const startWorkflow = async () => {
  startingWorkflow.value = true
  
  setTimeout(async () => {
    workStatus.value = 'patrolling'
    isSuspended.value = false
    isHandlingViolation.value = false
    startingWorkflow.value = false
    
    // 初始化最后操作时间
    updateLastActionTime()
    
    startTimer()
    startAFKDetection()
    await addLog('开始巡查', '接入工作流，开始计时')
    
    Message.success('工作流已接入，开始计时')
  }, 300)
}

const stopWorkflow = () => {
  Modal.confirm({
    title: '结束工作流',
    content: '确定要结束当前工作流吗？所有计时将停止。',
    okText: '确认结束',
    cancelText: '取消',
    onOk: async () => {
      workStatus.value = 'offline'
      stopTimer()
      stopAFKDetection()
      await addLog('结束巡查', `本次巡查总时长: ${formatTime(totalSeconds.value)}`)
      
      // 更新最终任务进度
      if (todayTask.value) {
        await rbacApi.updateTaskProgress(todayTask.value.id, {
          reviewed_count: reviewedCount.value,
          violation_count: violationCount.value,
          work_duration: totalSeconds.value,
          is_completed: true
        })
      }
      
      Message.success('工作流已结束')
    }
  })
}

const switchRoom = async () => {
  if (!canSwitchRoom.value) return
  
  // 机制A：切房冷却检查
  if (checkCoolingDown()) {
    return
  }
  
  reviewedCount.value++
  await addLog('切房审查', `已审场次: ${reviewedCount.value}`)
  
  Message.success(`切房完成，已审场次: ${reviewedCount.value}`)
}

const markViolation = async () => {
  if (!canMarkViolation.value) return
  
  workStatus.value = 'handling'
  isHandlingViolation.value = true
  violationCount.value++
  
  await addLog('违规标记', `违规拦截数: ${violationCount.value}`)
  
  Message.warning('已标记违规，请完成处置')
}

const completeViolation = async () => {
  workStatus.value = 'patrolling'
  isHandlingViolation.value = false
  
  await addLog('处置完成', '违规处置完成')
  
  Message.success('违规处置完成，返回巡查状态')
}

const suspendWork = async () => {
  if (!canSuspend.value) return
  
  workStatus.value = 'suspended'
  isSuspended.value = true
  
  await addLog('挂起休整', '暂停计时，临时休整')
  
  Message.info('工作已挂起，计时器暂停')
}

const resumeWork = async () => {
  workStatus.value = 'patrolling'
  isSuspended.value = false
  
  await addLog('恢复工作', '恢复计时，继续巡查')
  
  Message.success('已恢复工作，继续计时')
}

// 键盘事件处理
const handleKeyDown = (event: KeyboardEvent) => {
  // 只在巡查或处置状态下响应快捷键
  if (workStatus.value !== 'patrolling' && workStatus.value !== 'handling') {
    return
  }
  
  // Alt+空格：切房审查
  if (event.altKey && event.code === 'Space') {
    event.preventDefault()
    if (canSwitchRoom.value) {
      switchRoom()
    }
  }
  
  // Alt+1：违规标记/处置完成
  if (event.altKey && event.code === 'Digit1') {
    event.preventDefault()
    if (isHandlingViolation.value) {
      completeViolation()
    } else if (canMarkViolation.value) {
      markViolation()
    }
  }
  
  // Alt+2：挂起休整/恢复工作
  if (event.altKey && event.code === 'Digit2') {
    event.preventDefault()
    if (isSuspended.value) {
      resumeWork()
    } else if (canSuspend.value) {
      suspendWork()
    }
  }
  
  // 更新最后操作时间（任何按键都算操作）
  updateLastActionTime()
}

// 加载今日任务
const loadTodayTask = async () => {
  taskLoading.value = true
  try {
    const response = await rbacApi.getMyTasks()
    
    // 检查是否有今日任务
    if (response?.today_tasks && response.today_tasks.length > 0) {
      const task = response.today_tasks[0]
      todayTask.value = task
      
      // 恢复任务进度（使用可选链和默认值）
      reviewedCount.value = task?.reviewed_count || 0
      violationCount.value = task?.violation_count || 0
      totalSeconds.value = task?.work_duration || 0
      
      // 如果任务未完成，恢复工作状态
      if (task && !task.is_completed && (task.work_duration || 0) > 0) {
        workStatus.value = 'patrolling'
        startTimer()
        startAFKDetection()
        Message.info('检测到未完成任务，已恢复工作状态')
      }
    } else {
      // 没有今日任务（主管或未分配任务的审核员）
      todayTask.value = null
      console.log('今日无任务分配')
    }
  } catch (error) {
    console.error('加载今日任务失败:', error)
    Message.error('加载任务信息失败')
    todayTask.value = null
  } finally {
    taskLoading.value = false
  }
}

// 生命周期
onMounted(() => {
  // 加载今日任务
  loadTodayTask()
  
  // 加载本地状态
  const savedState = localStorage.getItem('blind_checker_state')
  if (savedState) {
    try {
      const state = JSON.parse(savedState)
      totalSeconds.value = state.totalSeconds || 0
      reviewedCount.value = state.reviewedCount || 0
      violationCount.value = state.violationCount || 0
      
      // 恢复工作状态
      if (state.isWorking) {
        workStatus.value = state.workStatus || 'offline'
        isSuspended.value = state.isSuspended || false
        isHandlingViolation.value = state.isHandlingViolation || false
        
        if (workStatus.value === 'patrolling' && !isSuspended.value) {
          startTimer()
          startAFKDetection()
        }
      }
    } catch (error) {
      console.error('加载状态失败:', error)
    }
  }
  
  // 加载操作日志
  const savedLog = localStorage.getItem('blind_checker_log')
  if (savedLog) {
    try {
      actionLog.value = JSON.parse(savedLog)
    } catch (error) {
      console.error('加载日志失败:', error)
    }
  }
  
  // 注册键盘事件
  window.addEventListener('keydown', handleKeyDown)
  
  // 自动保存状态
  setInterval(() => {
    const state = {
      totalSeconds: totalSeconds.value,
      reviewedCount: reviewedCount.value,
      violationCount: violationCount.value,
      workStatus: workStatus.value,
      isWorking: isWorking.value,
      isSuspended: isSuspended.value,
      isHandlingViolation: isHandlingViolation.value,
      timestamp: new Date().toISOString()
    }
    localStorage.setItem('blind_checker_state', JSON.stringify(state))
    
    // 保存日志
    localStorage.setItem('blind_checker_log', JSON.stringify(actionLog.value))
  }, 5000)
})

onUnmounted(() => {
  // 清理计时器
  stopTimer()
  stopAFKDetection()
  
  // 移除键盘事件
  window.removeEventListener('keydown', handleKeyDown)
})
</script>

<style scoped>
.auditor-view {
  padding: 0;
}

.task-banner {
  margin-bottom: 24px;
}

.task-alert {
  background: linear-gradient(135deg, #e6f7ff 0%, #f0f5ff 100%);
  border: 1px solid #91d5ff;
}

.task-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-title {
  font-size: 16px;
  font-weight: 600;
  color: #1890ff;
}

.task-details {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.task-time {
  font-size: 14px;
  color: #666;
}

.task-progress {
  font-size: 14px;
  color: #52c41a;
  font-weight: 500;
}

/* 盲打计件器样式 */
.blind-checker {
  margin-bottom: 24px;
}

.main-card {
  width: 100%;
  max-width: 1200px;
  background: var(--color-bg-2);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin: 0 auto;
}

.card-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
  padding: 24px;
}

/* 左侧数据看板 */
.data-panel {
  display: grid;
  grid-template-columns: 1fr;
  gap: 32px;
}

.data-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.data-label {
  font-size: 14px;
  color: var(--color-text-3);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 500;
}

.data-value {
  font-size: 32px;
  font-weight: 600;
  color: var(--color-text-1);
}

.data-value.time-value {
  font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
  font-size: 48px;
  color: var(--color-primary);
}

.data-value.count-value {
  font-size: 40px;
  color: var(--color-text-1);
}

.data-desc {
  font-size: 12px;
  color: var(--color-text-3);
}

/* 右侧操作面板 */
.action-panel {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

.action-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-button {
  height: 60px;
  font-size: 16px;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.shortcut {
  font-size: 12px;
  font-weight: normal;
  opacity: 0.7;
  margin-left: auto;
  padding: 2px 8px;
  background: var(--color-bg-3);
  border-radius: 4px;
}

.action-desc {
  font-size: 12px;
  color: var(--color-text-3);
  line-height: 1.4;
  padding-left: 8px;
}

.cooling-warning {
  color: var(--color-warning);
  font-weight: 500;
  margin-left: 4px;
}

/* 底部流水日志 */
.log-section {
  margin-top: 24px;
}

.log-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-1);
}

.timestamp {
  font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
  font-size: 12px;
  color: var(--color-text-2);
}

/* 响应式调整 */
@media (max-width: 992px) {
  .card-content {
    grid-template-columns: 1fr;
    gap: 32px;
  }
  
  .data-value.time-value {
    font-size: 40px;
  }
  
  .data-value.count-value {
    font-size: 32px;
  }
}

@media (max-width: 576px) {
  .main-card {
    border-radius: 8px;
  }
  
  .card-content {
    padding: 16px;
  }
  
  .data-value.time-value {
    font-size: 32px;
  }
  
  .data-value.count-value {
    font-size: 28px;
  }
  
  .action-button {
    height: 50px;
    font-size: 14px;
  }
  
  .task-details {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>