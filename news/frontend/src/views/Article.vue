<template>
  <div class="article-page">
    <header class="header">
      <div class="header-content">
        <button class="btn-back" @click="goBack">← 返回</button>
        <h1 class="title">文章详情</h1>
      </div>
    </header>

    <main class="main">
      <div v-if="loading" class="loading">加载中...</div>
      
      <div v-else-if="article" class="article-container">
        <div class="article-split">
          <div class="article-panel">
            <div class="panel-header">
              <div class="panel-title-row">
                <h3>🇬🇧 {{ article.title_en }}</h3>
                <span v-if="article.published_at" class="panel-time">{{ formatTime(article.published_at) }}</span>
              </div>
              <button 
                v-if="article.content_en"
                class="btn-copy"
                @click="copyText(article.content_en, '英文')"
              >
                📋 复制
              </button>
            </div>
            <div class="panel-content" ref="enPanelRef">
              <div v-if="fetching" class="loading-content">
                <div class="spinner"></div>
                <p>正在获取内容...</p>
              </div>
              <p v-else-if="article.content_en" class="article-text">{{ article.content_en }}</p>
              <div v-else class="empty-content">
                <p>暂无英文内容</p>
                <button class="btn-fetch" @click="handleFetch" :disabled="fetching">
                  📥 获取英文内容
                </button>
              </div>
            </div>
          </div>

          <div class="article-panel">
            <div class="panel-header">
              <div class="panel-title-row">
                <h3>🇨🇳 {{ article.title_zh || '未翻译' }}</h3>
                <span v-if="article.translated_at" class="panel-time">{{ formatTime(article.translated_at) }}</span>
              </div>
              <button 
                v-if="article.content_zh"
                class="btn-copy"
                @click="copyText(article.content_zh, '中文')"
              >
                📋 复制
              </button>
              <button 
                v-else-if="article.content_en && !article.content_zh"
                class="btn-translate"
                @click="handleTranslate"
                :disabled="translating"
              >
                <span v-if="translating">
                  <span class="spinner-small"></span> 翻译中...
                </span>
                <span v-else>🌐 翻译全文</span>
              </button>
            </div>
            <div class="panel-content" ref="zhPanelRef">
              <div v-if="translating" class="loading-content">
                <div class="spinner"></div>
                <p>正在翻译...</p>
              </div>
              <p v-else-if="article.content_zh" class="article-text">{{ article.content_zh }}</p>
              <div v-else class="empty-content">
                <p>暂无中文翻译</p>
                <p v-if="article.content_en" class="hint">请点击右侧按钮翻译</p>
                <p v-else class="hint">请先获取英文内容</p>
              </div>
            </div>
          </div>

          <div class="article-panel">
            <div class="panel-header">
              <div class="panel-title-row">
                <h3>✨ AI润色</h3>
                <span v-if="article.polished_at" class="panel-time">{{ formatTime(article.polished_at) }}</span>
              </div>
              <div class="panel-actions">
                <button 
                  v-if="article.content_zh"
                  class="btn-polish"
                  @click="handlePolish"
                  :disabled="polishing"
                >
                  <span v-if="polishing">
                    <span class="spinner-small"></span> 润色中...
                  </span>
                  <span v-else>✨ {{ article.content_polished ? '重新润色' : 'AI润色' }}</span>
                </button>
                <button 
                  v-if="article.content_polished"
                  class="btn-copy"
                  @click="copyText(article.content_polished, '润色后')"
                >
                  📋 复制
                </button>
              </div>
            </div>
            <div class="panel-content" ref="polishedPanelRef">
              <div v-if="polishing" class="loading-content">
                <div class="spinner"></div>
                <p>正在润色...</p>
              </div>
              <p v-else-if="article.content_polished" class="article-text">{{ article.content_polished }}</p>
              <div v-else class="empty-content">
                <p>暂无润色内容</p>
                <p v-if="article.content_zh" class="hint">请点击上方按钮进行AI润色</p>
                <p v-else class="hint">请先翻译文章内容</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api'

const router = useRouter()
const route = useRoute()
const article = ref(null)
const loading = ref(false)
const fetching = ref(false)
const translating = ref(false)
const polishing = ref(false)
const enPanelRef = ref(null)
const zhPanelRef = ref(null)
const polishedPanelRef = ref(null)

let enScrollTimer = null
let zhScrollTimer = null

const loadArticle = async () => {
  loading.value = true
  try {
    const res = await api.getArticle(route.params.id)
    article.value = res.data.data
  } catch (error) {
    console.error('加载失败:', error)
  }
  loading.value = false
}

const handleFetch = async () => {
  fetching.value = true
  try {
    const res = await api.fetchContent(article.value.id)
    article.value = res.data.data
    ElMessage.success('获取成功')
  } catch (error) {
    console.error('获取内容失败:', error)
    ElMessage.error('获取失败')
  }
  fetching.value = false
}

