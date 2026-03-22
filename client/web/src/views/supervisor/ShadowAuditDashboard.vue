<template>
  <div class="shadow-audit-page">
    <!-- 页头 -->
    <div class="page-header">
      <div class="header-left">
        <icon-eye :size="24" />
        <span class="page-title">统帅大屏 — 影子审计</span>
        <a-badge status="processing" text="实时监控中" />
      </div>
      <a-space>
        <a-select v-model="filterUserId" style="width:160px" allow-clear placeholder="筛选审核员"
          @change="loadLogs">
          <a-option :value="0">全部人员</a-option>
          <a-option v-for="u in activeUsers" :key="u.id" :value="u.id">
            {{ u.full_name }}
          </a-option>
        </a-select>
        <a-input
          v-model="filterAction"
          placeholder="操作关键词"
          style="width:140px"
          allow-clear
          @press-enter="loadLogs"
        />
        <a-button type="primary" @click="loadLogs" :loading="loading">
          <template #icon><icon-search /></template>查询
        </a-button>
        <a-button @click="toggleAutoRefresh">
          <template #icon>
            <icon-pause v-if="autoRefresh" />
            <icon-play-arrow v-else />
          </template>
          {{ autoRefresh ? '暂停刷新' : '恢复刷新' }}
        </a-button>
      </a-space>
    </div>

    <!-- 统计卡片 -->
    <a-row :gutter="16" class="stat-row">
      <a-col :span="6">
        <a-card class="stat-card">
          <a-statistic title="总操作数" :value="total">
            <template #prefix><icon-list /></template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="stat-card">
          <a-statistic title="活跃用户" :value="uniqueUsers"
            :value-style="{ color: '#165dff' }">
            <template #prefix><icon-user-group /></template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="stat-card">
          <a-statistic title="平均操作时长(ms)" :value="avgDuration" :precision="0"
            :value-style="{ color: '#ff7d00' }">
            <template #prefix><icon-clock-circle /></template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="stat-card">
          <a-statistic title="总页数" :value="totalPages">
            <template #prefix><icon-file /></template>
          </a-statistic>
        </a-card>
      </a-col>
    </a-row>

    <!-- 日志表格 -->
    <a-card class="table-card">
      <a-table
        :data="logs"
        :loading="loading"
        :pagination="{
          current: page,
          pageSize: pageSize,
          total: total,
          showTotal: true,
          onChange: onPageChange,
        }"
        row-key="id"
        stripe
        size="small"
      >
        <template #columns>
          <a-table-column title="时间" :width="160">
            <template #cell="{ record }">
              <span class="ts-cell">{{ formatTs(record.timestamp) }}</span>
            </template>
          </a-table-column>
          <a-table-column title="用户" :width="120">
            <template #cell="{ record }">
              <a-tag color="blue" size="small">{{ record.username }}</a-tag>
            </template>
          </a-table-column>
          <a-table-column title="操作" data-index="action" :width="140" />
          <a-table-column title="详情" data-index="details" />
          <a-table-column title="时长(ms)" data-index="duration" :width="100">
            <template #cell="{ record }">
              <span :style="{ color: record.duration > 5000 ? '#f53f3f' : 'inherit' }">
                {{ record.duration ?? '-' }}
              </span>
            </template>
          </a-table-column>
          <a-table-column title="任务ID" data-index="task_id" :width="90">
            <template #cell="{ record }">{{ record.task_id ?? '-' }}</template>
          </a-table-column>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import { rbacApi, type ActionLogItem, type ActiveUser } from '@/api/rbac'

// ---- state ---------------------------------------------------------------
const logs         = ref<ActionLogItem[]>([])
const activeUsers  = ref<ActiveUser[]>([])
const loading      = ref(false)
const total        = ref(0)
const page         = ref(1)
const pageSize     = ref(50)
const filterUserId = ref<number | null>(null)
const filterAction = ref('')
const autoRefresh  = ref(true)
let refreshTimer: ReturnType<typeof setInterval> | null = null

// ---- computed ------------------------------------------------------------
const totalPages  = computed(() => Math.ceil(total.value / pageSize.value))
const uniqueUsers = computed(() => new Set(logs.value.map(l => l.user_id)).size)
const avgDuration = computed(() => {
  const withDur = logs.value.filter(l => l.duration != null)
  if (!withDur.length) return 0
  return Math.round(withDur.reduce((s, l) => s + (l.duration ?? 0), 0) / withDur.length)
})

// ---- helpers -------------------------------------------------------------
function formatTs(iso: string): string {
  return new Date(iso).toLocaleString('zh-CN', { hour12: false })
}

// ---- data ----------------------------------------------------------------
async function loadLogs() {
  loading.value = true
  try {
    const params: Parameters<typeof rbacApi.getActionLogs>[0] = {
      page:      page.value,
      page_size: pageSize.value,
    }
    if (filterUserId.value !== null) params.user_id = filterUserId.value
    if (filterAction.value)          params.action  = filterAction.value
    const res = await rbacApi.getActionLogs(params)
    logs.value  = res.items
    total.value = res.total
  } catch {
    Message.error('加载日志失败')
  } finally {
    loading.value = false
  }
}

async function loadActiveUsers() {
  try {
    const res = await rbacApi.getActiveUsers()
    activeUsers.value = res.users
  } catch {
    // non-critical
  }
}

function onPageChange(p: number) {
  page.value = p
  loadLogs()
}

function toggleAutoRefresh() {
  autoRefresh.value = !autoRefresh.value
  if (autoRefresh.value) startAutoRefresh()
  else if (refreshTimer) clearInterval(refreshTimer)
}

function startAutoRefresh() {
  if (refreshTimer) clearInterval(refreshTimer)
  refreshTimer = setInterval(() => {
    if (page.value === 1) loadLogs()
  }, 15_000)
}

// ---- lifecycle -----------------------------------------------------------
onMounted(async () => {
  await Promise.all([loadLogs(), loadActiveUsers()])
  startAutoRefresh()
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
})
</script>

<style scoped>
.shadow-audit-page { padding: 0; }

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

.ts-cell {
  font-family: 'SF Mono', 'Cascadia Code', monospace;
  font-size: 12px;
  color: var(--color-text-2);
}
</style>
