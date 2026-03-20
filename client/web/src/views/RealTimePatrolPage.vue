<template>
  <div class="realtime-page">
    <!-- 页头 -->
    <div class="page-header">
      <div class="header-left">
        <icon-eye :size="24" />
        <span class="page-title">实时监控</span>
        <a-badge
          :status="monitorStatus === 'running' ? 'processing' : 'default'"
          :text="monitorStatus === 'running' ? '运行中' : '已暂停'"
        />
      </div>
      <a-space>
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

    <!-- 统计卡片 -->
    <a-row :gutter="16" class="stat-row">
      <a-col :span="6">
        <a-card class="stat-card">
          <a-statistic title="今日任务" :value="stats.totalTasks" >
            <template #prefix><icon-file-list /></template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="stat-card">
          <a-statistic title="已审核" :value="stats.totalReviewed" 
            :value-style="{ color: '#00b42a' }">
            <template #prefix><icon-check-circle /></template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="stat-card">
          <a-statistic title="违规数" :value="stats.totalViolations"
            :value-style="{ color: '#f53f3f' }">
            <template #prefix><icon-exclamation-circle /></template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="stat-card">
          <a-statistic title="在岗时长(分钟)" :value="Math.round(stats.totalDuration / 60)"
            :value-style="{ color: '#165dff' }">
            <template #prefix><icon-clock-circle /></template>
          </a-statistic>
        </a-card>
      </a-col>
    </a-row>

    <!-- 今日任务表格 -->
    <a-card title="今日任务列表" class="table-card">
      <a-table
        :data="todayTasks"
        :loading="loading"
        :pagination="false"
        row-key="id"
        stripe
      >
        <a-table-column title="通道" data-index="task_channel">
          <template #cell="{ record }">
            <a-tag :color="channelColor(record.task_channel)">
              {{ channelLabel(record.task_channel) }}
            </a-tag>
          </template>
        </a-table-column>
        <a-table-column title="班次" data-index="shift_type">
          <template #cell="{ record }">{{ shiftLabel(record.shift_type) }}</template>
        </a-table-column>
        <a-table-column title="已审核" data-index="reviewed_count" />
        <a-table-column title="违规" data-index="violation_count" />
        <a-table-column title="状态">
          <template #cell="{ record }">
            <a-badge
              :status="record.is_completed ? 'success' : 'processing'"
              :text="record.is_completed ? '已完成' : '进行中'"
            />
          </template>
        </a-table-column>
        <a-table-column title="操作" :width="120">
          <template #cell="{ record }">
            <a-button
              v-if="!record.is_completed"
              type="text"
              size="small"
              @click="completeTask(record.id)"
            >完成</a-button>
            <a-tag v-else color="green" size="small">已完成</a-tag>
          </template>
        </a-table-column>
      </a-table>

      <div v-if="!loading && todayTasks.length === 0" class="empty-state">
        <a-empty description="今日暂无分配任务">
          <template #image><icon-inbox :size="48" /></template>
        </a-empty>
      </div>
    </a-card>

    <!-- 派发任务弹窗 -->
    <a-modal
      v-model:visible="dispatchModal.visible"
      title="智能任务派发"
      :width="520"
      @ok="submitDispatch"
      :ok-loading="dispatchModal.loading"
      ok-text="开始派发"
    >
      <a-form :model="dispatchForm" layout="vertical">
        <a-form-item label="派发日期" required>
          <a-input v-model="dispatchForm.shift_date" placeholder="YYYY-MM-DD" />
        </a-form-item>
        <a-form-item label="班次" required>
          <a-radio-group v-model="dispatchForm.shift_type" type="button">
            <a-radio value="morning">早班</a-radio>
            <a-radio value="afternoon">中班</a-radio>
            <a-radio value="night">晚班</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-form-item label="审核通道" required>
          <a-checkbox-group v-model="dispatchForm.required_channels">
            <a-checkbox value="image">图片审核</a-checkbox>
            <a-checkbox value="chat">单聊审核</a-checkbox>
            <a-checkbox value="video">视频审核</a-checkbox>
            <a-checkbox value="live">直播巡查</a-checkbox>
          </a-checkbox-group>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import { rbacApi, type TaskItem, getTaskChannelLabel, getShiftTypeLabel } from '@/api/rbac'
import { usePermissionStore } from '@/stores/permission'

const permissionStore = usePermissionStore()

// ---- state ---------------------------------------------------------------
const loading       = ref(false)
const todayTasks    = ref<TaskItem[]>([])
const monitorStatus = ref<'running' | 'paused'>('running')

const dispatchModal = ref({ visible: false, loading: false })
const dispatchForm  = ref({
  shift_date: new Date().toISOString().slice(0, 10),
  shift_type: 'morning',
  required_channels: [] as string[],
})

// ---- computed ------------------------------------------------------------
const stats = computed(() => ({
  totalTasks:      todayTasks.value.length,
  totalReviewed:   todayTasks.value.reduce((s, t) => s + t.reviewed_count, 0),
  totalViolations: todayTasks.value.reduce((s, t) => s + t.violation_count, 0),
  totalDuration:   todayTasks.value.reduce((s, t) => s + t.work_duration, 0),
}))

// ---- helpers -------------------------------------------------------------
const channelLabel = (ch: string) => getTaskChannelLabel(ch)
const shiftLabel   = (st: string) => getShiftTypeLabel(st)
const channelColor = (ch: string): string =>
  ({ image: 'blue', chat: 'cyan', video: 'purple', live: 'orange' })[ch] ?? 'gray'

// ---- data ----------------------------------------------------------------
async function loadTasks() {
  loading.value = true
  try {
    const res = await rbacApi.getMyTasks()
    todayTasks.value = res.today_tasks
  } catch {
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

function showDispatchModal() {
  dispatchModal.value.visible = true
}

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
      user_ids: [],          // backend will use all active users when empty
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

onMounted(loadTasks)
</script>

<style scoped>
.realtime-page { padding: 0; }

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.header-left { display: flex; align-items: center; gap: 12px; }
.page-title { font-size: 20px; font-weight: 600; color: var(--color-text-1); }

.stat-row { margin-bottom: 20px; }
.stat-card { border-radius: 8px; }

.table-card { border-radius: 8px; }

.empty-state {
  padding: 48px 0;
  display: flex;
  justify-content: center;
}
</style>
