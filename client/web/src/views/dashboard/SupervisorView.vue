<template>
  <div class="supervisor-view">
    <!-- 顶部：单兵战报精准查询 -->
    <div class="user-search-section">
      <a-card title="🔍 单兵战报精准查询" class="search-card">
        <template #extra>
          <a-space>
            <a-date-picker
              v-model="searchStartDate"
              placeholder="开始日期"
              style="width: 150px"
              :disabled="searchingUser"
            />
            <span>至</span>
            <a-date-picker
              v-model="searchEndDate"
              placeholder="结束日期"
              style="width: 150px"
              :disabled="searchingUser"
            />
          </a-space>
        </template>
        
        <div class="search-input-group">
          <a-input-search
            v-model="searchKeyword"
            placeholder="输入员工姓名、用户名或ID进行搜索"
            :loading="searchingUser"
            @search="searchUserStats"
            @press-enter="searchUserStats"
            class="search-input"
          >
            <template #button>
              <a-button type="primary" :loading="searchingUser">
                <template #icon>
                  <icon-search />
                </template>
                精准查询
              </a-button>
            </template>
          </a-input-search>
          
          <div class="search-hint">
            <icon-info-circle />
            支持模糊搜索：可输入姓名、用户名或员工ID
          </div>
        </div>
        
        <!-- 搜索结果提示 -->
        <div v-if="searchResults.length > 0" class="search-results-hint">
          <icon-check-circle style="color: #52c41a" />
          找到 {{ searchResults.length }} 个匹配的员工
          <a-button type="text" size="small" @click="clearSearch">
            <template #icon>
              <icon-close />
            </template>
            清空
          </a-button>
        </div>
        
        <!-- 搜索结果列表 -->
        <div v-if="searchResults.length > 0" class="search-results">
          <a-list :data="searchResults" :bordered="false" size="small">
            <template #item="{ item }">
              <a-list-item class="search-result-item">
                <a-list-item-meta>
                  <template #avatar>
                    <a-avatar :size="32" :style="{ backgroundColor: getUserColor(item.role) }">
                      {{ item.username?.charAt(0)?.toUpperCase() || 'U' }}
                    </a-avatar>
                  </template>
                  <template #title>
                    <div class="user-title">
                      <span class="user-name">{{ item.full_name }}</span>
                      <a-tag :color="getRoleColor(item.role)" size="small">
                        {{ getRoleLabel(item.role) }}
                      </a-tag>
                    </div>
                  </template>
                  <template #description>
                    <div class="user-details">
                      <span class="username">@{{ item.username }}</span>
                      <span class="user-id">ID: {{ item.id }}</span>
                      <span class="user-email">{{ item.email }}</span>
                    </div>
                  </template>
                </a-list-item-meta>
                <template #actions>
                  <a-button type="primary" size="small" @click="showUserStats(item)">
                    <template #icon>
                      <icon-eye />
                    </template>
                    查看战报
                  </a-button>
                </template>
              </a-list-item>
            </template>
          </a-list>
        </div>
      </a-card>
    </div>
    
    <!-- 中部：团队实时看板 -->
    <div class="dashboard-section">
      <a-card title="📊 团队实时看板" class="dashboard-card">
        <!-- 时间范围选择 -->
        <div class="time-range-section">
          <div class="section-header">
            <icon-calendar />
            <span>数据时间范围</span>
          </div>
          
          <a-space :size="16">
            <a-date-picker
              v-model="startDate"
              placeholder="开始日期"
              style="width: 150px"
              :disabled="loadingInsight"
            />
            <span>至</span>
            <a-date-picker
              v-model="endDate"
              placeholder="结束日期"
              style="width: 150px"
              :disabled="loadingInsight"
            />
            <a-button type="primary" @click="loadTeamInsight" :loading="loadingInsight">
              <template #icon>
                <icon-refresh />
              </template>
              查询数据
            </a-button>
            <a-button type="outline" @click="resetDateRange">
              <template #icon>
                <icon-reset />
              </template>
              重置
            </a-button>
          </a-space>
        </div>
        
        <!-- 数据展示区域 -->
        <div v-if="loadingInsight" class="loading-state">
          <a-spin size="large">
            <div class="loading-content">
              <icon-loading />
              <div class="loading-text">正在加载团队数据...</div>
            </div>
          </a-spin>
        </div>
        
        <div v-else-if="!teamInsight && !loadingInsight" class="empty-state">
          <a-empty description="暂无团队数据">
            <template #image>
              <icon-pie-chart />
            </template>
            <div class="empty-hint">
              请选择时间范围并点击"查询数据"
            </div>
          </a-empty>
        </div>
        
        <div v-else-if="teamInsight" class="data-display">
          <!-- 总体统计卡片 -->
          <div class="overall-stats">
            <a-row :gutter="24">
              <a-col :span="6">
                <a-statistic
                  title="总任务量"
                  :value="teamInsight.overall_stats?.total_tasks || 0"
                  :precision="0"
                  show-group-separator
                >
                  <template #prefix>
                    <icon-file-text style="color: #1890ff" />
                  </template>
                </a-statistic>
              </a-col>
              
              <a-col :span="6">
                <a-statistic
                  title="总审核场次"
                  :value="teamInsight.overall_stats?.total_reviewed || 0"
                  :precision="0"
                  show-group-separator
                >
                  <template #prefix>
                    <icon-check-circle style="color: #52c41a" />
                  </template>
                </a-statistic>
              </a-col>
              
              <a-col :span="6">
                <a-statistic
                  title="总违规拦截"
                  :value="teamInsight.overall_stats?.total_violations || 0"
                  :precision="0"
                  show-group-separator
                >
                  <template #prefix>
                    <icon-flag style="color: #f5222d" />
                  </template>
                </a-statistic>
              </a-col>
              
              <a-col :span="6">
                <a-statistic
                  title="人均审核场次"
                  :value="teamInsight.overall_stats?.avg_reviewed_per_user || 0"
                  :precision="1"
                  show-group-separator
                >
                  <template #prefix>
                    <icon-user style="color: #722ed1" />
                  </template>
                </a-statistic>
              </a-col>
            </a-row>
            
            <!-- 时间范围提示 -->
            <div class="period-hint">
              <icon-clock-circle />
              数据时间: {{ teamInsight.period?.start }} 至 {{ teamInsight.period?.end }}
            </div>
          </div>
          
          <!-- 用户绩效明细 -->
          <div class="user-performance">
            <div class="section-header">
              <icon-team />
              <span>用户绩效明细 (共 {{ teamInsight.overall_stats?.total_users || 0 }} 人)</span>
            </div>
            
            <a-table
              :data="teamInsight.user_stats || []"
              :pagination="false"
              :scroll="{ y: 300 }"
              size="small"
              class="performance-table"
            >
              <template #columns>
                <a-table-column title="员工" data-index="username" :width="100">
                  <template #cell="{ record }">
                    <div class="user-cell">
                      <a-avatar :size="24" :style="{ backgroundColor: getUserColor(record.role) }">
                        {{ record.username?.charAt(0)?.toUpperCase() || 'U' }}
                      </a-avatar>
                      <span>{{ record.username }}</span>
                    </div>
                  </template>
                </a-table-column>
                
                <a-table-column title="姓名" data-index="full_name" :width="80" />
                
                <a-table-column title="审核场次" data-index="total_reviewed" :width="90">
                  <template #cell="{ record }">
                    <span class="stat-value">{{ record.total_reviewed || 0 }}</span>
                  </template>
                </a-table-column>
                
                <a-table-column title="违规拦截" data-index="total_violations" :width="90">
                  <template #cell="{ record }">
                    <span class="stat-value" :class="{ 'high-violation': record.total_violations > 5 }">
                      {{ record.total_violations || 0 }}
                    </span>
                  </template>
                </a-table-column>
                
                <a-table-column title="工作时长" data-index="total_duration" :width="100">
                  <template #cell="{ record }">
                    <span class="stat-value">{{ formatDuration(record.total_duration || 0) }}</span>
                  </template>
                </a-table-column>
                
                <a-table-column title="违规率" data-index="violation_rate" :width="80">
                  <template #cell="{ record }">
                    <span class="stat-value" :class="getViolationRateClass(record.violation_rate)">
                      {{ ((record.violation_rate || 0) * 100).toFixed(1) }}%
                    </span>
                  </template>
                </a-table-column>
                
                <a-table-column title="操作" :width="100" fixed="right">
                  <template #cell="{ record }">
                    <a-button type="text" size="small" @click="showUserStats(record)">
                      <template #icon>
                        <icon-eye />
                      </template>
                      详情
                    </a-button>
                  </template>
                </a-table-column>
              </template>
            </a-table>
          </div>
          
          <!-- 各通道工作量对比 -->
          <div class="channel-comparison">
            <div class="section-header">
              <icon-bar-chart />
              <span>各通道工作量对比 (共 {{ teamInsight.channel_stats?.length || 0 }} 个通道)</span>
            </div>
            
            <div class="channel-charts">
              <!-- 任务量对比 -->
              <div class="chart-container">
                <div class="chart-title">
                  <icon-pie-chart />
                  <span>任务量分布</span>
                </div>
                
                <div v-if="teamInsight.channel_stats && teamInsight.channel_stats.length > 0" class="mock-chart">
                  <div v-for="channel in teamInsight.channel_stats" :key="channel.channel" class="chart-bar">
                    <div class="bar-label">
                      <span>{{ getChannelLabel(channel.channel) }}</span>
                      <span class="bar-value">{{ channel.total_tasks || 0 }}</span>
                    </div>
                    <div class="bar-track">
                      <div 
                        class="bar-fill" 
                        :style="{ 
                          width: `${getChannelPercentage(channel.total_tasks || 0)}%`,
                          backgroundColor: getChannelColor(channel.channel)
                        }"
                      ></div>
                    </div>
                  </div>
                </div>
                
                <div v-else class="no-data">
                  <icon-file-exclamation />
                  <span>暂无通道数据</span>
                </div>
              </div>
              
              <!-- 审核场次对比 -->
              <div class="chart-container">
                <div class="chart-title">
                  <icon-line-chart />
                  <span>审核场次分布</span>
                </div>
                
                <div v-if="teamInsight.channel_stats && teamInsight.channel_stats.length > 0" class="mock-chart">
                  <div v-for="channel in teamInsight.channel_stats" :key="channel.channel" class="chart-bar">
                    <div class="bar-label">
                      <span>{{ getChannelLabel(channel.channel) }}</span>
                      <span class="bar-value">{{ channel.total_reviewed || 0 }}</span>
                    </div>
                    <div class="bar-track">
                      <div 
                        class="bar-fill" 
                        :style="{ 
                          width: `${getChannelPercentage(channel.total_reviewed || 0)}%`,
                          backgroundColor: getChannelColor(channel.channel)
                        }"
                      ></div>
                    </div>
                  </div>
                </div>
                
                <div v-else class="no-data">
                  <icon-file-exclamation />
                  <span>暂无通道数据</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </a-card>
    </div>
    
    <!-- 底部：人事与权限管理 -->
    <div class="personnel-management-section">
      <a-card title="👥 人事与权限管理" class="management-card">
        <template #extra>
          <a-space>
            <a-button type="primary" size="small" @click="loadAllUsers" :loading="loadingUsers">
              <template #icon>
                <icon-refresh />
              </template>
              刷新列表
            </a-button>
            <a-select
              v-model="userFilterRole"
              placeholder="按角色筛选"
              style="width: 120px"
              size="small"
              @change="filterUsersByRole"
            >
              <a-option value="">全部角色</a-option>
              <a-option value="supervisor">主管</a-option>
              <a-option value="shift_leader">组长</a-option>
              <a-option value="auditor">审核员</a-option>
            </a-select>
          </a-space>
        </template>
        
        <!-- 用户管理表格 -->
        <a-table
          :data="filteredUsers"
          :pagination="{ pageSize: 10, showTotal: true }"
          :scroll="{ x: 1200, y: 400 }"
          :loading="loadingUsers"
          size="small"
          class="user-management-table"
        >
          <template #columns>
            <a-table-column title="ID" data-index="id" :width="70" fixed="left" />
            
            <a-table-column title="用户名" data-index="username" :width="100" fixed="left">
              <template #cell="{ record }">
                <div class="user-cell">
                  <a-avatar :size="28" :style="{ backgroundColor: getUserColor(record.role) }">
                    {{ record.username?.charAt(0)?.toUpperCase() || 'U' }}
                  </a-avatar>
                  <span class="username-text">{{ record.username }}</span>
                </div>
              </template>
            </a-table-column>
            
            <a-table-column title="姓名" data-index="full_name" :width="90" />
            
            <a-table-column title="邮箱" data-index="email" :width="180">
              <template #cell="{ record }">
                <span class="email-text">{{ record.email }}</span>
              </template>
            </a-table-column>
            
            <a-table-column title="当前角色" data-index="role" :width="100">
              <template #cell="{ record }">
                <a-tag :color="getRoleColor(record.role)" size="small">
                  {{ getRoleLabel(record.role) }}
                </a-tag>
              </template>
            </a-table-column>
            
            <a-table-column title="管理员" data-index="is_admin" :width="80">
              <template #cell="{ record }">
                <a-tag :color="record.is_admin ? 'green' : 'gray'" size="small">
                  {{ record.is_admin ? '是' : '否' }}
                </a-tag>
              </template>
            </a-table-column>
            
            <a-table-column title="状态" data-index="is_active" :width="80">
              <template #cell="{ record }">
                <a-tag :color="record.is_active ? 'blue' : 'red'" size="small">
                  {{ record.is_active ? '活跃' : '禁用' }}
                </a-tag>
              </template>
            </a-table-column>
            
            <a-table-column title="创建时间" data-index="created_at" :width="120">
              <template #cell="{ record }">
                <span class="time-text">{{ formatTime(record.created_at) }}</span>
              </template>
            </a-table-column>
            
            <a-table-column title="最后更新" data-index="updated_at" :width="120">
              <template #cell="{ record }">
                <span class="time-text">{{ formatTime(record.updated_at) }}</span>
              </template>
            </a-table-column>
            
            <a-table-column title="操作" :width="180" fixed="right">
              <template #cell="{ record }">
                <a-space :size="8">
                  <!-- 角色修改下拉框 -->
                  <a-select
                    v-model="record.role"
                    :style="{ width: '100px' }"
                    size="small"
                    @change="(value: any) => handleUpdateUserRole(record.id, value)"
                    :disabled="record.id === currentUserId"
                  >
                    <a-option value="supervisor">主管</a-option>
                    <a-option value="shift_leader">组长</a-option>
                    <a-option value="auditor">审核员</a-option>
                  </a-select>
                  
                  <!-- 查看详情按钮 -->
                  <a-button type="text" size="small" @click="showUserStats(record)">
                    <template #icon>
                      <icon-eye />
                    </template>
                    详情
                  </a-button>
                </a-space>
              </template>
            </a-table-column>
          </template>
        </a-table>
        
        <!-- 表格底部统计 -->
        <div class="table-footer">
          <div class="footer-stats">
            <div class="stat-item">
              <icon-team />
              <span>总人数:</span>
              <strong>{{ allUsers.length }}</strong>
            </div>
            <div class="stat-item">
              <icon-user-group />
              <span>角色分布:</span>
              <div class="role-distribution">
                <a-tag v-for="(count, role) in roleDistribution" :key="role" :color="getRoleColor(role as any)" size="small">
                  {{ getRoleLabel(role as any) }}: {{ count }}
                </a-tag>
              </div>
            </div>
          </div>
        </div>
      </a-card>
    </div>
    
    <!-- 用户详细统计抽屉 -->
    <a-drawer
      v-model:visible="userStatsVisible"
      title="单兵战报详情"
      :width="800"
      :footer="false"
      :mask-closable="true"
      class="user-stats-drawer"
    >
      <div v-if="selectedUser && userStats" class="user-stats-content">
        <!-- 用户基本信息 -->
        <div class="user-basic-info">
          <div class="user-avatar-section">
            <a-avatar :size="64" :style="{ backgroundColor: getUserColor(selectedUser.role) }">
              {{ selectedUser.username?.charAt(0)?.toUpperCase() || 'U' }}
            </a-avatar>
            <div class="user-title">
              <h3>{{ selectedUser.full_name }}</h3>
              <div class="user-subtitle">
                <a-tag :color="getRoleColor(selectedUser.role)" size="small">
                  {{ getRoleLabel(selectedUser.role) }}
                </a-tag>
                <span class="username">@{{ selectedUser.username }}</span>
                <span class="user-id">ID: {{ selectedUser.id }}</span>
              </div>
            </div>
          </div>
          
          <!-- 统计时间段 -->
          <div class="stats-period">
            <icon-calendar />
            <span>统计时间: {{ userStats.period?.start }} 至 {{ userStats.period?.end }}</span>
          </div>
        </div>
        
        <!-- 总体统计 -->
        <div class="user-overall-stats">
          <a-row :gutter="16">
            <a-col :span="6">
              <a-statistic
                title="总任务量"
                :value="Number(userStats.summary?.total_tasks || 0)"
                :precision="0"
                show-group-separator
              >
                <template #prefix>
                  <icon-file-text style="color: #1890ff" />
                </template>
              </a-statistic>
            </a-col>
            
            <a-col :span="6">
              <a-statistic
                title="总审核场次"
                :value="Number(userStats.summary?.total_reviewed || 0)"
                :precision="0"
                show-group-separator
              >
                <template #prefix>
                  <icon-check-circle style="color: #52c41a" />
                </template>
              </a-statistic>
            </a-col>
            
            <a-col :span="6">
              <a-statistic
                title="违规拦截"
                :value="Number(userStats.summary?.total_violations || 0)"
                :precision="0"
                show-group-separator
              >
                <template #prefix>
                  <icon-flag style="color: #f5222d" />
                </template>
              </a-statistic>
            </a-col>
            
            <a-col :span="6">
              <a-statistic
                title="违规率"
                :value="+(((userStats.summary?.violation_rate || 0) * 100).toFixed(1))"
                suffix="%"
                :precision="1"
              >
                <template #prefix>
                  <icon-pie-chart style="color: #722ed1" />
                </template>
              </a-statistic>
            </a-col>
          </a-row>
        </div>
        
        <!-- 通道工作量分布 -->
        <div class="user-channel-stats">
          <div class="section-header">
            <icon-bar-chart />
            <span>各通道工作量分布</span>
          </div>
          
          <a-table
            :data="userStats.channel_stats || []"
            :pagination="false"
            size="small"
            class="channel-stats-table"
          >
            <template #columns>
              <a-table-column title="通道类型" data-index="channel" :width="120">
                <template #cell="{ record }">
                  <a-tag :color="getChannelColor(record.channel)" size="small">
                    {{ getChannelLabel(record.channel) }}
                  </a-tag>
                </template>
              </a-table-column>
              
              <a-table-column title="任务量" data-index="task_count" :width="90">
                <template #cell="{ record }">
                  <span class="stat-value">{{ record.task_count || 0 }}</span>
                </template>
              </a-table-column>
              
              <a-table-column title="审核场次" data-index="total_reviewed" :width="90">
                <template #cell="{ record }">
                  <span class="stat-value">{{ record.total_reviewed || 0 }}</span>
                </template>
              </a-table-column>
              
              <a-table-column title="违规数" data-index="total_violations" :width="80">
                <template #cell="{ record }">
                  <span class="stat-value">{{ record.total_violations || 0 }}</span>
                </template>
              </a-table-column>
              
              <a-table-column title="工作时长" data-index="total_duration" :width="100">
                <template #cell="{ record }">
                  <span class="stat-value">{{ formatDuration(record.total_duration || 0) }}</span>
                </template>
              </a-table-column>
              
              <a-table-column title="占比" data-index="percentage" :width="80">
                <template #cell="{ record }">
                  <span class="stat-value">
                    {{ calculatePercentage(record.task_count, userStats.summary?.total_tasks) }}%
                  </span>
                </template>
              </a-table-column>
            </template>
          </a-table>
        </div>
        
        <!-- 最近班次记录 -->
        <div class="user-recent-shifts">
          <div class="section-header">
            <icon-history />
            <span>最近班次记录 (最近10次)</span>
          </div>
          
          <a-table
            :data="userStats.recent_shifts || []"
            :pagination="false"
            :scroll="{ y: 200 }"
            size="small"
            class="shifts-table"
          >
            <template #columns>
              <a-table-column title="日期" data-index="shift_date" :width="100" />
              
              <a-table-column title="班次" data-index="shift_type" :width="80">
                <template #cell="{ record }">
                  <a-tag :color="getShiftTypeColor(record.shift_type)" size="small">
                    {{ getShiftTypeLabel(record.shift_type) }}
                  </a-tag>
                </template>
              </a-table-column>
              
              <a-table-column title="通道" data-index="task_channel" :width="100">
                <template #cell="{ record }">
                  <a-tag :color="getChannelColor(record.task_channel)" size="small">
                    {{ getChannelLabel(record.task_channel) }}
                  </a-tag>
                </template>
              </a-table-column>
              
              <a-table-column title="审核场次" data-index="reviewed_count" :width="90">
                <template #cell="{ record }">
                  <span class="stat-value">{{ record.reviewed_count || 0 }}</span>
                </template>
              </a-table-column>
              
              <a-table-column title="违规数" data-index="violation_count" :width="80">
                <template #cell="{ record }">
                  <span class="stat-value">{{ record.violation_count || 0 }}</span>
                </template>
              </a-table-column>
              
              <a-table-column title="工作时长" data-index="work_duration" :width="100">
                <template #cell="{ record }">
                  <span class="stat-value">{{ formatDuration(record.work_duration || 0) }}</span>
                </template>
              </a-table-column>
              
              <a-table-column title="状态" data-index="is_completed" :width="80">
                <template #cell="{ record }">
                  <a-tag :color="record.is_completed ? 'green' : 'orange'" size="small">
                    {{ record.is_completed ? '已完成' : '进行中' }}
                  </a-tag>
                </template>
              </a-table-column>
            </template>
          </a-table>
        </div>
      </div>
      
      <div v-else class="drawer-loading">
        <a-spin size="large">
          <div class="loading-content">
            <icon-loading />
            <div class="loading-text">正在加载用户数据...</div>
          </div>
        </a-spin>
      </div>
    </a-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import dayjs from 'dayjs'
