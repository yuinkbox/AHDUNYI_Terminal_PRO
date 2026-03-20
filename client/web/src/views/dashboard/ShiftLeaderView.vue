<template>
  <div class="shift-leader-view">
    <!-- 审核员视图部分 -->
    <AuditorView />
    
    <!-- 组长专属：任务派发面板 -->
    <div class="dispatch-panel">
      <a-card title="📋 当班任务派发" class="dispatch-card">
        <template #extra>
          <a-space>
            <a-button type="primary" size="small" @click="loadActiveUsers" :loading="loadingUsers">
              <template #icon>
                <icon-refresh />
              </template>
              刷新人员
            </a-button>
          </a-space>
        </template>
        
        <!-- 出勤人员选择 -->
        <div class="attendance-section">
          <div class="section-header">
            <icon-team />
            <span>当前出勤人员选择</span>
            <a-tag color="blue" size="small">{{ selectedUsers.length }}人已选</a-tag>
          </div>
          
          <a-checkbox-group v-model="selectedUsers" class="user-checkbox-group">
            <a-row :gutter="[16, 16]">
              <a-col :span="8" v-for="user in activeUsers" :key="user.id">
                <a-checkbox :value="user.id">
                  <div class="user-item">
                    <a-avatar :size="32" :style="{ backgroundColor: getUserColor(user.role) }">
                      {{ user.username?.charAt(0)?.toUpperCase() || 'U' }}
                    </a-avatar>
                    <div class="user-info">
                      <div class="user-name">{{ user.username }}</div>
                      <div class="user-role">
                        <a-tag :color="getRoleColor(user.role)" size="small">
                          {{ getRoleLabel(user.role) }}
                        </a-tag>
                      </div>
                    </div>
                  </div>
                </a-checkbox>
              </a-col>
            </a-row>
          </a-checkbox-group>
          
          <div class="attendance-actions">
            <a-button type="outline" size="small" @click="selectAll">
              <template #icon>
                <icon-check />
              </template>
              全选
            </a-button>
            <a-button type="outline" size="small" @click="clearSelection">
              <template #icon>
                <icon-close />
              </template>
              清空
            </a-button>
          </div>
        </div>
        
        <!-- 班次配置 -->
        <div class="shift-config">
          <div class="section-header">
            <icon-schedule />
            <span>班次配置</span>
          </div>
          
          <a-space :size="16">
            <a-date-picker
              v-model="shiftDate"
              placeholder="选择日期"
              style="width: 150px"
              :disabled="dispatching"
            />
            
            <a-select
              v-model="shiftType"
              placeholder="选择班次"
              style="width: 120px"
              :disabled="dispatching"
            >
              <a-option value="morning">早班</a-option>
              <a-option value="afternoon">中班</a-option>
              <a-option value="night">晚班</a-option>
            </a-select>
            
            <a-select
              v-model="selectedChannels"
              placeholder="选择任务通道"
              multiple
              style="width: 200px"
              :disabled="dispatching"
            >
              <a-option value="image">图片审核</a-option>
              <a-option value="chat">单聊审核</a-option>
              <a-option value="video">视频审核</a-option>
              <a-option value="live">直播间巡查</a-option>
            </a-select>
          </a-space>
        </div>
        
        <!-- 智能派发按钮 -->
        <div class="dispatch-actions">
          <a-button
            type="primary"
            size="large"
            long
            @click="dispatchTasks"
            :loading="dispatching"
            :disabled="!canDispatch"
            class="dispatch-button"
          >
            <template #icon>
              <icon-thunderbolt />
            </template>
            智能一键派发
          </a-button>
          <div class="dispatch-hint">
            基于"最少分配优先"原则，确保一周内各通道任务量绝对均衡
          </div>
        </div>
        
        <!-- 派发结果展示 -->
        <div v-if="dispatchResult" class="dispatch-result">
          <div class="section-header">
            <icon-check-circle style="color: #52c41a" />
            <span>派发结果</span>
            <a-tag color="green" size="small">已锁定</a-tag>
          </div>
          
          <a-table
            :data="dispatchResult.assignments"
            :pagination="false"
            :scroll="{ y: 300 }"
            size="small"
          >
            <template #columns>
              <a-table-column title="员工" data-index="username" :width="100">
                <template #cell="{ record }">
                  <div class="user-cell">
                    <a-avatar :size="24" :style="{ backgroundColor: '#1890ff' }">
                      {{ record.username?.charAt(0)?.toUpperCase() || 'U' }}
                    </a-avatar>
                    <span>{{ record.username }}</span>
                  </div>
                </template>
              </a-table-column>
              
              <a-table-column title="姓名" data-index="full_name" :width="80" />
              
              <a-table-column title="分配通道" data-index="task_channel" :width="100">
                <template #cell="{ record }">
                  <a-tag :color="getChannelColor(record.task_channel)" size="small">
                    {{ getChannelLabel(record.task_channel) }}
                  </a-tag>
                </template>
              </a-table-column>
              
              <a-table-column title="本周历史次数" data-index="historical_count" :width="100">
                <template #cell="{ record }">
                  <span :class="{ 'high-count': record.historical_count > 3 }">
                    {{ record.historical_count }}次
                  </span>
                </template>
              </a-table-column>
              
              <a-table-column title="公平性说明" data-index="fairness_note" :width="200">
                <template #cell="{ record }">
                  <div class="fairness-note">
                    <icon-info-circle v-if="record.historical_count === 0" style="color: #1890ff" />
                    <icon-warning v-else-if="record.historical_count > 3" style="color: #ff7d00" />
                    <icon-check-circle v-else style="color: #52c41a" />
                    <span>
                      {{ getFairnessNote(record.historical_count) }}
                    </span>
                  </div>
                </template>
              </a-table-column>
            </template>
          </a-table>
          
          <!-- 统计摘要 -->
          <div class="result-summary">
            <div class="summary-item">
              <icon-file-text />
              <span>总分配数:</span>
              <strong>{{ dispatchResult.summary.total_assignments }}</strong>
            </div>
            <div class="summary-item">
              <icon-pie-chart />
              <span>通道分布:</span>
              <div class="channel-distribution">
                <a-tag
                  v-for="(count, channel) in dispatchResult.summary.channel_distribution"
                  :key="channel"
                  :color="getChannelColor(channel)"
                  size="small"
                >
                  {{ getChannelLabel(channel) }}: {{ count }}
                </a-tag>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 无结果提示 -->
        <div v-else-if="!dispatching && selectedUsers.length > 0" class="no-result">
          <a-empty description="暂未派发任务">
            <template #image>
              <icon-send />
            </template>
            <div class="empty-hint">
              请配置班次信息并点击"智能一键派发"
            </div>
          </a-empty>
        </div>
      </a-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import dayjs from 'dayjs'
