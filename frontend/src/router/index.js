import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import SettingsView from '../views/SettingsView.vue'
import PlaylistsView from '../views/PlaylistsView.vue'
import YoutubeAuthView from '../views/YoutubeAuthView.vue'

const routes = [
  { path: '/', component: DashboardView },
  { path: '/settings', component: SettingsView },
  { path: '/playlists', component: PlaylistsView },
  { path: '/youtube-auth', component: YoutubeAuthView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
