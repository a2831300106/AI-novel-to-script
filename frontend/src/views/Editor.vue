<template>
  <div class="editor-page">
    <el-container>
      <!-- 人物面板 -->
      <el-aside width="200px">
        <el-card>
          <template #header>
            <span>人物列表</span>
          </template>
          <el-scrollbar height="400px">
            <div v-for="char in characters" :key="char.id" class="character-item">
              <el-tag :type="getRoleType(char.role)">{{ char.name }}</el-tag>
              <span class="char-desc">{{ char.description }}</span>
            </div>
          </el-scrollbar>
        </el-card>
      </el-aside>

      <!-- 场景编辑器 -->
      <el-main>
        <el-card>
          <template #header>
            <div class="card-header">
              <span>场景编辑</span>
              <el-button type="primary" size="small" @click="saveChanges">保存修改</el-button>
            </div>
          </template>

          <el-collapse v-model="activeEpisodes">
            <el-collapse-item
              v-for="episode in episodes"
              :key="episode.episode"
              :title="episode.title"
              :name="episode.episode"
            >
              <div v-for="scene in episode.scenes" :key="scene.scene_id" class="scene-block">
                <div class="scene-header">
                  <el-tag>场景: {{ getLocationName(scene.location) }}</el-tag>
                  <el-tag type="info">{{ scene.time || '未知时间' }}</el-tag>
                </div>

                <div v-for="beat in scene.beats" :key="beat.beat_id" class="beat-item">
                  <el-tag :type="getBeatType(beat.type)" size="small">{{ beat.type }}</el-tag>

                  <div v-if="beat.type === 'dialogue'" class="dialogue-content">
                    <strong>{{ getCharacterName(beat.character) }}</strong>
                    <span v-if="beat.parenthetical" class="parenthetical">（{{ beat.parenthetical }}）</span>
                    <span>: {{ beat.content }}</span>
                  </div>

                  <div v-else class="beat-content">
                    {{ beat.content }}
                  </div>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
        </el-card>
      </el-main>

      <!-- YAML 预览 -->
      <el-aside width="300px">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>YAML 预览</span>
              <el-button size="small" @click="copyYaml">复制</el-button>
            </div>
          </template>

          <el-scrollbar height="500px">
            <pre class="yaml-preview">{{ yamlContent }}</pre>
          </el-scrollbar>
        </el-card>
      </el-aside>
    </el-container>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getYamlResult, getConvertProgress } from '../api'
import yaml from 'js-yaml'

export default {
  name: 'Editor',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const taskId = route.params.taskId

    const characters = ref([])
    const locations = ref([])
    const episodes = ref([])
    const activeEpisodes = ref([])
    const yamlContent = ref('')

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
        characters.value = scriptData.characters || []
        locations.value = scriptData.locations || []
        episodes.value = scriptData.episodes || []

        // 默认展开第一个章节
        if (episodes.value.length > 0) {
          activeEpisodes.value = [episodes.value[0].episode]
        }

        // 加载 YAML
        const yamlResponse = await getYamlResult(taskId)
        yamlContent.value = yamlResponse.data.yaml
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

    // 获取节拍类型标签
    const getBeatType = (type) => {
      const typeMap = {
        'action': '',
        'dialogue': 'success',
        'transition': 'warning',
        'note': 'info'
      }
      return typeMap[type] || 'info'
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

    // 保存修改
    const saveChanges = () => {
      ElMessage.success('保存成功（演示功能）')
    }

    // 复制 YAML
    const copyYaml = () => {
      navigator.clipboard.writeText(yamlContent.value)
      ElMessage.success('已复制到剪贴板')
    }

    onMounted(loadScriptData)

    return {
      characters,
      locations,
      episodes,
      activeEpisodes,
      yamlContent,
      getRoleType,
      getBeatType,
      getLocationName,
      getCharacterName,
      saveChanges,
      copyYaml
    }
  }
}
</script>

<style scoped>
.editor-page {
  height: calc(100vh - 120px);
}

.el-container {
  height: 100%;
}

.character-item {
  margin-bottom: 10px;
  padding: 5px;
}

.char-desc {
  font-size: 12px;
  color: #666;
  margin-left: 5px;
}

.scene-block {
  margin-bottom: 20px;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 4px;
}

.scene-header {
  margin-bottom: 10px;
}

.beat-item {
  margin-bottom: 8px;
  padding: 5px;
  background: #f5f5f5;
  border-radius: 4px;
}

.dialogue-content {
  margin-left: 10px;
}

.parenthetical {
  color: #999;
  font-size: 12px;
}

.beat-content {
  margin-left: 10px;
  color: #666;
}

.yaml-preview {
  font-size: 12px;
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>