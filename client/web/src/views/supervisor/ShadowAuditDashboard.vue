<template>
  <div class="shadow-audit-dashboard">
    <a-card class="status-card" :bordered="false">
      <div class="status-header">
        <div class="status-left">
          <a-space size="large">
            <div class="status-item">
              <div class="status-label">系统状态</div>
              <div class="status-value" :class="{ 'status-error': lastError }">
                {{ lastError || '卫星链路已连接' }}
              </div>
            </div>
            <div class="status-item">
              <div class="status-label">当前活跃用户</div>
              <div class="status-value">{{ systemStats.total_active_users || 0 }}</div>
            </div>
            <div class="status-item">
              <div class="status-label">最后侦测时间</div>
              <div class="status-value">{{ lastUpdateTime }}</div>
            </div>
            <div class="status-item">
              <div class="status-label">影子引擎</div>
              <div class="status-value" :class="systemStats.audit_engine_available ? 'status-success' : 'status-error'">
                {{ systemStats.audit_engine_available ? '满负荷运转' : '引擎离线' }}
              </div>
            </div>
          </a-space>
        </div>
        
        <div class="status-right">
          <a-space>
            <a-button type="primary" :loading="loading" @click="refreshData">
              <template #icon><icon-refresh /></template>
              强制侦测
            </a-button>
            <a-button 
              type="outline" 
              @click="toggleAutoRefresh"
              :status="autoRefreshEnabled ? 'success' : 'normal'"
            >
              <template #icon><icon-sync :spin="autoRefreshEnabled" /></template>
              {{ autoRefreshEnabled ? '自动巡航中' : '手动监控' }}
            </a-button>
            <a-tag color="arcoblue" bordered>5s 刷新间隔</a-tag>
          </a-space>
        </div>
      </div>
    </a-card>

    <a-card class="radar-card" :bordered="false">
      <template #title>
        <div class="radar-title">
          <icon-apps size="20" style="color: #165dff" />
          <span>全员实时统帅监控</span>
          <a-badge v-if="suspiciousCount > 0" :count="suspiciousCount" color="red" class="suspicious-badge" />
            color="red" 
            class="suspicious-badge"
          />
