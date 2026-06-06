<template>
  <div class="preview-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>剧本预览</span>
          <div>
            <el-button @click="goBack">返回</el-button>
            <el-dropdown @command="handleExport" style="margin-left: 10px;">
              <el-button type="primary">
                导出剧本 <el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="yaml">YAML 格式</el-dropdown-item>
                  <el-dropdown-item command="json">JSON 格式</el-dropdown-item>
                  <el-dropdown-item command="txt">TXT 格式</el-dropdown-item>
                  <el-dropdown-item command="fdx">Final Draft (.fdx)</el-dropdown-item>
                  <el-dropdown-item command="fountain">Fountain 格式</el-dropdown-item>
                  <el-dropdown-item command="storyboard">分镜脚本</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-button type="success" @click="showAnalysisDialog" style="margin-left: 10px;">
              智能分析
            </el-button>
          </div>
        </div>
      </template>

      <!-- 剧本元数据 -->
      <div v-if="scriptMeta" class="script-meta">
        <h2>{{ scriptMeta.title }}</h2>
        <p><strong>原著来源:</strong> {{ scriptMeta.source }}</p>
        <p><strong>改编作者:</strong> {{ scriptMeta.author }}</p>
        <p><strong>创建日期:</strong> {{ scriptMeta.created_at }}</p>
        <p><strong>故事梗概:</strong> {{ scriptMeta.synopsis }}</p>
      </div>

      <el-divider />

      <!-- 人物表 -->
      <div v-if="characters.length > 0" class="characters-section">
        <h3>人物表</h3>
        <el-table :data="characters" style="width: 100%">
          <el-table-column prop="name" label="姓名" width="100" />
          <el-table-column prop="role" label="角色" width="100">
            <template #default="{ row }">
              <el-tag :type="getRoleType(row.role)">{{ getRoleText(row.role) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="alias" label="别名">
            <template #default="{ row }">
              {{ row.alias.join(', ') || '无' }}
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" />
        </el-table>
      </div>

      <el-divider />

      <!-- 场景表 -->
      <div v-if="locations.length > 0" class="locations-section">
        <h3>场景表</h3>
        <el-table :data="locations" style="width: 100%">
          <el-table-column prop="name" label="名称" width="150" />
          <el-table-column prop="type" label="类型" width="100">
            <template #default="{ row }">
              {{ getTypeText(row.type) }}
            </template>
          </el-table-column>
          <el-table-column prop="time" label="时间" width="100">
            <template #default="{ row }">
              {{ getTimeText(row.time) }}
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" />
        </el-table>
      </div>

      <el-divider />

      <!-- 分集内容 -->
      <div v-for="episode in episodes" :key="episode.episode" class="episode-section">
        <h3>第 {{ episode.episode }} 章: {{ episode.title }}</h3>
        <p class="episode-synopsis">{{ episode.synopsis }}</p>

        <div v-for="scene in episode.scenes" :key="scene.scene_id" class="scene-block">
          <div class="scene-header">
            <strong>【场景: {{ getLocationName(scene.location) }}】</strong>
            <span class="scene-time">{{ getTimeText(scene.time) }}</span>
          </div>

          <div class="beats-list">
            <div v-for="beat in scene.beats" :key="beat.beat_id" class="beat-line">
              <span v-if="beat.type === 'action'" class="action-beat">
                [动作] {{ beat.content }}
              </span>

              <span v-else-if="beat.type === 'dialogue'" class="dialogue-beat">
                <strong>{{ getCharacterName(beat.character) }}</strong>
                <span v-if="beat.parenthetical" class="parenthetical">（{{ beat.parenthetical }}）</span>
                : {{ beat.content }}
              </span>

              <span v-else-if="beat.type === 'transition'" class="transition-beat">
                [转场] {{ beat.content }}
              </span>

              <span v-else class="note-beat">
                [备注] {{ beat.content }}
              </span>
            </div>
          </div>
        </div>

        <el-divider />
      </div>
    </el-card>

    <!-- 智能分析对话框 -->
    <el-dialog v-model="analysisDialogVisible" title="剧本智能分析" width="80%" top="5vh">
      <el-tabs v-model="activeAnalysisTab">
        <el-tab-pane label="角色关系图谱" name="relationships">
          <div v-if="relationshipData" class="analysis-content">
            <div class="relationship-graph">
              <h4>角色关系网络</h4>
              <div class="nodes-list">
                <el-tag v-for="node in relationshipData.nodes" :key="node.id"
                  :type="node.role === 'protagonist' ? 'success' : node.role === 'supporting' ? 'warning' : 'info'"
                  style="margin: 5px;">{{ node.name }}</el-tag>
              </div>
              <div class="links-list" v-if="relationshipData.links.length > 0">
                <h4>关系连接</h4>
                <el-table :data="relationshipData.links" size="small">
                  <el-table-column prop="source" label="角色A" width="120" />
                  <el-table-column prop="target" label="角色B" width="120" />
                  <el-table-column prop="strength" label="强度" width="80">
                    <template #default="{ row }">
                      <el-rate v-model="row.strength" disabled :max="3" size="small" />
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无数据" />
        </el-tab-pane>

        <el-tab-pane label="剧情节奏分析" name="rhythm">
          <div v-if="rhythmData" class="analysis-content">
            <div class="rhythm-summary">
              <el-descriptions :column="3" border>
                <el-descriptions-item label="整体弧线">{{ rhythmData.overall_arc?.type }}</el-descriptions-item>
                <el-descriptions-item label="弧线描述">{{ rhythmData.overall_arc?.description }}</el-descriptions-item>
                <el-descriptions-item label="高潮章节">第 {{ rhythmData.overall_arc?.peak_episode }} 章</el-descriptions-item>
              </el-descriptions>
            </div>
            <div class="episode-rhythm">
              <h4>各章节节奏</h4>
              <el-table :data="rhythmData.episodes" size="small">
                <el-table-column prop="episode" label="章节" width="80" />
                <el-table-column prop="title" label="标题" />
                <el-table-column prop="pace" label="节奏" width="100">
                  <template #default="{ row }">
                    <el-tag :type="row.pace === 'fast' ? 'danger' : row.pace === 'slow' ? 'success' : 'warning'">
                      {{ row.pace === 'fast' ? '快' : row.pace === 'slow' ? '慢' : '中' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="avg_intensity" label="情感强度" width="100">
                  <template #default="{ row }">
                    <el-progress :percentage="row.avg_intensity * 100" :stroke-width="8" />
                  </template>
                </el-table-column>
              </el-table>
            </div>
            <div class="climax-points" v-if="rhythmData.climax_points?.length > 0">
              <h4>高潮点检测</h4>
              <el-table :data="rhythmData.climax_points" size="small">
                <el-table-column prop="episode" label="章节" width="80" />
                <el-table-column prop="type" label="类型" width="120">
                  <template #default="{ row }">
                    {{ row.type === 'action_climax' ? '动作高潮' : '对话高潮' }}
                  </template>
                </el-table-column>
                <el-table-column prop="content" label="内容片段" />
              </el-table>
            </div>
          </div>
          <el-empty v-else description="暂无数据" />
        </el-tab-pane>

        <el-tab-pane label="对话风格分析" name="dialogue">
          <div v-if="dialogueData" class="analysis-content">
            <el-table :data="Object.entries(dialogueData).map(([name, data]) => ({ name, ...data }))" size="small">
              <el-table-column prop="name" label="角色" width="120" />
              <el-table-column prop="dialogue_count" label="台词数" width="80" />
              <el-table-column prop="avg_length" label="平均长度" width="100" />
              <el-table-column prop="style" label="风格" width="120">
                <template #default="{ row }">
                  <el-tag :type="getStyleTagType(row.style)">{{ getStyleText(row.style) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="description" label="描述" />
            </el-table>
          </div>
          <el-empty v-else description="暂无数据" />
        </el-tab-pane>
      </el-tabs>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import { getConvertProgress, exportScript, analyzeScript, analyzeRelationships, analyzeRhythm, analyzeDialogue } from '../api'

export default {
  name: 'Preview',
  components: { ArrowDown },
  setup() {
    const router = useRouter()
    const route = useRoute()
    const taskId = route.params.taskId

    const scriptMeta = ref(null)
    const characters = ref([])
    const locations = ref([])
    const episodes = ref([])

    const analysisDialogVisible = ref(false)
    const activeAnalysisTab = ref('relationships')
    const relationshipData = ref(null)
    const rhythmData = ref(null)
    const dialogueData = ref(null)

    // 加载剧本数据
    const loadScriptData = async () => {
      try {
        const response = await getConvertProgress(taskId)
        if (response.data.status !== 'completed') {
          ElMessage.warning('剧本尚未生成完成')
          router.push('/')
          return
        }

        const scriptData = response.data.result
        scriptMeta.value = scriptData.script
        characters.value = scriptData.characters || []
        locations.value = scriptData.locations || []
        episodes.value = scriptData.episodes || []
      } catch (error) {
        ElMessage.error('加载失败')
        router.push('/')
      }
    }

    // 获取角色类型标签
    const getRoleType = (role) => {
      const roleMap = {
        'protagonist': 'success',
        'supporting': 'warning',
        'minor': 'info'
      }
      return roleMap[role] || 'info'
    }

    // 获取角色类型文本
    const getRoleText = (role) => {
      const roleMap = {
        'protagonist': '主角',
        'supporting': '配角',
        'minor': '龙套'
      }
      return roleMap[role] || '未知'
    }

    // 获取场景类型文本
    const getTypeText = (type) => {
      const typeMap = {
        'interior': '内景',
        'exterior': '外景'
      }
      return typeMap[type] || '未知'
    }

    // 获取时间文本
    const getTimeText = (time) => {
      const timeMap = {
        'day': '日',
        'night': '夜',
        'dawn': '晨',
        'dusk': '暮'
      }
      return timeMap[time] || '未知'
    }

    // 获取场景名称
    const getLocationName = (locationId) => {
      const location = locations.value.find(loc => loc.id === locationId)
      return location ? location.name : '未知场景'
    }

    // 获取人物名称
    const getCharacterName = (characterId) => {
      const character = characters.value.find(char => char.id === characterId)
      return character ? character.name : '未知人物'
    }

    // 返回
    const goBack = () => {
      router.push('/')
    }

    // 导出剧本
    const handleExport = async (format) => {
      try {
        const response = await exportScript(taskId, format)
        const mimeTypes = {
          'yaml': 'application/x-yaml',
          'json': 'application/json',
          'txt': 'text/plain',
          'fdx': 'application/xml',
          'fountain': 'text/plain',
          'storyboard': 'text/plain'
        }
        const extensions = {
          'yaml': 'yaml',
          'json': 'json',
          'txt': 'txt',
          'fdx': 'fdx',
          'fountain': 'fountain',
          'storyboard': 'txt'
        }
        const blob = new Blob([response.data], { type: mimeTypes[format] })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `script.${extensions[format]}`
        link.click()
        window.URL.revokeObjectURL(url)
        ElMessage.success(`导出 ${format} 格式成功`)
      } catch (error) {
        ElMessage.error('导出失败')
      }
    }

    // 显示分析对话框
    const showAnalysisDialog = async () => {
      analysisDialogVisible.value = true
      await loadAnalysisData()
    }

    // 加载分析数据
    const loadAnalysisData = async () => {
      try {
        const [relRes, rhythmRes, dialogueRes] = await Promise.all([
          analyzeRelationships(taskId),
          analyzeRhythm(taskId),
          analyzeDialogue(taskId)
        ])
        relationshipData.value = relRes.data
        rhythmData.value = rhythmRes.data
        dialogueData.value = dialogueRes.data
      } catch (error) {
        ElMessage.error('加载分析数据失败')
      }
    }

    // 获取风格标签类型
    const getStyleTagType = (style) => {
      const styleMap = {
        'passionate': 'danger',
        'inquisitive': 'primary',
        'verbose': 'warning',
        'concise': 'success',
        'balanced': 'info'
      }
      return styleMap[style] || 'info'
    }

    // 获取风格文本
    const getStyleText = (style) => {
      const styleMap = {
        'passionate': '热情型',
        'inquisitive': '提问型',
        'verbose': '详尽型',
        'concise': '简洁型',
        'balanced': '平衡型'
      }
      return styleMap[style] || '未知'
    }

    onMounted(loadScriptData)

    return {
      scriptMeta,
      characters,
      locations,
      episodes,
      getRoleType,
      getRoleText,
      getTypeText,
      getTimeText,
      getLocationName,
      getCharacterName,
      goBack,
      handleExport,
      analysisDialogVisible,
      activeAnalysisTab,
      relationshipData,
      rhythmData,
      dialogueData,
      showAnalysisDialog,
      getStyleTagType,
      getStyleText
    }
  }
}
</script>

<style scoped>
.preview-page {
  max-width: 900px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.script-meta {
  text-align: center;
  padding: 20px;
}

.script-meta h2 {
  margin-bottom: 15px;
}

.script-meta p {
  margin: 5px 0;
  color: #666;
}

.characters-section,
.locations-section,
.episode-section {
  margin-bottom: 20px;
}

.episode-synopsis {
  color: #666;
  margin-bottom: 15px;
}

.scene-block {
  margin-bottom: 15px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.scene-header {
  margin-bottom: 10px;
}

.scene-time {
  color: #999;
  margin-left: 10px;
}

.beats-list {
  padding-left: 20px;
}

.beat-line {
  margin-bottom: 8px;
  line-height: 1.6;
}

.action-beat {
  color: #666;
}

.dialogue-beat {
  color: #333;
}

.parenthetical {
  color: #999;
  font-size: 12px;
}

.transition-beat {
  color: #E6A23C;
  font-style: italic;
}

.note-beat {
  color: #909399;
  font-size: 12px;
}
</style>