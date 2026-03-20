import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useLoadingStore = defineStore('loading', () => {
  // 全局加载状态
  const globalLoading = ref(false)
  
  // 页面级加载状态
  const pageLoading = ref(false)
  
  // 按钮级加载状态
  const buttonLoading = ref<Record<string, boolean>>({})
  
  // 设置全局加载状态
  const setGlobalLoading = (loading: boolean) => {
    globalLoading.value = loading
  }
  
  // 设置页面加载状态
  const setPageLoading = (loading: boolean) => {
    pageLoading.value = loading
  }
  
  // 设置按钮加载状态
  const setButtonLoading = (key: string, loading: boolean) => {
    buttonLoading.value[key] = loading
  }
  
  // 获取按钮加载状态
  const getButtonLoading = (key: string) => {
    return buttonLoading.value[key] || false
  }
  
  // 重置所有加载状态
  const resetAllLoading = () => {
    globalLoading.value = false
    pageLoading.value = false
    buttonLoading.value = {}
  }
  
  return {
    globalLoading,
    pageLoading,
    buttonLoading,
    setGlobalLoading,
    setPageLoading,
    setButtonLoading,
    getButtonLoading,
    resetAllLoading
  }
})