>>>>>>> ccbe7b8 (style: 重写全站UI文案，采用字节跳动内部中台风格，更新为业务导向词汇)
        </div>
      </template>
      
      <a-table
        :data="activeUsers"
        :columns="columns"
        :pagination="false"
        :loading="loading"
        :row-class-name="getRowClassName"
        class="radar-table"
        row-key="user_id"
      >
        <template #username="{ record }">
          <div class="user-cell">
            <a-avatar :size="32" :style="{ backgroundColor: getUserColor(record.user_id) }">
              {{ record.full_name ? record.full_name.charAt(0) : '?' }}
            </a-avatar>
            <div class="user-info">
              <div class="user-name">{{ record.full_name }}</div>
              <div class="user-id">ID: {{ record.id }}</div>
            </div>
          </div>
        </template>

        <template #status="{ record }">
          <a-tag :color="getStatusColor(record.status)" :bordered="false">
            {{ getStatusText(record.status) }}
          </a-tag>
        </template>

        <template #stay_duration="{ record }">
          <a-space size="mini">
            <icon-clock-circle />
            <span>{{ formatDuration(record.stay_duration || 0) }}</span>
          </a-space>
        </template>

        <template #judgment="{ record }">
          <div class="judgment-cell" :style="{ color: getStatusColor(record.status) }">
            <component :is="getStatusIcon(record.status)" style="margin-right: 4px" />
            <span style="font-weight: 600">{{ getJudgmentText(record.status) }}</span>
          </div>
        </template>

        <template #operations="{ record }">
          <a-button type="text" size="small" @click="showUserDetail(record)">
            <template #icon><icon-eye /></template>
            追踪
          </a-button>
        </template>
      </a-table>

      <div class="table-footer">
        <a-space size="large">
          <span class="footer-stat-item">监控总数: <b>{{ activeUsers.length }}</b></span>
          <span class="footer-stat-item color-red">高危预警: <b>{{ suspiciousCount }}</b></span>
          <span class="footer-stat-item color-green">风险追踪: <b>{{ riskTrackingCount }}</b></span>
        </a-space>
        <a-button type="text" size="small" @click="exportData">
          <template #icon><icon-download /></template>
          导出战报
        </a-button>
      </div>
    </a-card>

    <a-row :gutter="16">
      <a-col :span="8">
        <a-card title="影子引擎侦测统计" size="small" :bordered="false">
          <div class="engine-stats">
            <div class="stat-row"><span>总检查频次</span><b>{{ auditStats.total_checks }}</b></div>
            <div class="stat-row"><span>平均响应耗时</span><b>{{ auditStats.avg_response_time }}ms</b></div>
            <div class="stat-row"><span>跳房检测拦截</span><b style="color: #f53f3f">{{ auditStats.hopping_detected }}</b></div>
          </div>
        </a-card>
      </a-col>
      <a-col :span="16">
        <a-card title="RoomMonitor 终端状态" size="small" :bordered="false">
          <div class="monitor-info-grid">
            <a-tag :color="roomMonitor.running ? 'green' : 'red'">
              探针状态: {{ roomMonitor.running ? '在线' : '离线' }}
            </a-tag>
            <span v-if="roomMonitor.running">当前锁定房间: <b>{{ roomMonitor.current_room_id || '未进房' }}</b></span>
            <span v-if="roomMonitor.running">底层扫描次数: {{ roomMonitor.stats?.total_scans }}</span>
          </div>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import { 
  IconRefresh, IconSync, IconApps, IconClockCircle,
  IconEye, IconCheckCircle, IconDownload, IconExclamationCircle,
  IconNotification
} from '@arco-design/web-vue/es/icon'
import { supervisorApi } from '@/api/supervisor'

// --- 1. 响应式状态 ---
const loading = ref(false)
const lastError = ref('')
const lastUpdateTime = ref('--:--:--')
const autoRefreshEnabled = ref(true)
const refreshTimer = ref<any>(null)

const activeUsers = ref<any[]>([])
const systemStats = ref({
  total_active_users: 0,
  audit_engine_available: false,
  timestamp: ''
})
const auditStats = ref({
  total_checks: 0,
  avg_response_time: 0,
  hopping_detected: 0
})
const roomMonitor = ref({
  running: false,
  current_room_id: null as string | null,
  stats: { total_scans: 0 }
})

// --- 2. 计算属性 ---
const suspiciousCount = computed(() => activeUsers.value.filter(u => u.status === 'SUSPICIOUS').length)
const riskTrackingCount = computed(() => activeUsers.value.filter(u => u.status === 'RISK_TRACKING').length)

// --- 3. 表格配置 ---
const columns = [
  { title: '员工/终端', slotName: 'username', width: 200 },
  { title: '申报状态', slotName: 'status', width: 120 },
  { title: '直播软件位置', dataIndex: 'room_id', width: 150 },
  { title: '停留', slotName: 'stay_duration', width: 120 },
  { title: '上帝判定', slotName: 'judgment', width: 150 },
  { title: '异常/判定依据', dataIndex: 'context_reason' },
  { title: '操作', slotName: 'operations', width: 100 }
]

