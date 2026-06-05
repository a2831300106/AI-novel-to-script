<template>
  <div class="preview-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>剧本预览</span>
          <div>
            <el-button @click="goBack">返回</el-button>
            <el-button type="primary" @click="downloadYaml">下载 YAML</el-button>
            <el-button type="success" @click="downloadTxt">下载 TXT</el-button>
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
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getConvertProgress, exportScript } from '../api'

export default {
  name: 'Preview',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const taskId = route.params.taskId

    const scriptMeta = ref(null)
    const characters = ref([])
    const locations = ref([])
    const episodes = ref([])

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

    // 下载 YAML
    const downloadYaml = async () => {
      try {
        const response = await exportScript(taskId, 'yaml')
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

    // 下载 TXT
    const downloadTxt = async () => {
      try {
        const response = await exportScript(taskId, 'txt')
        const blob = new Blob([response.data], { type: 'text/plain' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = 'script.txt'
        link.click()
        window.URL.revokeObjectURL(url)
      } catch (error) {
        ElMessage.error('下载失败')
      }
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
      downloadYaml,
      downloadTxt
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