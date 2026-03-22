<template>
  <div class="settings-page">
    <!-- 页头 -->
    <div class="page-header">
      <div class="header-left">
        <div class="page-icon-wrap">
          <icon-user-group :size="18" />
        </div>
        <div class="page-title-group">
          <span class="page-title">人事与权限管理</span>
          <span class="page-subtitle">Personnel &amp; Access Control</span>
        </div>
        <a-tag color="red" size="small">风控经理专属</a-tag>
      </div>
      <div class="header-actions">
        <a-button @click="loadUsers">
          <template #icon><icon-refresh /></template>刷新
        </a-button>
        <a-button type="primary" @click="openCreateModal" v-if="permissionStore.can('action:update_role')">
          <template #icon><icon-plus /></template>新增人员
        </a-button>
      </div>
    </div>

    <!-- 角色统计卡片 -->
    <div class="stat-cards" v-if="!loading">
      <div class="stat-card" v-for="stat in roleStats" :key="stat.value">
        <div class="stat-top">
          <a-tag :color="stat.color" size="small">{{ stat.label }}</a-tag>
          <span class="stat-count">{{ stat.count }}</span>
        </div>
        <div class="stat-bar"><div class="stat-fill" :style="{ width: stat.pct + '%', background: stat.hex }"></div></div>
      </div>
    </div>

    <!-- 工具栏 -->
    <div class="toolbar">
      <a-input-search v-model="searchText" placeholder="搜索用户名 / 姓名" style="width:240px" allow-clear />
      <a-select v-model="filterRole" placeholder="角色筛选" style="width:150px" allow-clear>
        <a-option value="">全部角色</a-option>
        <a-option v-for="r in permissionStore.allRoles" :key="r.value" :value="r.value">{{ r.label }}</a-option>
      </a-select>
      <a-select v-model="filterStatus" style="width:120px">
        <a-option value="all">全部状态</a-option>
        <a-option value="active">在职</a-option>
        <a-option value="inactive">停用</a-option>
      </a-select>
    </div>

    <!-- 用户表格 -->
    <div class="table-wrap">
    <a-table :data="filteredUsers" :loading="loading" :pagination="{ pageSize: 12, showTotal: true }" row-key="id" stripe>
      <!-- Arco Table：列必须放在 #columns，否则走 default 插槽分支，data 不会渲染表体 -->
      <template #columns>
        <a-table-column title="ID" data-index="id" :width="60" />
        <a-table-column title="姓名" :width="170">
          <template #cell="{ record }">
            <div class="user-cell">
              <a-avatar :size="28" :style="{ background: getRoleHex(record.role), fontSize: '12px' }">
                {{ ((record.full_name || record.username || '?') + '')[0] }}
              </a-avatar>
              <div>
                <div class="uname">{{ record.full_name || '—' }}</div>
                <div class="ulogin">@{{ record.username || '—' }}</div>
              </div>
            </div>
          </template>
        </a-table-column>
        <a-table-column title="邮箱">
          <template #cell="{ record }">{{ record.email || '—' }}</template>
        </a-table-column>
        <a-table-column title="角色" :width="120">
          <template #cell="{ record }">
            <a-tag :color="getRoleColor(record.role)" size="small">{{ getRoleLabel(record.role) }}</a-tag>
          </template>
        </a-table-column>
        <a-table-column title="状态" :width="90">
          <template #cell="{ record }">
            <a-badge :status="record.is_active ? 'processing' : 'default'" :text="record.is_active ? '在职' : '停用'" />
          </template>
        </a-table-column>
        <a-table-column title="创建时间" :width="110">
          <template #cell="{ record }">{{ formatDate(record.created_at) }}</template>
        </a-table-column>
        <a-table-column title="操作" :width="210" v-if="permissionStore.can('action:update_role')">
          <template #cell="{ record }">
            <a-space size="mini">
              <a-tooltip content="编辑资料">
                <a-button type="text" size="mini" @click="openEditModal(record)"><template #icon><icon-edit /></template></a-button>
              </a-tooltip>
              <a-tooltip content="修改角色">
                <a-button type="text" size="mini" @click="openRoleModal(record)"><template #icon><icon-user-group /></template></a-button>
              </a-tooltip>
              <a-tooltip content="重置密码">
                <a-button type="text" size="mini" @click="openPasswordModal(record)"><template #icon><icon-lock /></template></a-button>
              </a-tooltip>
              <a-tooltip :content="record.is_active ? '停用账号' : '启用账号'">
                <a-button type="text" size="mini"
                  :status="record.is_active ? 'warning' : 'success'"
                  @click="confirmToggleStatus(record)"
                  :disabled="record.id === selfId">
                  <template #icon><icon-poweroff v-if="record.is_active" /><icon-check-circle v-else /></template>
                </a-button>
              </a-tooltip>
              <a-tooltip content="删除人员">
                <a-button type="text" size="mini" status="danger"
                  @click="confirmDelete(record)" :disabled="record.id === selfId">
                  <template #icon><icon-delete /></template>
                </a-button>
              </a-tooltip>
            </a-space>
          </template>
        </a-table-column>
      </template>
    </a-table>
    </div>

    <!-- ① 新增人员弹窗 -->
    <a-modal v-model:visible="createModal.visible" title="新增人员" :ok-loading="createModal.loading"
      @ok="submitCreate" @cancel="createModal.visible = false" width="480px">
      <a-form :model="createModal.form" layout="vertical" ref="createFormRef">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="用户名" field="username" required
              :rules="[{required:true,message:'请填写用户名'},{minLength:2,message:'至少2个字符'}]">
              <a-input v-model="createModal.form.username" placeholder="英文+数字，全局唯一" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="姓名" field="full_name" required :rules="[{required:true,message:'请填写姓名'}]">
              <a-input v-model="createModal.form.full_name" placeholder="真实姓名" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="邮箱">
          <a-input v-model="createModal.form.email" placeholder="选填" />
        </a-form-item>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="初始密码" field="password" required
              :rules="[{required:true,message:'请设置密码'},{minLength:6,message:'至少6位'}]">
              <a-input-password v-model="createModal.form.password" placeholder="至少6位" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="角色" field="role" required :rules="[{required:true,message:'请选择角色'}]">
              <a-select v-model="createModal.form.role" placeholder="选择角色">
                <a-option v-for="r in permissionStore.allRoles" :key="r.value" :value="r.value">
                  <a-tag :color="r.color" size="small">{{ r.label }}</a-tag>
                </a-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="入职状态">
          <a-switch v-model="createModal.form.is_active" checked-text="立即启用" unchecked-text="暂不启用" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- ② 编辑资料弹窗 -->
    <a-modal v-model:visible="editModal.visible" title="编辑人员资料" :ok-loading="editModal.loading"
      @ok="submitEdit" @cancel="editModal.visible = false" width="420px">
      <a-form :model="editModal.form" layout="vertical">
        <a-form-item label="姓名">
          <a-input v-model="editModal.form.full_name" />
        </a-form-item>
        <a-form-item label="邮箱">
          <a-input v-model="editModal.form.email" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- ③ 修改角色弹窗 -->
    <a-modal v-model:visible="roleModal.visible" title="修改用户角色" :ok-loading="roleModal.loading"
      @ok="submitRoleChange" @cancel="roleModal.visible = false" width="400px">
      <div class="modal-user-banner">
        <a-avatar :size="36" :style="{ background: getRoleHex(roleModal.user?.role || '') }">
          {{ (roleModal.user?.full_name || 'U').charAt(0) }}
        </a-avatar>
        <div>
          <div style="font-weight:600">{{ roleModal.user?.full_name }}</div>
          <div style="font-size:12px;color:var(--color-text-3)">@{{ roleModal.user?.username }}</div>
        </div>
      </div>
      <a-divider :margin="12" />
      <a-form layout="vertical">
        <a-form-item label="当前角色">
          <a-tag :color="getRoleColor(roleModal.user?.role || '')">{{ getRoleLabel(roleModal.user?.role || '') }}</a-tag>
        </a-form-item>
        <a-form-item label="变更为" required>
          <a-select v-model="roleModal.newRole" style="width:100%">
            <a-option v-for="r in permissionStore.allRoles" :key="r.value" :value="r.value">
              <a-tag :color="r.color" size="small">{{ r.label }}</a-tag>
            </a-option>
          </a-select>
        </a-form-item>
        <a-alert type="warning">角色变更即时生效，用户下次登录权限同步更新。</a-alert>
      </a-form>
    </a-modal>

    <!-- ④ 重置密码弹窗 -->
    <a-modal v-model:visible="passwordModal.visible" title="重置密码" :ok-loading="passwordModal.loading"
      @ok="submitPasswordReset" @cancel="passwordModal.visible = false" width="400px">
      <div class="modal-user-banner">
        <a-avatar :size="36" :style="{ background: getRoleHex(passwordModal.user?.role || '') }">
          {{ (passwordModal.user?.full_name || 'U').charAt(0) }}
        </a-avatar>
        <div>
          <div style="font-weight:600">{{ passwordModal.user?.full_name }}</div>
          <div style="font-size:12px;color:var(--color-text-3)">@{{ passwordModal.user?.username }}</div>
        </div>
      </div>
      <a-divider :margin="12" />
      <a-form layout="vertical">
        <a-form-item label="新密码" required>
          <a-input-password v-model="passwordModal.newPassword" placeholder="至少6位" />
        </a-form-item>
        <a-alert type="warning">密码重置后原密码立即失效，请告知本人新密码。</a-alert>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import { rbacApi, type ActiveUser } from '@/api/rbac'
