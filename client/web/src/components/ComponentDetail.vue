<template>
  <div class="component-detail" v-if="props.component">
    <!-- 组件基本信息 -->
    <div class="component-header">
      <a-space direction="vertical" :size="8">
        <div class="component-title">
          <component :is="props.component.icon" size="24" />
          <a-typography-title :level="3" class="title-text">
            {{ props.component.name }}
          </a-typography-title>
        </div>
        <a-typography-text type="secondary">
          {{ props.component.description }}
        </a-typography-text>
      </a-space>
      
      <div class="component-actions">
        <a-space :size="8">
          <a-button type="primary" @click="handleUse">
            <template #icon>
              <icon-code />
            </template>
            使用组件
          </a-button>
          <a-button type="outline" @click="handleCopyAll">
            <template #icon>
              <icon-copy />
            </template>
            复制全部
          </a-button>
        </a-space>
      </div>
    </div>

    <!-- 标签 -->
    <div class="component-tags">
      <a-space :size="8" wrap>
        <a-tag
          v-for="tag in props.component.tags"
          :key="tag"
          color="blue"
        >
          {{ tag }}
        </a-tag>
      </a-space>
    </div>

    <!-- 使用说明 -->
    <div class="section">
      <a-typography-title :level="4" class="section-title">
        使用说明
      </a-typography-title>
      <div class="usage-content">
        {{ props.component.usage }}
      </div>
    </div>

    <!-- 属性表格 -->
    <div class="section" v-if="props.component.props">
      <a-typography-title :level="4" class="section-title">
        属性 (Props)
      </a-typography-title>
      <a-table
        :columns="propColumns"
        :data="props.component.props"
        :pagination="false"
        :bordered="false"
      >
        <template #type="{ record }">
          <code>{{ record.type }}</code>
        </template>
        
        <template #default="{ record }">
          <code v-if="record.default">{{ record.default }}</code>
          <a-typography-text v-else type="secondary">
            -
          </a-typography-text>
        </template>
      </a-table>
    </div>

    <!-- 代码示例 -->
    <div class="section" v-if="props.component.examples">
      <a-typography-title :level="4" class="section-title">
        代码示例
      </a-typography-title>
      
      <a-tabs v-model="activeExample" class="example-tabs">
        <a-tab-pane
          v-for="(example, index) in props.component.examples"
          :key="index"
          :title="example.title"
        >
          <div class="example-content">
            <a-typography-paragraph>
              {{ example.description || '示例代码' }}
            </a-typography-paragraph>
            
            <div class="code-block">
              <div class="code-header">
                <span>Vue + TypeScript</span>
                <a-button
                  type="text"
                  size="small"
                  @click="copyExampleCode(example.code)"
                >
                  <template #icon>
                    <icon-copy />
                  </template>
                  复制
                </a-button>
              </div>
              <pre><code>{{ example.code }}</code></pre>
            </div>
          </div>
        </a-tab-pane>
      </a-tabs>
    </div>

    <!-- 默认示例 -->
    <div class="section" v-else>
      <a-typography-title :level="4" class="section-title">
        基础示例
      </a-typography-title>
      
      <div class="example-content">
        <div class="code-block">
          <div class="code-header">
            <span>基础用法</span>
            <a-button
              type="text"
              size="small"
              @click="copyBasicCode"
            >
              <template #icon>
                <icon-copy />
              </template>
              复制
            </a-button>
          </div>
          <pre><code>{{ basicExampleCode }}</code></pre>
        </div>
      </div>
    </div>

    <!-- 注意事项 -->
    <div class="section">
      <a-typography-title :level="4" class="section-title">
        注意事项
      </a-typography-title>
      <ul class="notes-list">
        <li>确保已安装并正确引入 Arco Design Vue 组件库</li>
        <li>根据实际需求调整组件的属性和样式</li>
        <li>在生产环境中注意性能优化和代码分割</li>
        <li>遵循 Vue 3 的组合式 API 最佳实践</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface ComponentProp {
  name: string
  type: string
  default: string
  description: string
}

interface ComponentExample {
  title: string
  description?: string
  code: string
}

interface ComponentItem {
  id: string
  name: string
  description: string
  icon: string
  category: string
  tags: string[]
  usage: string
  props?: ComponentProp[]
  examples?: ComponentExample[]
}