import { 
  rbacApi, 
  type TeamInsightResponse,
  getRoleLabel,
  getRoleColor,
  getShiftTypeLabel
} from '@/api/rbac'

// ==================== 响应式数据 ====================

// 团队看板数据
const startDate = ref<string>(dayjs().subtract(7, 'day').format('YYYY-MM-DD'))
const endDate = ref<string>(dayjs().format('YYYY-MM-DD'))
const teamInsight = ref<TeamInsightResponse | null>(null)
const loadingInsight = ref(false)

// 单兵战报搜索
const searchKeyword = ref('')
const searchStartDate = ref<string>(dayjs().subtract(30, 'day').format('YYYY-MM-DD'))
const searchEndDate = ref<string>(dayjs().format('YYYY-MM-DD'))
const searchResults = ref<any[]>([])
const searchingUser = ref(false)

// 人事权限管理
const allUsers = ref<any[]>([])
const filteredUsers = ref<any[]>([])
const userFilterRole = ref('')
const loadingUsers = ref(false)
const currentUserId = ref<number | null>(null)

// 用户详细统计
const userStatsVisible = ref(false)
const selectedUser = ref<any>(null)
const userStats = ref<any>(null)

// ==================== 计算属性 ====================

// 角色分布统计
const roleDistribution = computed(() => {
  const distribution: Record<string, number> = {}
  allUsers.value.forEach(user => {
    distribution[user.role] = (distribution[user.role] || 0) + 1
  })
  return distribution
})