import { usePermissionStore } from '@/stores/permission'
import { auth } from '@/utils/auth'

const permissionStore = usePermissionStore()
const selfId = computed(() => (auth.getUserInfo() as any)?.id as number | undefined)

// ── state ──────────────────────────────────────────────────
const users        = ref<ActiveUser[]>([])
const loading      = ref(false)
const searchText   = ref('')
const filterRole   = ref('')
const filterStatus = ref<'all' | 'active' | 'inactive'>('all')
const createFormRef = ref()

const createModal = ref({
  visible: false, loading: false,
  form: { username: '', full_name: '', email: '', password: '', role: '', is_active: true },
})
const editModal = ref({
  visible: false, loading: false, userId: 0,
  form: { full_name: '', email: '' },
})
const roleModal = ref({
  visible: false, loading: false,
  user: null as ActiveUser | null, newRole: '',
})
const passwordModal = ref({
  visible: false, loading: false,
  user: null as ActiveUser | null, newPassword: '',
})

// ── computed ───────────────────────────────────────────────
const filteredUsers = computed(() => {
  let list = users.value
  // 角色筛选（前端完成，无需重新请求后端）
  if (filterRole.value) list = list.filter(u => u.role === filterRole.value)
  if (filterStatus.value === 'active')   list = list.filter(u => u.is_active)
  if (filterStatus.value === 'inactive') list = list.filter(u => !u.is_active)
  const q = searchText.value.trim().toLowerCase()
  if (q) {
    list = list.filter(u => {
      const un = (u.username ?? '').toLowerCase()
      const fn = (u.full_name ?? '').toLowerCase()
      return un.includes(q) || fn.includes(q)
    })
  }
  return list
})

