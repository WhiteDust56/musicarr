<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const API_BASE = '/api'
const tracks = ref([])
const sabQueue = ref(null)
const timer = ref(null)

const fetchData = async () => {
  try {
    const tracksRes = await axios.get(`${API_BASE}/dashboard/tracks`)
    tracks.value = tracksRes.data

    const progressRes = await axios.get(`${API_BASE}/dashboard/sabnzbd/progress`)
    sabQueue.value = progressRes.data.queue?.queue || null
  } catch (err) {
    console.error('Failed to fetch dashboard data', err)
  }
}

onMounted(() => {
  fetchData()
  timer.value = setInterval(fetchData, 5000) // Poll every 5s
})

onUnmounted(() => {
  clearInterval(timer.value)
})
</script>

<template>
  <div>
    <h1>Dashboard</h1>

    <div class="card" v-if="sabQueue">
      <h2>SABnzbd Queue</h2>
      <div style="display: flex; gap: 20px; margin-bottom: 20px;">
        <div><strong>Status:</strong> {{ sabQueue.status }}</div>
        <div><strong>Speed:</strong> {{ sabQueue.speed }}</div>
        <div><strong>Remaining:</strong> {{ sabQueue.timeleft }}</div>
      </div>

      <div v-if="sabQueue.slots.length === 0">Queue is empty</div>
      <div v-else v-for="job in sabQueue.slots" :key="job.nzo_id" style="margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
          <strong>{{ job.filename }}</strong>
          <span>{{ job.percentage }}%</span>
        </div>
        <div style="background: #eee; height: 10px; border-radius: 5px; overflow: hidden;">
          <div :style="{ width: job.percentage + '%', background: '#3498db', height: '100%' }"></div>
        </div>
      </div>
    </div>

    <div class="card">
      <h2>Recent Tracks</h2>
      <table style="width: 100%; border-collapse: collapse;">
        <thead>
          <tr style="text-align: left; border-bottom: 2px solid #ddd;">
            <th style="padding: 10px;">Title</th>
            <th style="padding: 10px;">Artist</th>
            <th style="padding: 10px;">Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in tracks" :key="t.id" style="border-bottom: 1px solid #eee;">
            <td style="padding: 10px;">{{ t.title }}</td>
            <td style="padding: 10px;">{{ t.artist }}</td>
            <td style="padding: 10px;">
              <span :style="{
                padding: '3px 8px', borderRadius: '12px', fontSize: '0.85em',
                background: t.status === 'downloaded' ? '#d4edda' :
                            t.status === 'failed' ? '#f8d7da' :
                            t.status === 'grabbed' ? '#cce5ff' : '#e2e3e5',
                color: t.status === 'downloaded' ? '#155724' :
                       t.status === 'failed' ? '#721c24' :
                       t.status === 'grabbed' ? '#004085' : '#383d41'
              }">
                {{ t.status }}
              </span>
            </td>
          </tr>
          <tr v-if="tracks.length === 0">
            <td colspan="3" style="padding: 10px; text-align: center; color: #777;">No tracks processed yet</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
