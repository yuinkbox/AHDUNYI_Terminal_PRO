<template>
  <a-row :gutter="[16, 16]" class="component-grid">
    <a-col
      v-for="component in props.components"
      :key="component.id"
      :xs="24"
      :sm="12"
      :md="8"
      :lg="6"
      :xl="6"
    >
      <a-card
        class="component-card"
        hoverable
        @click="handleClick(component)"
      >
        <template #cover>
          <div class="component-icon">
            <component :is="component.icon" size="32" />
          </div>
        </template>

        <a-card-meta :title="component.name">
          <template #description>
            <div class="component-description">
              {{ component.description }}
            </div>
            <div class="component-tags">
              <a-space :size="4" wrap>
                <a-tag
                  v-for="tag in component.tags"
                  :key="tag"
                  size="small"
                  color="blue"
                >
                  {{ tag }}
                </a-tag>
              </a-space>
            </div>
            <div class="component-usage">
              <a-typography-text type="secondary">
                {{ component.usage }}
              </a-typography-text>
            </div>
          </template>
        </a-card-meta>

        <template #actions>
          <a-space :size="8">
            <a-button type="text" size="small" @click.stop="handlePreview(component)">
              <template #icon><icon-eye /></template>
              预览
            </a-button>
            <a-button type="text" size="small" @click.stop="handleCopyCode(component)">
              <template #icon><icon-copy /></template>
              复制
            </a-button>
          </a-space>
        </template>
      </a-card>
    </a-col>
  </a-row>
</template>

<script setup lang="ts">
import { Message } from '@arco-design/web-vue'

interface ComponentItem {
  id: string
  name: string
  description: string
  icon: string
  category: string
  tags: string[]
  usage: string
}

interface Props {
  components: ComponentItem[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  viewDetail: [component: ComponentItem]
}>()

const handleClick = (component: ComponentItem): void => {
  emit('viewDetail', component)
}

const handlePreview = (component: ComponentItem): void => {
  Message.info('预览组件: ' + component.name)
}

const handleCopyCode = async (component: ComponentItem): Promise<void> => {
  const code = generateComponentCode(component)
  try {
    await navigator.clipboard.writeText(code)
    Message.success('代码已复制到剪贴板')
  } catch (err) {
    console.error('复制失败:', err)
    Message.error('复制失败，请手动复制')
  }
}

const COMPONENT_TEMPLATES: Record<string, string> = {
  button: [
    '<template>',
    '  <a-space>',
    '    <a-button type="primary">主要按钮</a-button>',
    '    <a-button type="outline">轮廓按钮</a-button>',
    '    <a-button type="text">文字按钮</a-button>',
    '  </a-space>',
    '</template>',
  ].join('\n'),
  input: [
    '<template>',
    '  <a-space direction="vertical" :size="16">',
    '    <a-input placeholder="请输入内容" />',
    '    <a-input placeholder="带前缀" add-before="https://"></a-input>',
    '    <a-textarea placeholder="多行文本" />',
    '  </a-space>',
    '</template>',
  ].join('\n'),
  select: [
    '<template>',
    '  <a-select placeholder="请选择" style="width: 200px">',
    '    <a-option value="option1">选项一</a-option>',
    '    <a-option value="option2">选项二</a-option>',
    '    <a-option value="option3">选项三</a-option>',
    '  </a-select>',
    '</template>',
  ].join('\n'),
  card: [
    '<template>',
    '  <a-card title="卡片标题" :style="{ width: \'360px\' }">',
    '    <p>卡片内容</p>',
    '  </a-card>',
    '</template>',
  ].join('\n'),
}

const generateComponentCode = (component: ComponentItem): string => {
  return COMPONENT_TEMPLATES[component.id] ?? ('<!-- ' + component.name + ' 组件 -->\n<template>\n  <div></div>\n</template>')
}
</script>

<style scoped>
.component-grid {
  margin-bottom: 24px;
}

.component-card {
  height: 100%;
  cursor: pointer;
  transition: all 0.3s ease;
}

.component-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-3);
}

.component-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px 0;
  color: var(--primary-6);
  background: linear-gradient(135deg, var(--color-fill-1), var(--color-fill-2));
}

.component-description {
  margin-bottom: 8px;
  color: var(--color-text-2);
  font-size: 13px;
  line-height: 1.5;
}

.component-tags {
  margin-bottom: 8px;
}

.component-usage {
  font-size: 12px;
  color: var(--color-text-3);
}

:deep(.arco-card-actions) {
  border-top: 1px solid var(--color-border-2);
  padding: 12px 16px;
}

:deep(.arco-card-actions .arco-btn) {
  padding: 0 8px;
}
</style>