const roleStats = computed(() => {
  const total = users.value.length || 1
  return permissionStore.allRoles.map(r => ({
    ...r,
    count: users.value.filter(u => u.role === r.value).length,
    hex:   getRoleHex(r.value),
    pct:   Math.round(users.value.filter(u => u.role === r.value).length / total * 100),
  }))
})

// ── helpers ────────────────────────────────────────────────
function getRoleLabel(role: string) { return permissionStore.allRoles.find(r => r.value === role)?.label ?? role }
function getRoleColor(role: string) { return permissionStore.allRoles.find(r => r.value === role)?.color ?? 'gray' }
const roleHexMap: Record<string, string> = {
  manager: '#f53f3f', team_leader: '#ff7d00',
  qa_specialist: '#722ed1', admin_support: '#0fc6c2', auditor: '#00b42a',
}
function getRoleHex(role: string) { return roleHexMap[role] ?? '#86909c' }
function formatDate(iso: string) { return iso ? new Date(iso).toLocaleDateString('zh-CN') : '—' }

// ── data ───────────────────────────────────────────────────
async function loadUsers() {
  loading.value = true
  users.value = []
  try {
    let res: { users: ActiveUser[]; count: number; filter_role: string } | null = null
    // 优先使用全量接口（含停用用户）
    try {
      res = await rbacApi.getAllUsers()
    } catch (e1: any) {
      console.warn('[SettingsPage] getAllUsers failed, falling back to getActiveUsers:', e1?.response?.status, e1?.message)
      // 降级：服务器旧版本只有 /api/users/active
      try {
        res = await rbacApi.getActiveUsers()
      } catch (e2: any) {
        console.error('[SettingsPage] getActiveUsers also failed:', e2?.response?.status, e2?.message)
        const detail = e2?.response?.data?.detail || e2?.message || '未知错误'
        Message.error(`加载用户列表失败：${detail}`)
        return
      }
    }
    if (res && Array.isArray(res.users)) {
      users.value = res.users
      console.log('[SettingsPage] loaded', res.users.length, 'users')
    } else {
      console.warn('[SettingsPage] unexpected response shape:', res)
      Message.warning('返回数据格式异常，请刷新重试')
    }
  } catch (e: any) {
    console.error('[SettingsPage] loadUsers unexpected error:', e)
    Message.error('加载用户列表失败，请检查网络连接或联系管理员')
  } finally {
    loading.value = false
  }
}

