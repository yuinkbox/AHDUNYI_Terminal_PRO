<template>
  <div class="violation-page">
    <!-- 页头 -->
    <div class="page-header">
      <div class="header-left">
        <icon-shield :size="24" />
        <span class="page-title">违规复核</span>
      </div>
      <a-space>
        <a-range-picker v-model="dateRange" style="width:280px" @change="loadTasks" />
        <a-button @click="loadTasks" :loading="loading">
          <template #icon><icon-refresh /></template>刷新
        </a-button>
      </a-space>
    </div>

    <!-- 统计行 -->
    <a-row :gutter="16" class="stat-row">
      <a-col :span="6">
        <a-card class="stat-card">
          <a-statistic title="总违规数" :value="stats.totalViolations"
            :value-style="{ color: '#f53f3f' }">
            <template #prefix><icon-bug /></template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="stat-card">
          <a-statistic title="总审核量" :value="stats.totalReviewed"
            :value-style="{ color: '#165dff' }">
            <template #prefix><icon-eye /></template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="stat-card">
          <a-statistic title="违规率" :value="stats.violationRate"
            :precision="2" suffix="%"
            :value-style="{ color: stats.violationRate > 5 ? '#f53f3f' : '#00b42a' }">
            <template #prefix><icon-percentage /></template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="stat-card">
          <a-statistic title="已完成任务" :value="stats.completedTasks"
            :value-style="{ color: '#00b42a' }">
            <template #prefix><icon-check-circle /></template>
          </a-statistic>
        </a-card>
      </a-col>
    </a-row>

    <!-- 任务列表 -->
    <a-card title="任务明细" class="table-card">
      <template #extra>
        <a-select v-model="channelFilter" style="width:140px" allow-clear placeholder="通道筛选"
          @change="() => {}">
          <a-option value="">全部</a-option>
          <a-option value="image">图片</a-option>
          <a-option value="chat">单聊</a-option>
          <a-option value="video">视频</a-option>
          <a-option value="live">直播</a-option>
        </a-select>
      </template>

      <a-table
        :data="filteredTasks"
        :loading="loading"
        :pagination="{ pageSize: 15, showTotal: true }"
        row-key="id"
        stripe
      >
        <template #columns>
          <a-table-column title="日期" data-index="shift_date" :width="110" />
          <a-table-column title="班次">
            <template #cell="{ record }">{{ shiftLabel(record.shift_type) }}</template>
          </a-table-column>
          <a-table-column title="通道">
            <template #cell="{ record }">
              <a-tag :color="channelColor(record.task_channel)">
                {{ channelLabel(record.task_channel) }}
              </a-tag>
            </template>
          </a-table-column>
          <a-table-column title="审核量" data-index="reviewed_count" :sortable="{ sortDirections: ['ascend','descend'] }" />
          <a-table-column title="违规数" data-index="violation_count" :sortable="{ sortDirections: ['ascend','descend'] }">
            <template #cell="{ record }">
              <span :style="{ color: record.violation_count > 0 ? '#f53f3f' : 'inherit' }">
                {{ record.violation_count }}
              </span>
            </template>
          </a-table-column>
          <a-table-column title="违规率">
            <template #cell="{ record }">
              <a-progress
                :percent="record.reviewed_count
                  ? Math.round((record.violation_count / record.reviewed_count) * 100)
                  : 0"
                size="small"
                :status="(record.violation_count / (record.reviewed_count || 1)) > 0.05
                  ? 'danger' : 'normal'"
              />
            </template>
          </a-table-column>
          <a-table-column title="状态">
            <template #cell="{ record }">
              <a-badge
                :status="record.is_completed ? 'success' : 'processing'"
                :text="record.is_completed ? '已完成' : '进行中'"
              />
            </template>
          </a-table-column>
          <a-table-column title="操作" :width="100">
            <template #cell="{ record }">
              <a-button type="text" size="small" @click="viewDetail(record)">
                <template #icon><icon-eye /></template>详情
              </a-button>
            </template>
          </a-table-column>
        </template>
      </a-table>
    </a-card>

    <!-- 任务详情弹窗 -->
    <a-modal
      v-model:visible="detailModal.visible"
      title="任务详情"
      :footer="false"
      :width="480"
    >
      <a-descriptions :data="detailFields" bordered :column="1" />
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import { rbacApi, type TaskItem, getTaskChannelLabel, getShiftTypeLabel } from '@/api/rbac'

// ---- state ---------------------------------------------------------------
const loading       = ref(false)
const allTasks      = ref<TaskItem[]>([])
const channelFilter = ref('')
const dateRange     = ref<string[]>([])

const detailModal = ref<{ visible: boolean; task: TaskItem | null }>({
  visible: false,
  task: null,
})

// ---- computed ------------------------------------------------------------
const filteredTasks = computed(() =>
  channelFilter.value
    ? allTasks.value.filter(t => t.task_channel === channelFilter.value)
    : allTasks.value,
)

const stats = computed(() => {
  const tasks = filteredTasks.value
  const totalReviewed   = tasks.reduce((s, t) => s + t.reviewed_count, 0)
  const totalViolations = tasks.reduce((s, t) => s + t.violation_count, 0)
  return {
    totalViolations,
    totalReviewed,
    violationRate: totalReviewed ? (totalViolations / totalReviewed) * 100 : 0,
    completedTasks: tasks.filter(t => t.is_completed).length,
  }
})

const detailFields = computed(() => {
  const t = detailModal.value.task
  if (!t) return []
  return [
    { label: '日期',   value: t.shift_date },
    { label: '班次',   value: getShiftTypeLabel(t.shift_type) },
    { label: '通道',   value: getTaskChannelLabel(t.task_channel) },
    { label: '审核量', value: t.reviewed_count },
    { label: '违规数', value: t.violation_count },
    { label: '在岗时长', value: `${Math.round(t.work_duration / 60)} 分钟` },
    { label: '状态',   value: t.is_completed ? '已完成' : '进行中' },
  ]
})

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
    // combine today + historical for violation review
    allTasks.value = [...res.today_tasks, ...res.historical_tasks]
  } catch {
    Message.error('加载任务失败')
  } finally {
    loading.value = false
  }
}

function viewDetail(task: TaskItem) {
  detailModal.value = { visible: true, task }
}

onMounted(loadTasks)
</script>

<style scoped>
.violation-page { padding: 0; }
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
</style>
