<template>
  <div id="app">
    <el-container>
      <el-header>
        <h1>AI 辅助剧本创作工具</h1>
        <p>将小说自动转换为结构化剧本</p>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  font-family: 'Microsoft YaHei', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.el-header {
  background-color: #409EFF;
  color: white;
  text-align: center;
  padding: 20px;
}

.el-header h1 {
  margin: 0;
  font-size: 24px;
}

.el-header p {
  margin: 5px 0 0;
  font-size: 14px;
}

.el-main {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}
</style>