import AuditorView from './AuditorView.vue'
import { 
  rbacApi, 
  type ActiveUser, 
  type DispatchResponse,
  UserRole,
  TaskChannel,
  ShiftType,
  getRoleLabel,
  getRoleColor,
  getShiftTypeLabel
} from '@/api/rbac'

// 响应式数据
const activeUsers = ref<ActiveUser[]>([])
const selectedUsers = ref<number[]>([])
const shiftDate = ref<string>(dayjs().format('YYYY-MM-DD'))
const shiftType = ref<ShiftType>(ShiftType.MORNING)
const selectedChannels = ref<TaskChannel[]>([
  TaskChannel.IMAGE,
  TaskChannel.CHAT,
  TaskChannel.VIDEO,
  TaskChannel.LIVE
])

const dispatchResult = ref<DispatchResponse | null>(null)
const loadingUsers = ref(false)
const dispatching = ref(false)

// 计算属性
const canDispatch = computed(() => {
  return (
    selectedUsers.value.length > 0 &&
    shiftDate.value &&
    shiftType.value &&
    selectedChannels.value.length > 0
  )
})

// 工具函数
const getUserColor = (role: UserRole) => {
  const colors: Record<UserRole, string> = {
    [UserRole.SUPERVISOR]: '#f5222d',
    [UserRole.SHIFT_LEADER]: '#fa8c16',
    [UserRole.AUDITOR]: '#52c41a'
  }
  return colors[role] || '#1890ff'
}

const getChannelColor = (channel: TaskChannel | string) => {
  const colors: Record<string, string> = {
    'image': 'blue',
    'chat': 'green',
    'video': 'orange',
    'live': 'purple'
  }
  return colors[channel] || 'gray'
}

const getChannelLabel = (channel: TaskChannel | string) => {
  const labels: Record<string, string> = {
    'image': '图片审核',
    'chat': '单聊审核',
    'video': '视频审核',
    'live': '直播间巡查'
  }
  return labels[channel] || channel
}

