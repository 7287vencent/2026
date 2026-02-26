import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000
})

export default {
  getArticles(params) {
    return api.get('/articles', { params })
  },
  
  getArticle(id) {
    return api.get(`/articles/${id}`)
  },
  
  crawlNews() {
    return api.post('/crawl')
  },
  
  fetchContent(id) {
    return api.post(`/articles/${id}/fetch`)
  },
  
  translate(id) {
    return api.post(`/articles/${id}/translate`)
  },
  
  fetchAndTranslate(id) {
    return api.post(`/articles/${id}/fetch-and-translate`)
  },
  
  polish(id) {
    return api.post(`/articles/${id}/polish`)
  }
}
