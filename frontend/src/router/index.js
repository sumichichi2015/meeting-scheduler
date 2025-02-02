import { createRouter, createWebHistory } from 'vue-router'
import CreateMeeting from '../components/CreateMeeting.vue'
import JoinMeeting from '../components/JoinMeeting.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'create',
      component: CreateMeeting
    },
    {
      path: '/meetings/:id',
      name: 'join',
      component: JoinMeeting
    }
  ]
})

export default router
