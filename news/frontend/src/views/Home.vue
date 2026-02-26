<template>
  <div class="home">
    <header class="header">
      <div class="header-content">
        <h1 class="logo">📰 BBC新闻翻译系统</h1>
        <div class="header-actions">
          <button class="btn-primary" @click="handleCrawl" :disabled="loading">
            <span v-if="loading">加载中...</span>
            <span v-else>🔄 获取最新新闻</span>
          </button>
        </div>
      </div>
    </header>

    <main class="main">
      <div class="search-bar">
        <input
          type="text"
          v-model="keyword"
          placeholder="搜索新闻标题..."
          class="search-input"
          @keyup.enter="handleSearch"
        />
        <button class="btn-search" @click="handleSearch">搜索</button>
        <el-select v-model="statusFilter" @change="handleStatusFilter" placeholder="全部状态" class="status-filter">
          <el-option label="全部状态" value="" />
          <el-option label="已爬取" value="crawled" />
          <el-option label="已翻译" value="translated" />
          <el-option label="已润色" value="polished" />
        </el-select>
      </div>

      <div class="news-list">
        <div v-if="loading" class="loading">加载中...</div>
        
        <div v-else-if="articles.length === 0" class="empty">
          暂无新闻，请点击"获取最新新闻"
        </div>
        
        <div v-else class="news-items">
          <div v-for="article in articles" :key="article.id" class="news-item">
            <div class="news-content" @click="goToArticle(article.id)">
              <h3 class="news-title">{{ article.title_en }}</h3>
              <p v-if="article.title_zh" class="news-title-zh">{{ article.title_zh }}</p>
              <div class="news-meta">
                <span class="status" :class="article.status">{{ getStatusText(article.status) }}</span>
                <span class="date">{{ formatDate(article.crawled_at) }}</span>
              </div>
            </div>
            <div class="news-actions">
              <button 
                v-if="!article.content_en || !article.content_zh"
                class="btn-action btn-fetch-translate" 
                @click.stop="handleFetchAndTranslate(article)"
                :disabled="translatingId === article.id"
              >
                <span v-if="translatingId === article.id">处理中...</span>
                <span v-else>{{ article.content_en ? '📝 翻译文章内容' : '📥 获取原文并翻译' }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="total > pageSize" class="pagination">
        <button 
          class="page-btn" 
          :disabled="currentPage === 1"
          @click="handlePageChange(currentPage - 1)"
        >
          上一页
        </button>
        <span class="page-info">{{ currentPage }} / {{ Math.ceil(total / pageSize) }}</span>
        <button 
          class="page-btn" 
          :disabled="currentPage >= Math.ceil(total / pageSize)"
          @click="handlePageChange(currentPage + 1)"
        >
          下一页
        </button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const articles = ref([])
const keyword = ref('')
const statusFilter = ref('')
const loading = ref(false)
const translatingId = ref(null)
const currentPage = ref(1)
const pageSize = 10
const total = ref(0)

const loadArticles = async () => {
  loading.value = true
  try {
    const res = await api.getArticles({ 
      keyword: keyword.value,
      status: statusFilter.value,
      page: currentPage.value,
      page_size: pageSize
    })
    articles.value = res.data.data.list
    total.value = res.data.data.total
  } catch (error) {
    console.error('加载失败:', error)
  }
  loading.value = false
}

const handleSearch = () => {
  currentPage.value = 1
  loadArticles()
}

const handleStatusFilter = () => {
  currentPage.value = 1
  loadArticles()
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadArticles()
}

const handleCrawl = async () => {
  loading.value = true
  try {
    await api.crawlNews()
    await loadArticles()
  } catch (error) {
    console.error('爬取失败:', error)
  }
  loading.value = false
}

const handleFetchAndTranslate = async (article) => {
  translatingId.value = article.id
  try {
    await api.fetchAndTranslate(article.id)
    await loadArticles()
  } catch (error) {
    console.error('获取并翻译失败:', error)
  }
  translatingId.value = null
}

const goToArticle = (id) => {
  router.push(`/article/${id}`)
}

const getStatusText = (status) => {
  const map = {
    'crawled': '已爬取',
    'translated': '已翻译',
    'polished': '已润色'
  }
  return map[status] || '未知'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadArticles()
})
</script>

<style scoped>
.home {
  min-height: 100vh;
}

.header {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  padding: 20px 0;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  color: #fff;
  font-size: 24px;
  font-weight: 600;
}

.btn-primary {
  background: #4f46e5;
  color: #fff;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary:hover:not(:disabled) {
  background: #4338ca;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
}

.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  background: #fff;
  padding: 15px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.search-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.3s;
}

.search-input:focus {
  border-color: #4f46e5;
}

.btn-search {
  background: #4f46e5;
  color: #fff;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-search:hover {
  background: #4338ca;
}

.status-filter {
  width: 150px;
}

.news-list {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  overflow: hidden;
}

.loading, .empty {
  padding: 60px;
  text-align: center;
  color: #6b7280;
  font-size: 16px;
}

.news-items {
  divide-y: 1px solid #e5e7eb;
}

.news-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #f3f4f6;
  transition: background 0.2s;
}

.news-item:hover {
  background: #f9fafb;
}

.news-content {
  flex: 1;
  cursor: pointer;
}

.news-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 6px;
  line-height: 1.5;
}

.news-title-zh {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 8px;
}

.news-meta {
  display: flex;
  gap: 12px;
  align-items: center;
}

.status {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status.crawled {
  background: #dbeafe;
  color: #1d4ed8;
}

.status.translated {
  background: #d1fae5;
  color: #059669;
}

.status.polished {
  background: #fef3c7;
  color: #d97706;
}

.date {
  font-size: 12px;
  color: #9ca3af;
}

.news-actions {
  margin-left: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.btn-action {
  background: #fff;
  color: #4f46e5;
  border: 2px solid #4f46e5;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
}

.btn-action:hover:not(:disabled) {
  background: #4f46e5;
  color: #fff;
}

.btn-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  border-color: #9ca3af;
  color: #9ca3af;
}

.btn-fetch-translate {
  border-color: #10b981;
  color: #10b981;
}

.btn-fetch-translate:hover:not(:disabled) {
  background: #10b981;
  color: #fff;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #fff;
  border-top: 1px solid #f3f4f6;
}

.page-btn {
  background: #4f46e5;
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.page-btn:hover:not(:disabled) {
  background: #4338ca;
}

.page-btn:disabled {
  background: #e5e7eb;
  color: #9ca3af;
  cursor: not-allowed;
}

.page-info {
  color: #6b7280;
  font-size: 14px;
}
</style>
