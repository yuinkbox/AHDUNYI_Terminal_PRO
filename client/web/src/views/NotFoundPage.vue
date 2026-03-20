<template>
  <div class="not-found-page">
    <a-result
      status="404"
      title="404"
      sub-title="抱歉，您访问的页面不存在"
    >
      <template #extra>
        <a-space :size="16">
          <a-button type="primary" @click="goHome">
            <template #icon>
              <icon-home />
            </template>
            返回首页
          </a-button>
          <a-button type="outline" @click="goBack">
            <template #icon>
              <icon-arrow-left />
            </template>
            返回上一页
          </a-button>
        </a-space>
      </template>
    </a-result>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

// 返回首页
const goHome = () => {
  router.push('/dashboard')
}

// 返回上一页
const goBack = () => {
  router.back()
}
</script>

<style scoped>
.not-found-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 24px;
  background: #f5f5f5;
}
</style>