const getFairnessNote = (historicalCount: number) => {
  if (historicalCount === 0) {
    return '首次分配此通道，确保机会均等'
  } else if (historicalCount <= 2) {
    return '历史次数较少，优先分配'
  } else if (historicalCount <= 4) {
    return '历史次数适中，均衡分配'
  } else {
    return '历史次数较多，减少分配'
  }
}

// 数据加载
const loadActiveUsers = async () => {
  loadingUsers.value = true
  try {
    const response = await rbacApi.getActiveUsers(UserRole.AUDITOR)
    activeUsers.value = response.users.filter(user => user.is_active)
    Message.success(`已加载 ${activeUsers.value.length} 名审核员`)
  } catch (error) {
    console.error('加载用户列表失败:', error)
    Message.error('加载用户列表失败')
  } finally {
    loadingUsers.value = false
  }
}

// 选择操作
const selectAll = () => {
  selectedUsers.value = activeUsers.value.map(user => user.id)
}

const clearSelection = () => {
  selectedUsers.value = []
}

// 核心派发功能
const dispatchTasks = async () => {
  if (!canDispatch.value) return
  
  dispatching.value = true
  try {
    const result = await rbacApi.dispatchTasks({
      shift_date: shiftDate.value,
      shift_type: shiftType.value,
      user_ids: selectedUsers.value,
      required_channels: selectedChannels.value
    })
    
    dispatchResult.value = result
    Message.success(`任务派发成功！共分配 ${result.assignments.length} 个任务`)
    
    // 记录操作日志
    await rbacApi.logAction(
      '任务派发',
      `组长派发 ${shiftDate.value} ${getShiftTypeLabel(shiftType.value)} 班次任务，共 ${result.assignments.length} 个分配`
    )
    
  } catch (error) {
    console.error('任务派发失败:', error)
    Message.error('任务派发失败，请检查配置')
  } finally {
    dispatching.value = false
  }
}

// 生命周期
onMounted(() => {
  // 默认加载审核员列表
  loadActiveUsers()
})
</script>

<style scoped>
.shift-leader-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.dispatch-panel {
  margin-top: 24px;
}

.dispatch-card {
  background: var(--color-bg-2);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 500;
  color: var(--color-text-1);
}

/* 出勤人员选择 */
.attendance-section {
  margin-bottom: 24px;
  padding: 16px;
  background: var(--color-bg-3);
  border-radius: 8px;
}

.user-checkbox-group {
  width: 100%;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.user-item:hover {
  background: var(--color-bg-4);
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.user-name {
  font-weight: 500;
  color: var(--color-text-1);
}

.user-role {
  font-size: 12px;
}

.attendance-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

/* 班次配置 */
.shift-config {
  margin-bottom: 24px;
  padding: 16px;
  background: var(--color-bg-3);
  border-radius: 8px;
}

/* 派发按钮 */
.dispatch-actions {
  margin-bottom: 24px;
}

.dispatch-button {
  height: 48px;
  font-size: 16px;
  font-weight: 500;
}

.dispatch-hint {
  margin-top: 8px;
  font-size: 12px;
  color: var(--color-text-3);
  text-align: center;
}

/* 派发结果 */
.dispatch-result {
  margin-top: 24px;
  padding: 16px;
  background: linear-gradient(135deg, #f6ffed 0%, #e6fffb 100%);
  border-radius: 8px;
  border: 1px solid var(--color-success-light);
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.high-count {
  color: var(--color-warning);
  font-weight: 600;
}

.fairness-note {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--color-text-2);
}

.result-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--color-border-2);
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--color-text-2);
}

.summary-item strong {
  color: var(--color-text-1);
  font-weight: 600;
}

.channel-distribution {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

/* 无结果提示 */
.no-result {
  margin-top: 24px;
  padding: 32px;
  text-align: center;
}

.empty-hint {
  margin-top: 8px;
  font-size: 14px;
  color: var(--color-text-3);
}

/* 响应式调整 */
@media (max-width: 992px) {
  .user-checkbox-group .arco-col {
    width: 50%;
  }
  
  .shift-config .arco-space {
    flex-direction: column;
    align-items: stretch;
  }
  
  .shift-config .arco-date-picker,
  .shift-config .arco-select {
    width: 100% !important;
  }
}

@media (max-width: 576px) {
  .user-checkbox-group .arco-col {
    width: 100%;
  }
  
  .result-summary {
    flex-direction: column;
    gap: 12px;
  }
}
</style>