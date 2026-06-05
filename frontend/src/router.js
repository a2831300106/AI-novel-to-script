import { createRouter, createWebHistory } from 'vue-router'
import Upload from './views/Upload.vue'
import Editor from './views/Editor.vue'
import Preview from './views/Preview.vue'

const routes = [
  {
    path: '/',
    name: 'Upload',
    component: Upload
  },
  {
    path: '/editor/:taskId',
    name: 'Editor',
    component: Editor
  },
  {
    path: '/preview/:taskId',
    name: 'Preview',
    component: Preview
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router