// ==================== 工具函数 ====================

// 获取用户颜色
const getUserColor = (role: string) => {
  const colors: Record<string, string> = {
    'supervisor': '#f5222d',
    'shift_leader': '#fa8c16',
    'auditor': '#52c41a'
  }
  return colors[role] || '#1890ff'
}

// 获取通道颜色
const getChannelColor = (channel: string) => {
  const colors: Record<string, string> = {
    'image': 'blue',
    'chat': 'green',
    'video': 'orange',
    'live': 'purple'
  }
  return colors[channel] || 'gray'
}

// 获取通道标签
const getChannelLabel = (channel: string) => {
  const labels: Record<string, string> = {
    'image': '图片审核',
    'chat': '单聊审核',
    'video': '视频审核',
    'live': '直播间巡查'
  }
  return labels[channel] || channel
}

// 获取班次类型颜色
const getShiftTypeColor = (shiftType: string) => {
  const colors: Record<string, string> = {
    'morning': 'blue',
    'afternoon': 'green',
    'night': 'purple'
  }
  return colors[shiftType] || 'gray'
}

// 获取班次类型标签

// 格式化时长
const formatDuration = (seconds: number): string => {
  if (seconds < 60) return `${seconds}秒`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}分钟`
  return `${Math.floor(seconds / 3600)}小时${Math.floor((seconds % 3600) / 60)}分钟`
}

// 格式化时间
const formatTime = (timeStr: string): string => {
  if (!timeStr) return '-'
  return dayjs(timeStr).format('MM-DD HH:mm')
}

// 计算通道百分比
const getChannelPercentage = (value: number): number => {
  if (!teamInsight.value?.channel_stats || teamInsight.value.channel_stats.length === 0) return 0
  
  const maxValue = Math.max(...teamInsight.value.channel_stats.map(c => c.total_tasks || 0))
  if (maxValue === 0) return 0
  
  return (value / maxValue) * 100
}

// 计算占比
const calculatePercentage = (part: number, total: number): string => {
  if (!total || total === 0) return '0.0'
  return ((part / total) * 100).toFixed(1)
}

// 获取违规率样式类
const getViolationRateClass = (rate: number) => {
  if (!rate) return ''
  if (rate > 0.1) return 'high-violation-rate'
  if (rate > 0.05) return 'medium-violation-rate'
  return 'low-violation-rate'
}

// ==================== 核心功能函数 ====================

// 1. 团队看板数据加载
const loadTeamInsight = async () => {
  if (!startDate.value || !endDate.value) {
    Message.warning('请选择时间范围')
    return
  }
  
  loadingInsight.value = true
  try {
    const response = await rbacApi.getTeamInsight({
      start_date: startDate.value,
      end_date: endDate.value
    })
    teamInsight.value = response
    console.log('✅ 团队数据加载成功:', response)
  } catch (error) {
    console.error('❌ 加载团队数据失败:', error)
    Message.error('加载数据失败，请检查后端服务')
    teamInsight.value = null
  } finally {
    loadingInsight.value = false
  }
}

const resetDateRange = () => {
  startDate.value = dayjs().subtract(7, 'day').format('YYYY-MM-DD')
  endDate.value = dayjs().format('YYYY-MM-DD')
  teamInsight.value = null
}

// 2. 单兵战报搜索
const searchUserStats = async () => {
  if (!searchKeyword.value.trim()) {
    Message.warning('请输入搜索关键词')
    return
  }
  
  searchingUser.value = true
  try {
    // 先获取所有用户
    const response = await rbacApi.getActiveUsers()
    const allUsers = response.users
    
    // 根据关键词筛选
    const keyword = searchKeyword.value.toLowerCase().trim()
    searchResults.value = allUsers.filter(user => {
      return (
        user.username.toLowerCase().includes(keyword) ||
        user.full_name.toLowerCase().includes(keyword) ||
        user.id.toString().includes(keyword) ||
        user.email.toLowerCase().includes(keyword)
      )
    })
    
    if (searchResults.value.length === 0) {
      Message.info('未找到匹配的员工')
    } else {
      Message.success(`找到 ${searchResults.value.length} 个匹配的员工`)
    }
  } catch (error) {
    console.error('❌ 搜索用户失败:', error)
    Message.error('搜索失败，请检查网络连接')
    searchResults.value = []
  } finally {
    searchingUser.value = false
  }
}

const clearSearch = () => {
  searchKeyword.value = ''
  searchResults.value = []
}

// 3. 显示用户详细统计
const showUserStats = async (user: any) => {
  selectedUser.value = user
  userStatsVisible.value = true
  
  try {
    const response = await rbacApi.getUserDetailedStats(
      user.id,
      searchStartDate.value,
      searchEndDate.value
    )
    userStats.value = response
  } catch (error) {
    console.error('❌ 加载用户详细统计失败:', error)
    Message.error('加载用户数据失败')
    userStats.value = null
  }
}

// 4. 人事权限管理
const loadAllUsers = async () => {
  loadingUsers.value = true
  try {
    const response = await rbacApi.getActiveUsers()
    allUsers.value = response.users
    filteredUsers.value = [...allUsers.value]
    
    // 获取当前用户ID
    try {
      const userInfo = localStorage.getItem('ahdunyi_user_info') || localStorage.getItem('user_info')
      if (userInfo) {
        const user = JSON.parse(userInfo)
        currentUserId.value = user.id
      }
    } catch (error) {
      console.error('获取当前用户ID失败:', error)
    }
    
    Message.success(`已加载 ${allUsers.value.length} 名员工`)
  } catch (error) {
    console.error('❌ 加载用户列表失败:', error)
    Message.error('加载用户列表失败')
  } finally {
    loadingUsers.value = false
  }
}

const filterUsersByRole = () => {
  if (!userFilterRole.value) {
    filteredUsers.value = [...allUsers.value]
  } else {
    filteredUsers.value = allUsers.value.filter(user => user.role === userFilterRole.value)
  }
}

// 5. 更新用户角色
const handleUpdateUserRole = async (userId: number, newRole: string) => {
  try {
    const response = await rbacApi.updateUserRole(userId, newRole)
    
    if (response.success) {
      Message.success(response.message)
      
      // 更新本地数据
      const userIndex = allUsers.value.findIndex(user => user.id === userId)
      if (userIndex !== -1) {
        allUsers.value[userIndex].role = newRole
        filterUsersByRole() // 重新筛选
      }
    } else {
      Message.error('更新角色失败')
    }
  } catch (error) {
    console.error('❌ 更新用户角色失败:', error)
    Message.error('更新角色失败，请检查权限')
  }
}

// ==================== 生命周期 ====================
onMounted(() => {
  // 默认加载用户列表
  loadAllUsers()
  
  // 默认加载团队数据
  loadTeamInsight()
})
</script>

<style scoped>
.supervisor-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 0;
}

/* ==================== 单兵战报搜索 ==================== */
.search-card {
  background: var(--color-bg-2);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.search-input-group {
  margin-bottom: 16px;
}

.search-input {
  margin-bottom: 8px;
}

.search-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--color-text-3);
  margin-top: 8px;
}

.search-results-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 16px 0;
  padding: 12px;
  background: var(--color-bg-3);
  border-radius: 6px;
  font-size: 14px;
  color: var(--color-text-2);
}

.search-results {
  margin-top: 16px;
}

.search-result-item {
  padding: 12px;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.search-result-item:hover {
  background: var(--color-bg-3);
}

.user-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-name {
  font-weight: 500;
  color: var(--color-text-1);
}

.user-details {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--color-text-3);
}

.username {
  color: var(--color-text-2);
}

.user-id {
  color: var(--color-text-3);
}

.user-email {
  color: var(--color-text-3);
}

/* ==================== 团队实时看板 ==================== */
.dashboard-card {
  background: var(--color-bg-2);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.time-range-section {
  margin-bottom: 24px;
  padding: 16px;
  background: var(--color-bg-3);
  border-radius: 8px;
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

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.loading-text {
  color: var(--color-text-2);
  font-size: 14px;
}

.empty-state {
  padding: 60px 0;
  text-align: center;
}

.empty-hint {
  margin-top: 8px;
  font-size: 14px;
  color: var(--color-text-3);
}

/* 总体统计 */
.overall-stats {
  margin-bottom: 32px;
  padding: 24px;
  background: var(--color-bg-3);
  border-radius: 8px;
}

.period-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  font-size: 14px;
  color: var(--color-text-2);
}

/* 用户绩效明细 */
.user-performance {
  margin-bottom: 32px;
}

.performance-table {
  background: transparent;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-value {
  font-weight: 500;
  color: var(--color-text-1);
}

.high-violation {
  color: var(--color-error);
  font-weight: 600;
}

.high-violation-rate {
  color: var(--color-error);
  font-weight: 600;
}

.medium-violation-rate {
  color: var(--color-warning);
  font-weight: 500;
}

.low-violation-rate {
  color: var(--color-success);
  font-weight: 500;
}

/* 通道工作量对比 */
.channel-comparison {
  margin-bottom: 24px;
}

.channel-charts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

@media (max-width: 1200px) {
  .channel-charts {
    grid-template-columns: 1fr;
  }
}

.chart-container {
  padding: 20px;
  background: var(--color-bg-3);
  border-radius: 8px;
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 500;
  color: var(--color-text-1);
}

.mock-chart {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chart-bar {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.bar-label {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: var(--color-text-2);
}

.bar-value {
  font-weight: 500;
  color: var(--color-text-1);
}

.bar-track {
  height: 8px;
  background: var(--color-fill-3);
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 40px 0;
  color: var(--color-text-3);
}

/* ==================== 人事与权限管理 ==================== */
.management-card {
  background: var(--color-bg-2);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.user-management-table {
  background: transparent;
}

.username-text {
  margin-left: 8px;
  font-weight: 500;
  color: var(--color-text-1);
}

.email-text {
  color: var(--color-text-2);
  font-size: 13px;
}

.time-text {
  color: var(--color-text-3);
  font-size: 12px;
}

.table-footer {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--color-border-2);
}

.footer-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--color-text-2);
}

.stat-item strong {
  color: var(--color-text-1);
  font-weight: 600;
}

.role-distribution {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

/* ==================== 用户详细统计抽屉 ==================== */
.user-stats-drawer :deep(.arco-drawer-content) {
  background: var(--color-bg-2);
}

.user-stats-content {
  padding: 0;
}

.user-basic-info {
  padding: 24px;
  background: var(--color-bg-3);
  border-radius: 8px;
  margin-bottom: 24px;
}

.user-avatar-section {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.user-title h3 {
  margin: 0;
  font-size: 20px;
  color: var(--color-text-1);
}

.user-subtitle {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}

.stats-period {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--color-text-2);
}

.user-overall-stats {
  margin-bottom: 32px;
  padding: 24px;
  background: var(--color-bg-3);
  border-radius: 8px;
}

.user-channel-stats {
  margin-bottom: 32px;
}

.channel-stats-table {
  background: transparent;
}

.user-recent-shifts {
  margin-bottom: 24px;
}

.shifts-table {
  background: transparent;
}

.drawer-loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}

/* ==================== 响应式调整 ==================== */
@media (max-width: 768px) {
  .channel-charts {
    grid-template-columns: 1fr;
  }
  
  .footer-stats {
    flex-direction: column;
    gap: 12px;
  }
  
  .user-subtitle {
    flex-wrap: wrap;
  }
}
</style>