// ── 新增 ───────────────────────────────────────────────────
function openCreateModal() {
  createModal.value.form = { username: '', full_name: '', email: '', password: '', role: '', is_active: true }
  createModal.value.visible = true
}
async function submitCreate() {
  createModal.value.loading = true
  try {
    const f = createModal.value.form
    await rbacApi.createUser({
      username: f.username, full_name: f.full_name,
      password: f.password,
      email: f.email || undefined,
      role: f.role, is_active: f.is_active,
    })
    Message.success(`人员「${f.full_name}」创建成功`)
    createModal.value.visible = false
    await loadUsers()
  } catch (e: any) {
    Message.error(e?.response?.data?.detail || '创建失败，请检查用户名是否重复')
  } finally {
    createModal.value.loading = false
  }
}

// ── 编辑资料 ───────────────────────────────────────────────
function openEditModal(user: ActiveUser) {
  editModal.value = {
    visible: true, loading: false,
    userId: user.id, form: { full_name: user.full_name, email: (user as any).email || '' },
  }
}
async function submitEdit() {
  editModal.value.loading = true
  try {
    await rbacApi.updateUser(editModal.value.userId, editModal.value.form)
    Message.success('资料更新成功')
    editModal.value.visible = false
    await loadUsers()
  } catch {
    Message.error('更新失败，请稍后重试')
  } finally {
    editModal.value.loading = false
  }
}

// ── 修改角色 ───────────────────────────────────────────────
function openRoleModal(user: ActiveUser) {
  roleModal.value = { visible: true, loading: false, user, newRole: user.role }
}
async function submitRoleChange() {
  const { user, newRole } = roleModal.value
  if (!user || !newRole) return
  roleModal.value.loading = true
  try {
    await rbacApi.updateUserRole(user.id, newRole)
    Message.success(`已将「${user.full_name}」角色更新为 ${getRoleLabel(newRole)}`)
    roleModal.value.visible = false
    await loadUsers()
  } catch {
    Message.error('角色更新失败，请稍后重试')
  } finally {
    roleModal.value.loading = false
  }
}

// ── 重置密码 ───────────────────────────────────────────────
function openPasswordModal(user: ActiveUser) {
  passwordModal.value = { visible: true, loading: false, user, newPassword: '' }
}
async function submitPasswordReset() {
  const { user, newPassword } = passwordModal.value
  if (!user) return
  if (!newPassword || newPassword.length < 6) { Message.warning('密码至少6位'); return }
  passwordModal.value.loading = true
  try {
    await rbacApi.resetUserPassword(user.id, newPassword)
    Message.success(`「${user.full_name}」密码已重置`)
    passwordModal.value.visible = false
  } catch {
    Message.error('密码重置失败，请稍后重试')
  } finally {
    passwordModal.value.loading = false
  }
}

