<template>
  <div class="components-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <a-space direction="vertical" :size="8">
        <a-typography-title :level="2">
          Arco Design 组件库
        </a-typography-title>
        <a-typography-text type="secondary">
          探索和使用 Arco Design 提供的丰富组件
        </a-typography-text>
      </a-space>
      
      <a-input-search
        v-model="searchKeyword"
        placeholder="搜索组件..."
        :style="{ width: '320px' }"
        @search="handleSearch"
        @clear="handleClearSearch"
        allow-clear
      />
    </div>

    <!-- 组件分类 -->
    <a-tabs v-model="activeCategory" class="category-tabs">
      <a-tab-pane key="basic" title="基础组件">
        <component-grid :components="basicComponents" />
      </a-tab-pane>
      
      <a-tab-pane key="layout" title="布局组件">
        <component-grid :components="layoutComponents" />
      </a-tab-pane>
      
      <a-tab-pane key="data" title="数据展示">
        <component-grid :components="dataComponents" />
      </a-tab-pane>
      
      <a-tab-pane key="feedback" title="反馈组件">
        <component-grid :components="feedbackComponents" />
      </a-tab-pane>
      
      <a-tab-pane key="navigation" title="导航组件">
        <component-grid :components="navigationComponents" />
      </a-tab-pane>
      
      <a-tab-pane key="other" title="其他组件">
        <component-grid :components="otherComponents" />
      </a-tab-pane>
    </a-tabs>

    <!-- 组件详情模态框 -->
    <a-modal
      v-model:visible="detailVisible"
      :title="selectedComponent?.name ?? ''"
      width="800px"
      :footer="false"
      @cancel="handleCloseDetail"
    >
      <component-detail
        v-if="selectedComponent"
        :component="selectedComponent"
      />
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
// @ts-ignore
import ComponentGrid from '@/components/ComponentGrid.vue'
// @ts-ignore
import ComponentDetail from '@/components/ComponentDetail.vue'

interface ComponentItem {
  id: string
  name: string
  description: string
  icon: string
  category: string
  tags: string[]
  usage: string
  props?: Array<{
    name: string
    type: string
    default: string
    description: string
  }>
  examples?: Array<{
    title: string
    code: string
  }>
}

// 搜索关键词
const searchKeyword = ref('')

// 激活的分类
const activeCategory = ref('basic')

// 详情模态框可见性
const detailVisible = ref(false)

// 选中的组件
const selectedComponent = ref<ComponentItem | null>(null)

// 基础组件
const basicComponents = ref<ComponentItem[]>([
  {
    id: 'button',
    name: 'Button 按钮',
    description: '按钮用于开始一个即时操作',
    icon: 'icon-command',
    category: 'basic',
    tags: ['交互', '基础'],
    usage: '用于触发操作或提交表单'
  },
  {
    id: 'input',
    name: 'Input 输入框',
    description: '通过鼠标或键盘输入内容',
    icon: 'icon-edit',
    category: 'basic',
    tags: ['表单', '输入'],
    usage: '用于用户输入文本内容'
  },
  {
    id: 'select',
    name: 'Select 选择器',
    description: '下拉选择器',
    icon: 'icon-down',
    category: 'basic',
    tags: ['表单', '选择'],
    usage: '用于从多个选项中选择一个或多个'
  },
  {
    id: 'checkbox',
    name: 'Checkbox 复选框',
    description: '在一组可选项中进行多项选择',
    icon: 'icon-check',
    category: 'basic',
    tags: ['表单', '选择'],
    usage: '用于多选场景'
  },
  {
    id: 'radio',
    name: 'Radio 单选框',
    description: '在一组可选项中进行单项选择',
    icon: 'icon-radio',
    category: 'basic',
    tags: ['表单', '选择'],
    usage: '用于单选场景'
  },
  {
    id: 'switch',
    name: 'Switch 开关',
    description: '开关选择器',
    icon: 'icon-swap',
    category: 'basic',
    tags: ['表单', '切换'],
    usage: '用于表示两种状态之间的切换'
  }
])

// 布局组件
const layoutComponents = ref<ComponentItem[]>([
  {
    id: 'layout',
    name: 'Layout 布局',
    description: '协助进行页面级整体布局',
    icon: 'icon-layout',
    category: 'layout',
    tags: ['布局', '容器'],
    usage: '用于页面整体布局'
  },
  {
    id: 'grid',
    name: 'Grid 栅格',
    description: '24 栅格系统',
    icon: 'icon-grid',
    category: 'layout',
    tags: ['布局', '响应式'],
    usage: '用于创建响应式布局'
  },
  {
    id: 'space',
    name: 'Space 间距',
    description: '设置组件之间的间距',
    icon: 'icon-space',
    category: 'layout',
    tags: ['布局', '间距'],
    usage: '用于控制组件间距'
  },
  {
    id: 'divider',
    name: 'Divider 分割线',
    description: '区隔内容的分割线',
    icon: 'icon-minus',
    category: 'layout',
    tags: ['布局', '分割'],
    usage: '用于分隔内容'
  }
])

