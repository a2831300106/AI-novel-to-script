import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

// 上传小说
export const uploadNovel = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/upload', formData)
}

// 上传文本
export const uploadText = (text) => {
  const formData = new FormData()
  formData.append('text', text)
  return api.post('/upload', formData)
}

// 获取上传信息
export const getUploadInfo = (taskId) => {
  return api.get(`/upload/${taskId}`)
}

// 开始转换
export const startConvert = (taskId, options = {}) => {
  return api.post('/convert', {
    task_id: taskId,
    options
  })
}

// 获取转换进度
export const getConvertProgress = (taskId) => {
  return api.get(`/convert/${taskId}/progress`)
}

// 获取 YAML 结果
export const getYamlResult = (taskId) => {
  return api.get(`/convert/${taskId}/yaml`)
}

// 导出剧本
export const exportScript = (taskId, format = 'yaml') => {
  return api.get(`/export/${taskId}`, {
    params: { format },
    responseType: 'blob'
  })
}

// 分析剧本 - 完整报告
export const analyzeScript = (taskId) => {
  return api.get(`/analyze/${taskId}`)
}

// 分析角色关系
export const analyzeRelationships = (taskId) => {
  return api.get(`/analyze/${taskId}/relationships`)
}

// 分析剧情节奏
export const analyzeRhythm = (taskId) => {
  return api.get(`/analyze/${taskId}/rhythm`)
}

// 分析对话风格
export const analyzeDialogue = (taskId) => {
  return api.get(`/analyze/${taskId}/dialogue`)
}

export default api