// ── 停用/启用 ──────────────────────────────────────────────
function confirmToggleStatus(user: ActiveUser) {
  const action = user.is_active ? '停用' : '启用'
  Modal.confirm({
    title: `确认${action}账号`,
    content: `确定要${action}「${user.full_name}」的账号吗？`,
    okText: `确认${action}`, cancelText: '取消',
    okButtonProps: { status: user.is_active ? 'warning' : 'normal' },
    async onOk() {
      try {
        await rbacApi.toggleUserStatus(user.id)
        Message.success(`账号已${action}`)
        await loadUsers()
      } catch {
        Message.error(`${action}失败，请稍后重试`)
      }
    },
  })
}

// ── 删除 ───────────────────────────────────────────────────
function confirmDelete(user: ActiveUser) {
  Modal.confirm({
    title: '确认删除人员',
    content: `此操作将永久删除「${user.full_name}」及其所有数据，无法恢复。确认继续？`,
    okText: '永久删除', cancelText: '取消',
    okButtonProps: { status: 'danger' },
    async onOk() {
      try {
        await rbacApi.deleteUser(user.id)
        Message.success(`「${user.full_name}」已删除`)
        await loadUsers()
      } catch {
        Message.error('删除失败，请稍后重试')
      }
    },
  })
}

// ── lifecycle ──────────────────────────────────────────────
onMounted(async () => {
  await permissionStore.fetchAllRoles()
  await loadUsers()
})
</script>

<style scoped>
.settings-page { padding: 0; }

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.header-left { display: flex; align-items: center; gap: 12px; }
.header-actions { display: flex; align-items: center; gap: 8px; }

/* 页头图标标识 */
.page-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #f53f3f 0%, #ff7d00 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(245, 63, 63, 0.35);
}

.page-title-group {
  display: flex;
  flex-direction: column;
  gap: 1px;
}
.page-title { font-size: 18px; font-weight: 700; color: var(--color-text-1); line-height: 1.3; }
.page-subtitle { font-size: 11px; color: var(--color-text-4); letter-spacing: 0.5px; }

/* 角色统计卡片 */
.stat-cards {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.stat-card {
  flex: 1;
  min-width: 120px;
  background: var(--color-bg-2);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 10px 14px;
}
.stat-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.stat-count {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text-1);
  line-height: 1;
}
.stat-bar {
  height: 4px;
  background: var(--color-fill-3);
  border-radius: 2px;
  overflow: hidden;
}
.stat-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.4s ease;
}

/* 工具栏 */
.toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 14px;
  flex-wrap: wrap;
  align-items: center;
}

/* 表格用户单元格 */
.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}
.uname {
  font-weight: 500;
  font-size: 13px;
  color: var(--color-text-1);
  line-height: 1.3;
}
.ulogin {
  font-size: 11px;
  color: var(--color-text-3);
}

/* 弹窗用户横幅 */
.modal-user-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: var(--color-fill-2);
  border-radius: 8px;
}

/* 表格容器 */
.table-wrap {
  background: var(--color-bg-2);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  overflow: hidden;
}

/* 强化表格头部在暗黑主题下的可见性 */
.table-wrap :deep(.arco-table-th) {
  background: var(--color-fill-2) !important;
  font-weight: 600;
  font-size: 12px;
  letter-spacing: 0.3px;
  color: var(--color-text-2);
  border-bottom: 1px solid var(--color-border);
}

.table-wrap :deep(.arco-table-tr:hover .arco-table-td) {
  background: var(--color-fill-1) !important;
}

.table-wrap :deep(.arco-table-stripe .arco-table-tr:nth-child(even) .arco-table-td) {
  background: var(--color-fill-1);
}

.table-wrap :deep(.arco-table-empty) {
  padding: 48px 0;
}

/* 分页器间距 */
.table-wrap :deep(.arco-table-pagination) {
  padding: 12px 16px;
  border-top: 1px solid var(--color-border);
  margin-top: 0;
}
</style>