// --- 4. 核心逻辑 ---
const refreshData = async () => {
  loading.value = true;
  try {
    // 使用统一的API客户端
    const response = await supervisorApi.getRealtimeStatus();
    
    if (response.success) {
      activeUsers.value = (response.active_users || []).sort((a: any, b: any) => {
        if (a.status === 'SUSPICIOUS' && b.status !== 'SUSPICIOUS') return -1;
        return a.status !== 'SUSPICIOUS' && b.status === 'SUSPICIOUS' ? 1 : 0;
      });
      systemStats.value = response.system || systemStats.value;
      auditStats.value = response.audit_stats || auditStats.value;
      roomMonitor.value = response.room_monitor || roomMonitor.value;
      lastUpdateTime.value = new Date().toLocaleTimeString('zh-CN', {
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
      lastError.value = '';
    }
  } catch (err: any) {
    console.error('刷新数据失败:', err);
    lastError.value = err.message || '网络请求失败';
  } finally {
    loading.value = false;
  }
};

const toggleAutoRefresh = () => {
  autoRefreshEnabled.value = !autoRefreshEnabled.value
  autoRefreshEnabled.value ? startAutoRefresh() : stopAutoRefresh()
}

const startAutoRefresh = () => {
  stopAutoRefresh()
  refreshTimer.value = setInterval(refreshData, 5000)
}

const stopAutoRefresh = () => {
  if (refreshTimer.value) clearInterval(refreshTimer.value)
}

// --- 5. 样式辅助函数 ---
const getStatusColor = (s: string) => {
  const map: any = { 'NORMAL': 'blue', 'SUSPICIOUS': 'red', 'RISK_TRACKING': 'green', 'EXEMPTED': 'purple' }
  return map[s] || 'gray'
}

const getStatusText = (s: string) => {
  const map: any = { 'NORMAL': '正常', 'SUSPICIOUS': '异常', 'RISK_TRACKING': '风险追踪', 'EXEMPTED': '业务豁免' }
  return map[s] || s
}

const getStatusIcon = (s: string) => {
  if (s === 'SUSPICIOUS') return IconExclamationCircle
  if (s === 'RISK_TRACKING') return IconNotification
  return IconCheckCircle
}

const getJudgmentText = (s: string) => {
  if (s === 'SUSPICIOUS') return '疑似挂机/跳房'
  if (s === 'NORMAL') return '审核作业中'
  return '系统豁免'
}

const getRowClassName = (record: any) => {
  if (record.status === 'SUSPICIOUS') return 'row-suspicious'
  if (record.status === 'RISK_TRACKING') return 'row-risk'
  return ''
}

const getUserColor = (id: number) => ['#165dff', '#00b42a', '#ff7d00', '#f53f3f'][id % 4]

const formatDuration = (s: number) => s < 60 ? `${s}秒` : `${Math.floor(s/60)}分${s%60}秒`

const showUserDetail = (r: any) => Message.info(`正在深度追踪: ${r.full_name}`)

const exportData = () => Message.success('实时战报导出成功')

// --- 6. 生命周期 ---
onMounted(() => {
  refreshData()
  startAutoRefresh()
})

onUnmounted(() => stopAutoRefresh())
</script>

<style scoped lang="less">
.shadow-audit-dashboard {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background-color: var(--color-fill-2);
  min-height: 100vh;

  .status-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    .status-item {
      display: flex;
      flex-direction: column;
      .status-label { font-size: 12px; color: var(--color-text-3); }
      .status-value { 
        font-size: 14px; font-weight: bold; 
        &.status-success { color: #00b42a; }
        &.status-error { color: #f53f3f; }
      }
    }
  }

  .radar-card {
    border-radius: 8px;
    :deep(.arco-card-header) { border-bottom: none; }
    .radar-title { display: flex; align-items: center; gap: 8px; font-weight: bold; }
  }

  .table-footer {
    padding: 12px 16px;
    display: flex;
    justify-content: space-between;
    background-color: var(--color-fill-1);
    font-size: 13px;
    .color-red b { color: #f53f3f; }
    .color-green b { color: #00b42a; }
  }

  .monitor-info-grid {
    display: flex;
    align-items: center;
    gap: 20px;
    font-size: 13px;
  }

  .stat-row {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    border-bottom: 1px solid var(--color-fill-3);
    font-size: 13px;
  }

  :deep(.row-suspicious) {
    background-color: rgba(245, 63, 63, 0.05) !important;
    .arco-table-td { color: #f53f3f !important; font-weight: 600; }
  }

  :deep(.row-risk) {
    background-color: rgba(0, 180, 42, 0.05) !important;
  }
}
</style>