// 数据展示组件
const dataComponents = ref<ComponentItem[]>([
  {
    id: 'table',
    name: 'Table 表格',
    description: '展示行列数据',
    icon: 'icon-table',
    category: 'data',
    tags: ['数据', '表格'],
    usage: '用于展示结构化数据'
  },
  {
    id: 'card',
    name: 'Card 卡片',
    description: '通用卡片容器',
    icon: 'icon-idcard',
    category: 'data',
    tags: ['容器', '卡片'],
    usage: '用于信息聚合展示'
  },
  {
    id: 'list',
    name: 'List 列表',
    description: '通用列表',
    icon: 'icon-list',
    category: 'data',
    tags: ['数据', '列表'],
    usage: '用于展示列表数据'
  },
  {
    id: 'tree',
    name: 'Tree 树形控件',
    description: '文件夹、组织架构、生物分类等',
    icon: 'icon-branch',
    category: 'data',
    tags: ['数据', '树形'],
    usage: '用于展示层级数据'
  }
])

// 反馈组件
const feedbackComponents = ref<ComponentItem[]>([
  {
    id: 'modal',
    name: 'Modal 模态框',
    description: '模态对话框',
    icon: 'icon-exclamation-circle',
    category: 'feedback',
    tags: ['弹窗', '对话框'],
    usage: '用于需要用户交互的弹窗'
  },
  {
    id: 'message',
    name: 'Message 全局提示',
    description: '全局展示操作反馈信息',
    icon: 'icon-message',
    category: 'feedback',
    tags: ['提示', '反馈'],
    usage: '用于操作结果反馈'
  },
  {
    id: 'notification',
    name: 'Notification 通知提醒框',
    description: '全局通知提醒',
    icon: 'icon-notification',
    category: 'feedback',
    tags: ['通知', '提醒'],
    usage: '用于系统通知'
  },
  {
    id: 'tooltip',
    name: 'Tooltip 文字提示',
    description: '简单的文字提示气泡框',
    icon: 'icon-question-circle',
    category: 'feedback',
    tags: ['提示', '气泡'],
    usage: '用于解释说明'
  }
])

// 导航组件
const navigationComponents = ref<ComponentItem[]>([
  {
    id: 'menu',
    name: 'Menu 导航菜单',
    description: '为页面和功能提供导航的菜单列表',
    icon: 'icon-menu',
    category: 'navigation',
    tags: ['导航', '菜单'],
    usage: '用于网站导航'
  },
  {
    id: 'tabs',
    name: 'Tabs 标签页',
    description: '选项卡切换组件',
    icon: 'icon-tag',
    category: 'navigation',
    tags: ['导航', '标签'],
    usage: '用于内容分类展示'
  },
  {
    id: 'breadcrumb',
    name: 'Breadcrumb 面包屑',
    description: '显示当前页面在系统层级结构中的位置',
    icon: 'icon-right',
    category: 'navigation',
    tags: ['导航', '路径'],
    usage: '用于显示当前位置'
  },
  {
    id: 'pagination',
    name: 'Pagination 分页',
    description: '采用分页的形式分隔长列表',
    icon: 'icon-double-right',
    category: 'navigation',
    tags: ['导航', '分页'],
    usage: '用于数据分页'
  }
])

// 其他组件
const otherComponents = ref<ComponentItem[]>([
  {
    id: 'avatar',
    name: 'Avatar 头像',
    description: '用图标、图片或者字符展示用户或事物',
    icon: 'icon-user',
    category: 'other',
    tags: ['用户', '头像'],
    usage: '用于展示用户头像'
  },
  {
    id: 'badge',
    name: 'Badge 徽标数',
    description: '图标右上角的圆形徽标数字',
    icon: 'icon-dot-chart',
    category: 'other',
    tags: ['标记', '徽标'],
    usage: '用于消息数量标记'
  },
  {
    id: 'progress',
    name: 'Progress 进度条',
    description: '展示操作的当前进度',
    icon: 'icon-loading',
    category: 'other',
    tags: ['进度', '状态'],
    usage: '用于展示任务进度'
  },
  {
    id: 'skeleton',
    name: 'Skeleton 骨架屏',
    description: '在需要等待加载内容的位置提供一个占位图形组合',
    icon: 'icon-code',
    category: 'other',
    tags: ['加载', '占位'],
    usage: '用于加载状态占位'
  }
])

// 处理搜索
const handleSearch = (value: string) => {
  console.log('搜索关键词:', value)
  // 这里可以添加搜索逻辑
}

// 清除搜索
const handleClearSearch = () => {
  searchKeyword.value = ''
}

// 查看组件详情
const viewComponentDetail = (component: ComponentItem) => {
  selectedComponent.value = component
  detailVisible.value = true
}

// 关闭详情
const handleCloseDetail = () => {
  detailVisible.value = false
  selectedComponent.value = null
}

// 暴露方法给子组件
defineExpose({
  viewComponentDetail
})
</script>

<style scoped>
.components-page {
  padding: 24px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.category-tabs {
  margin-bottom: 24px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .page-header .arco-input-search {
    width: 100% !important;
  }
}
</style>