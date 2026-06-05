<template>
  <div class="upload-page">
    <el-tabs v-model="activeTab">
      <!-- 文件上传 -->
      <el-tab-pane label="上传文件" name="file">
        <el-upload
          drag
          action="#"
          :auto-upload="false"
          :on-change="handleFileChange"
          accept=".txt"
          :limit="1"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将 TXT 文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              只支持 TXT 文件，文件大小不超过 10MB
            </div>
          </template>
        </el-upload>
      </el-tab-pane>

      <!-- 在线输入 -->
      <el-tab-pane label="在线输入" name="text">
        <el-input
          v-model="textContent"
          type="textarea"
          :rows="15"
          placeholder="请粘贴小说文本内容..."
        />
        <el-button type="primary" @click="handleTextSubmit" style="margin-top: 10px">
          提交文本
        </el-button>
      </el-tab-pane>
    </el-tabs>

    <!-- 章节预览 -->
    <el-card v-if="uploadResult" class="chapter-preview" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>章节预览</span>
          <el-tag>{{ uploadResult.total_chapters }} 章 / {{ uploadResult.total_words }} 字</el-tag>
        </div>
      </template>

      <el-table :data="uploadResult.chapters" style="width: 100%">
        <el-table-column prop="id" label="章节" width="80" />
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="word_count" label="字数" width="100" />
      </el-table>

      <!-- 转换选项 -->
      <el-divider />
      <el-form :model="convertOptions" label-width="100px">
        <el-form-item label="剧本类型">
          <el-select v-model="convertOptions.script_type">
            <el-option label="网剧" value="series" />
            <el-option label="电影" value="movie" />
            <el-option label="短剧" value="short" />
          </el-select>
        </el-form-item>
        <el-form-item label="AI 服务">
          <el-select v-model="convertOptions.ai_provider">
            <el-option label="文心一言" value="wenxin" />
            <el-option label="通义千问" value="qwen" />
          </el-select>
        </el-form-item>
      </el-form>

      <el-button type="primary" size="large" @click="startConvert" :loading="converting">
        开始转换
      </el-button>
    </el-card>

    <!-- 转换进度 -->
    <el-card v-if="converting" class="convert-progress" style="margin-top: 20px">
      <template #header>
        <span>转换进度</span>
      </template>

      <el-progress :percentage="progress * 100" :status="progressStatus" />
      <p style="margin-top: 10px">{{ currentStep }}</p>
    </el-card>

    <!-- 转换完成 -->
    <el-card v-if="convertCompleted" class="convert-result" style="margin-top: 20px">
      <template #header>
        <span>转换完成</span>
      </template>

      <el-button type="primary" @click="goToEditor">编辑剧本</el-button>
      <el-button @click="goToPreview">预览剧本</el-button>
      <el-button type="success" @click="downloadYaml">下载 YAML</el-button>
    </el-card>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { uploadNovel, uploadText, startConvert, getConvertProgress, exportScript } from '../api'

export default {
  name: 'Upload',
  components: { UploadFilled },
  setup() {
    const router = useRouter()
    const activeTab = ref('file')
    const textContent = ref('')
    const uploadResult = ref(null)
    const taskId = ref(null)
    const converting = ref(false)
    const progress = ref(0)
    const currentStep = ref('')
    const convertCompleted = ref(false)
    const convertOptions = ref({
      script_type: 'series',
      ai_provider: 'wenxin'
    })

    // 处理文件上传
    const handleFileChange = async (file) => {
      try {
        const response = await uploadNovel(file.raw)
        uploadResult.value = response.data
        taskId.value = response.data.task_id
        ElMessage.success('上传成功')
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '上传失败')
      }
    }

    // 处理文本提交
    const handleTextSubmit = async () => {
      if (!textContent.value.trim()) {
        ElMessage.warning('请输入小说文本')
        return
      }

      try {
        const response = await uploadText(textContent.value)
        uploadResult.value = response.data
        taskId.value = response.data.task_id
        ElMessage.success('提交成功')
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '提交失败')
      }
    }

    // 开始转换
    const startConvertProcess = async () => {
      converting.value = true
      progress.value = 0
      currentStep.value = '准备开始...'
      convertCompleted.value = false

      try {
        await startConvert(taskId.value, convertOptions.value)

        // 定时查询进度
        const pollProgress = async () => {
          const response = await getConvertProgress(taskId.value)
          const data = response.data

          progress.value = data.progress
          currentStep.value = getStepText(data.current_step)

          if (data.status === 'completed') {
            converting.value = false
            convertCompleted.value = true
            ElMessage.success('转换完成')
          } else if (data.status === 'failed') {
            converting.value = false
            ElMessage.error(data.error || '转换失败')
          } else {
            // 继续轮询
            setTimeout(pollProgress, 2000)
          }
        }

        pollProgress()
      } catch (error) {
        converting.value = false
        ElMessage.error(error.response?.data?.detail || '转换失败')
      }
    }

    // 获取步骤文本
    const getStepText = (step) => {
      const stepMap = {
        'extracting_characters': '正在提取人物信息...',
        'extracting_locations': '正在提取场景信息...',
        'extracting_storylines': '正在提取剧情线...',
        'generating_script': '正在生成剧本...',
        'completed': '转换完成'
      }
      return stepMap[step] || '处理中...'
    }

    // 进度状态
    const progressStatus = computed(() => {
      if (convertCompleted.value) return 'success'
      if (progress.value === 0) return ''
      return null
    })

    // 跳转到编辑页面
    const goToEditor = () => {
      router.push(`/editor/${taskId.value}`)
    }

    // 跳转到预览页面
    const goToPreview = () => {
      router.push(`/preview/${taskId.value}`)
    }

    // 下载 YAML
    const downloadYaml = async () => {
      try {
        const response = await exportScript(taskId.value, 'yaml')
        const blob = new Blob([response.data], { type: 'application/x-yaml' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = 'script.yaml'
        link.click()
        window.URL.revokeObjectURL(url)
      } catch (error) {
        ElMessage.error('下载失败')
      }
    }

    return {
      activeTab,
      textContent,
      uploadResult,
      converting,
      progress,
      currentStep,
      convertCompleted,
      convertOptions,
      handleFileChange,
      handleTextSubmit,
      startConvert: startConvertProcess,
      progressStatus,
      goToEditor,
      goToPreview,
      downloadYaml
    }
  }
}
</script>

<style scoped>
.upload-page {
  max-width: 800px;
  margin: 0 auto;
}

.chapter-preview .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>