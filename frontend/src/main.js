import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import CreateMeeting from './components/CreateMeeting.vue'
import JoinMeeting from './components/JoinMeeting.vue'
import VCalendar from 'v-calendar'
import 'v-calendar/style.css'

const routes = [
  { path: '/', redirect: '/create' },
  { path: '/create', component: CreateMeeting },
  { path: '/join', component: JoinMeeting },
  { path: '/meeting/:id', component: JoinMeeting }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(VCalendar, {})
app.mount('#app')