const handleTranslate = async () => {
  translating.value = true
  try {
    const res = await api.translate(article.value.id)
    article.value = res.data.data
    ElMessage.success('翻译成功')
  } catch (error) {
    console.error('翻译失败:', error)
    ElMessage.error('翻译失败')
  }
  translating.value = false
}

const handlePolish = async () => {
  polishing.value = true
  try {
    const res = await api.polish(article.value.id)
    article.value = res.data.data
    ElMessage.success('润色成功')
  } catch (error) {
    console.error('润色失败:', error)
    ElMessage.error('润色失败')
  }
  polishing.value = false
}

const copyText = async (text, lang) => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success(`${lang}内容已复制到剪贴板`)
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败，请手动复制')
  }
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

const syncScroll = (sourcePanel, targetPanel) => {
  if (!sourcePanel || !targetPanel) return
  const scrollPercentage = sourcePanel.scrollTop / (sourcePanel.scrollHeight - sourcePanel.clientHeight)
  targetPanel.scrollTop = scrollPercentage * (targetPanel.scrollHeight - targetPanel.clientHeight)
}

const onEnScroll = () => {
  clearTimeout(enScrollTimer)
  if (zhPanelRef.value) {
    enScrollTimer = setTimeout(() => syncScroll(enPanelRef.value, zhPanelRef.value), 10)
  }
}

const onZhScroll = () => {
  clearTimeout(zhScrollTimer)
  if (enPanelRef.value) {
    zhScrollTimer = setTimeout(() => syncScroll(zhPanelRef.value, enPanelRef.value), 10)
  }
}

const goBack = () => {
  router.push('/')
}

onMounted(() => {
  loadArticle()
})

onUnmounted(() => {
  clearTimeout(enScrollTimer)
  clearTimeout(zhScrollTimer)
})
</script>

<style scoped>
.article-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.header {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  padding: 16px 0;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  align-items: center;
  gap: 20px;
}

.btn-back {
  background: transparent;
  color: #fff;
  border: 1px solid rgba(255,255,255,0.3);
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-back:hover {
  background: rgba(255,255,255,0.1);
}

.title {
  color: #fff;
  font-size: 18px;
}

.main {
  max-width: 1400px;
  margin: 0 auto;
  padding: 30px 20px;
}

.loading {
  text-align: center;
  padding: 60px;
  color: #6b7280;
}

.article-container {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  overflow: hidden;
}

.article-header {
  padding: 24px 30px;
  border-bottom: 1px solid #e5e7eb;
  background: #fafafa;
}

.article-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
  line-height: 1.5;
}

.article-title-zh {
  font-size: 16px;
  color: #4b5563;
  line-height: 1.6;
}

.article-time {
  font-size: 13px;
  color: #6b7280;
  margin-top: 8px;
}

.panel-time {
  font-size: 12px;
  color: #9ca3af;
}

.article-split {
    display: flex;
    min-height: calc(100vh - 280px);
    width: 100%;
  }

.article-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.article-panel:first-child {
  border-right: 1px solid #e5e7eb;
}

.article-panel:nth-child(2) {
  border-right: 1px solid #e5e7eb;
}

.panel-header {
  padding: 16px 24px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  font-size: 15px;
  font-weight: 600;
  color: #374151;
}

.panel-title-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  min-width: 0;
  margin-right: 12px;
}

.panel-title-row h3 {
  word-break: break-word;
}

.panel-actions {
  display: flex;
  gap: 8px;
}

.btn-translate {
  background: #4f46e5;
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-translate:hover:not(:disabled) {
  background: #4338ca;
}

.btn-translate:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-polish {
  background: #f59e0b;
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-polish:hover:not(:disabled) {
  background: #d97706;
}

.btn-polish:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-copy {
  background: #10b981;
  color: #fff;
  border: none;
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.btn-copy:hover {
  background: #059669;
  transform: translateY(-1px);
}

.panel-content {
    flex: 1;
    padding: 24px;
    overflow-y: auto;
    max-height: calc(100vh - 220px);
  }

.article-text {
  font-size: 15px;
  line-height: 1.8;
  color: #374151;
  white-space: pre-wrap;
  word-break: break-word;
}

.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
  color: #9ca3af;
}

.empty-content p {
  margin-bottom: 16px;
}

.hint {
  font-size: 13px;
  color: #d1d5db;
}

.btn-fetch {
  background: #4f46e5;
  color: #fff;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-fetch:hover:not(:disabled) {
  background: #4338ca;
}

.btn-fetch:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 200px;
  color: #6b7280;
}

.loading-content p {
  margin-top: 16px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e5e7eb;
  border-top-color: #4f46e5;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.spinner-small {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .article-split {
    flex-direction: column;
    min-height: auto;
  }
  
  .article-panel:first-child {
    border-right: none;
    border-bottom: 1px solid #e5e7eb;
  }
  
  .panel-content {
    max-height: 300px;
  }
}
</style>
