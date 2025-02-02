import { createRouter, createWebHistory } from 'vue-router'
import CreateMeeting from './components/CreateMeeting.vue'
import JoinMeeting from './components/JoinMeeting.vue'

const routes = [
  {
    path: '/',
    name: 'create',
    component: CreateMeeting
  },
  {
    path: '/join/:id',
    name: 'join',
    component: JoinMeeting
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