interface Props {
  component: ComponentItem
}

const props = defineProps<Props>()

// 属性表格列定义

// 激活的示例


// 基础示例代码
const basicExampleCode = `<template>
  <!-- ${props.component?.name} 基础用法 -->
  <div class="component-container">
    <!-- 在这里使用 ${props.component?.name} 组件 -->
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// ${props.component?.name} 组件基础示例
const value = ref('')

// 组件事件处理
const handleChange = (newValue: any) => {
  console.log('值变化:', newValue)
}
</script>

<style scoped>
.component-container {
  /* 组件容器样式 */
}
</style>`

// 使用组件
const handleUse = () => {
  Message.success(`开始使用 ${props.component.name} 组件`)
  // 这里可以跳转到使用页面或打开代码编辑器
}

// 复制全部代码
const handleCopyAll = async () => {
  const allCode = generateAllCode()
  
  try {
    await navigator.clipboard.writeText(allCode)
    Message.success('全部代码已复制到剪贴板')
  } catch (err) {
    console.error('复制失败:', err)
    Message.error('复制失败，请手动复制')
  }
}

// 复制示例代码
const copyExampleCode = async (code: string) => {
  try {
    await navigator.clipboard.writeText(code)
    Message.success('示例代码已复制到剪贴板')
  } catch (err) {
    console.error('复制失败:', err)
    Message.error('复制失败，请手动复制')
  }
}

// 复制基础代码
const copyBasicCode = async () => {
  try {
    await navigator.clipboard.writeText(basicExampleCode)
    Message.success('基础代码已复制到剪贴板')
  } catch (err) {
    console.error('复制失败:', err)
    Message.error('复制失败，请手动复制')
  }
}

// 生成全部代码
const generateAllCode = (): string => {
  let code = `# ${props.component.name}\n\n`
  code += `${props.component.description}\n\n`
  code += `## 使用说明\n\n`
  code += `${props.component.usage}\n\n`
  
  if (props.component.props && props.component.props.length > 0) {
    code += `## 属性\n\n`
    code += `| 属性名 | 类型 | 默认值 | 说明 |\n`
    code += `|--------|------|--------|------|\n`
    
    props.component.props.forEach(prop => {
      code += `| ${prop.name} | \`${prop.type}\` | ${prop.default || '-'} | ${prop.description} |\n`
    })
    
    code += `\n`
  }
  
  code += `## 示例代码\n\n`
  code += `\`\`\`vue\n`
  code += basicExampleCode
  code += `\n\`\`\`\n`
  
  return code
}
</script>

<style scoped>
.component-detail {
  padding: 4px;
}

.component-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border-2);
}

.component-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-text {
  margin: 0;
}

.component-actions {
  flex-shrink: 0;
}

.component-tags {
  margin-bottom: 24px;
}

.section {
  margin-bottom: 32px;
}

.section-title {
  margin-bottom: 16px;
  color: var(--color-text-1);
}

.usage-content {
  padding: 16px;
  background: var(--color-fill-1);
  border-radius: var(--border-radius-medium);
  color: var(--color-text-2);
  line-height: 1.6;
}

.example-tabs {
  margin-top: 16px;
}

.example-content {
  padding: 16px 0;
}

.code-block {
  background: var(--color-fill-1);
  border-radius: var(--border-radius-medium);
  overflow: hidden;
  margin-top: 16px;
}

.code-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--color-fill-2);
  border-bottom: 1px solid var(--color-border-2);
  font-size: 13px;
  color: var(--color-text-2);
}

.code-header .arco-btn {
  padding: 0;
}

.code-block pre {
  margin: 0;
  padding: 16px;
  overflow-x: auto;
}

.code-block code {
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 13px;
  line-height: 1.5;
  color: var(--color-text-1);
}

.notes-list {
  padding-left: 20px;
  color: var(--color-text-2);
  line-height: 1.6;
}

.notes-list li {
  margin-bottom: 8px;
}

@media (max-width: 768px) {
  .component-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .component-actions {
    width: 100%;
  }
  
  .component-actions .arco-space {
    width: 100%;
  }
  
  .component-actions .arco-btn {
    flex: 1;
  }
}
</style>