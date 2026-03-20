<template>
  <div class="home-page">
    <!-- 导航栏 -->
    <a-layout-header class="header">
      <div class="header-content">
        <div class="logo">
          <a-typography-title :level="4" class="logo-text">
            🚀 Vue 3 + Arco Design
          </a-typography-title>
        </div>
        <div class="nav">
          <a-space :size="24">
            <a-link href="/" :hoverable="false">首页</a-link>
            <a-link href="/dashboard" :hoverable="false">仪表板</a-link>
            <a-link href="/components" :hoverable="false">组件库</a-link>
            <a-link href="https://arco.design" target="_blank" :hoverable="false">
              文档
              <icon-external-link />
            </a-link>
          </a-space>
        </div>
      </div>
    </a-layout-header>

    <!-- 主内容区 -->
    <a-layout-content class="content">
      <div class="hero-section">
        <a-space direction="vertical" :size="32" align="center">
          <a-typography-title :level="1" class="hero-title">
            商业级 Web 前端应用
          </a-typography-title>
          <a-typography-paragraph class="hero-description">
            基于 Vue 3 + Arco Design 构建的企业级前端解决方案
          </a-typography-paragraph>
          
          <a-space :size="16">
            <a-button type="primary" size="large" @click="goToDashboard">
              <template #icon>
                <icon-rocket />
              </template>
              开始使用
            </a-button>
            <a-button size="large" @click="viewComponents">
              <template #icon>
                <icon-code />
              </template>
              查看组件
            </a-button>
          </a-space>
        </a-space>
      </div>

      <!-- 特性展示 -->
      <div class="features-section">
        <a-typography-title :level="2" class="section-title">
          核心特性
        </a-typography-title>
        
        <a-row :gutter="24" class="features-grid">
          <a-col :span="8">
            <a-card class="feature-card" hoverable>
              <template #cover>
                <div class="feature-icon">
                  <icon-code-block size="48" />
                </div>
              </template>
              <a-card-meta title="TypeScript 支持">
                <template #description>
                  完整的 TypeScript 类型支持，提供更好的开发体验和代码质量
                </template>
              </a-card-meta>
            </a-card>
          </a-col>
          
          <a-col :span="8">
            <a-card class="feature-card" hoverable>
              <template #cover>
                <div class="feature-icon">
                  <icon-component size="48" />
                </div>
              </template>
              <a-card-meta title="Arco Design 组件库">
                <template #description>
                  字节跳动出品的企业级 UI 组件库，设计精美，功能丰富
                </template>
              </a-card-meta>
            </a-card>
          </a-col>
          
          <a-col :span="8">
            <a-card class="feature-card" hoverable>
              <template #cover>
                <div class="feature-icon">
                  <icon-bolt size="48" />
                </div>
              </template>
              <a-card-meta title="Vite 构建工具">
                <template #description>
                  极速的开发服务器和构建工具，提供优秀的开发体验
                </template>
              </a-card-meta>
            </a-card>
          </a-col>
        </a-row>
      </div>

      <!-- 技术栈展示 -->
      <div class="tech-stack-section">
        <a-typography-title :level="2" class="section-title">
          技术栈
        </a-typography-title>
        
        <a-space :size="32" wrap class="tech-stack">
          <a-tag color="blue" size="large">Vue 3</a-tag>
          <a-tag color="green" size="large">TypeScript</a-tag>
          <a-tag color="orange" size="large">Arco Design</a-tag>
          <a-tag color="purple" size="large">Pinia</a-tag>
          <a-tag color="red" size="large">Vue Router</a-tag>
          <a-tag color="cyan" size="large">Vite</a-tag>
          <a-tag color="magenta" size="large">Axios</a-tag>
          <a-tag color="gold" size="large">VueUse</a-tag>
        </a-space>
      </div>
    </a-layout-content>

    <!-- 页脚 -->
    <a-layout-footer class="footer">
      <div class="footer-content">
        <a-typography-paragraph class="copyright">
          © 2024 商业级 Web 前端应用. 基于 Vue 3 + Arco Design 构建.
        </a-typography-paragraph>
        <a-space :size="16">
          <a-link href="https://github.com" target="_blank">
            <icon-github />
            GitHub
          </a-link>
          <a-link href="https://arco.design" target="_blank">
            <icon-link />
            Arco Design
          </a-link>
          <a-link href="https://vuejs.org" target="_blank">
            <icon-link />
            Vue.js
          </a-link>
        </a-space>
      </div>
    </a-layout-footer>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goToDashboard = () => {
  router.push('/dashboard')
}

const viewComponents = () => {
  router.push('/components')
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: var(--color-bg-2);
  border-bottom: 1px solid var(--color-border-2);
  padding: 0 24px;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
}

.logo-text {
  margin: 0;
  color: var(--primary-6);
}

.content {
  flex: 1;
  padding: 48px 24px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.hero-section {
  text-align: center;
  padding: 80px 0;
}

.hero-title {
  margin: 0;
  background: linear-gradient(135deg, var(--primary-6), var(--primary-7));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-description {
  font-size: 18px;
  color: var(--color-text-2);
  max-width: 600px;
  margin: 0 auto;
}

.features-section {
  padding: 80px 0;
}

.section-title {
  text-align: center;
  margin-bottom: 48px;
  color: var(--color-text-1);
}

.features-grid {
  margin-top: 32px;
}

.feature-card {
  height: 100%;
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
}

.feature-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 0;
  color: var(--primary-6);
}

.tech-stack-section {
  padding: 80px 0;
  text-align: center;
}

.tech-stack {
  justify-content: center;
  margin-top: 32px;
}

.footer {
  background: var(--color-bg-2);
  border-top: 1px solid var(--color-border-2);
  padding: 24px;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.copyright {
  margin: 0;
  color: var(--color-text-3);
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    height: auto;
    padding: 16px 0;
  }
  
  .nav {
    margin-top: 16px;
  }
  
  .features-grid .arco-col {
    margin-bottom: 24px;
  }
  
  .footer-content {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
}
</style>