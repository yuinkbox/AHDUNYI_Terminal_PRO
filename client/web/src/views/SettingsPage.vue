<template>
  <div class="settings-page">
    <!-- 页头 -->
    <div class="page-header">
      <div class="header-left">
        <icon-settings :size="24" />
        <span class="page-title">系统管理</span>
      </div>
      <a-button type="primary" @click="showCreateModal"
        v-if="permissionStore.can('action:update_role')" >
        <template #icon><icon-plus /></template>
        新增用户
      </a-button>
    </div>

    <!-- 工具栏 -->
    <div class="toolbar">
      <a-input-search
        v-model="searchText"
        placeholder="搜索用户名 / 姓名"
        style="width: 260px"
        allow-clear
        @search="loadUsers"
      />
      <a-select
        v-model="filterRole"
        placeholder="角色筛选"
        style="width: 160px"
        allow-clear
        @change="loadUsers"
      >
        <a-option value="">全部角色</a-option>
        <a-option v-for="r in permissionStore.allRoles" :key="r.value" :value="r.value">
          {{ r.label }}
        </a-option>
      </a-select>
      <a-button @click="loadUsers">
        <template #icon><icon-refresh /></template>
        刷新
      </a-button>
    </div>

    <!-- 用户表格 -->
    <a-table
      :data="filteredUsers"
      :loading="loading"
      :pagination="{ pageSize: 15, showTotal: true }"
      row-key="id"
      stripe
    >
      <a-table-column title="ID" data-index="id" :width="70" />
      <a-table-column title="用户名" data-index="username" />
      <a-table-column title="姓名" data-index="full_name" />
      <a-table-column title="角色">
        <template #cell="{ record }">
          <a-tag :color="getRoleColor(record.role)">
            {{ getRoleLabel(record.role) }}
          </a-tag>
        </template>
      </a-table-column>
      <a-table-column title="状态">
        <template #cell="{ record }">
          <a-badge
            :status="record.is_active ? 'processing' : 'default'"
            :text="record.is_active ? '在职' : '停用'"
          />
        </template>
      </a-table-column>
      <a-table-column title="创建时间">
        <template #cell="{ record }">
          {{ formatDate(record.created_at) }}
        </template>
      </a-table-column>
      <a-table-column title="操作" :width="140"
        v-if="permissionStore.can('action:update_role')" >
        <template #cell="{ record }">
          <a-space>
            <a-button type="text" size="small" @click="openEditRole(record)">
              <template #icon><icon-edit /></template>
              改角色
            </a-button>
          </a-space>
        </template>
      </a-table-column>
    </a-table>

    <!-- 修改角色弹窗 -->
    <a-modal
      v-model:visible="editRoleModal.visible"
      title="修改用户角色"
      @ok="submitRoleChange"
      @cancel="editRoleModal.visible = false"
      :ok-loading="editRoleModal.loading"
    >
      <div class="modal-body">
        <div class="modal-user-info">
          <icon-user />
          <span>{{ editRoleModal.user?.full_name }} ({{ editRoleModal.user?.username }})</span>
        </div>
        <a-form layout="vertical" style="margin-top:16px">
          <a-form-item label="当前角色">
            <a-tag :color="getRoleColor(editRoleModal.user?.role || '')">
              {{ getRoleLabel(editRoleModal.user?.role || '') }}
            </a-tag>
          </a-form-item>
          <a-form-item label="新角色" required>
            <a-select v-model="editRoleModal.newRole" placeholder="选择新角色" style="width:100%">
              <a-option
                v-for="r in permissionStore.allRoles"
                :key="r.value"
                :value="r.value"
              >
                <a-tag :color="r.color" size="small">{{ r.label }}</a-tag>
              </a-option>
            </a-select>
          </a-form-item>
        </a-form>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import { rbacApi, type ActiveUser } from '@/api/rbac'
import { usePermissionStore } from '@/stores/permission'

const permissionStore = usePermissionStore()

// ---- state ---------------------------------------------------------------
const users     = ref<ActiveUser[]>([])
const loading   = ref(false)
const searchText = ref('')
const filterRole = ref('')

const editRoleModal = ref<{
  visible: boolean
  loading: boolean
  user: ActiveUser | null
  newRole: string
}>({ visible: false, loading: false, user: null, newRole: '' })

// ---- computed ------------------------------------------------------------
const filteredUsers = computed(() => {
  const q = searchText.value.trim().toLowerCase()
  if (!q) return users.value
  return users.value.filter(
    u => u.username.toLowerCase().includes(q) || u.full_name.toLowerCase().includes(q),
  )
})

// ---- helpers -------------------------------------------------------------
function getRoleLabel(role: string): string {
  return permissionStore.allRoles.find(r => r.value === role)?.label ?? role
}

function getRoleColor(role: string): string {
  return permissionStore.allRoles.find(r => r.value === role)?.color ?? 'gray'
}

function formatDate(iso: string): string {
  return iso ? new Date(iso).toLocaleDateString('zh-CN') : '-'
}

// ---- data ----------------------------------------------------------------
async function loadUsers() {
  loading.value = true
  try {
    const res = await rbacApi.getActiveUsers(filterRole.value || undefined)
    users.value = res.users
  } catch {
    Message.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

function showCreateModal() {
  Message.info('新增用户功能开发中')
}

function openEditRole(user: ActiveUser) {
  editRoleModal.value = {
    visible: true,
    loading: false,
    user,
    newRole: user.role,
  }
}

async function submitRoleChange() {
  const { user, newRole } = editRoleModal.value
  if (!user || !newRole) return
  editRoleModal.value.loading = true
  try {
    await rbacApi.updateUserRole(user.id, newRole)
    Message.success(`已将 ${user.full_name} 的角色更新为 ${getRoleLabel(newRole)}`)
    editRoleModal.value.visible = false
    await loadUsers()
  } catch {
    Message.error('角色更新失败，请稍后重试')
  } finally {
    editRoleModal.value.loading = false
  }
}

// ---- lifecycle -----------------------------------------------------------
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
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text-1);
}

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.modal-user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: var(--color-bg-3);
  border-radius: 6px;
  font-weight: 500;
}
</style>
