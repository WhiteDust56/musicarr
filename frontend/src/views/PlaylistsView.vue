<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const API_BASE = '/api'
const playlists = ref([])
const loading = ref(true)
const error = ref('')

const fetchPlaylists = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await axios.get(`${API_BASE}/youtube/playlists`)
    playlists.value = res.data
  } catch (err) {
    if (err.response && err.response.status === 401) {
      error.value = 'Not authenticated. Please go to YT Music Auth.'
    } else {
      error.value = 'Failed to load playlists.'
    }
  }
  loading.value = false
}

onMounted(fetchPlaylists)

const toggleSync = async (playlist) => {
  try {
    await axios.put(`${API_BASE}/youtube/playlists/${playlist.id}/sync`, {
      sync_enabled: !playlist.sync_enabled
    })
    playlist.sync_enabled = !playlist.sync_enabled
  } catch (err) {
    alert('Failed to update sync status')
  }
}
</script>

<template>
  <div>
    <h1>Your Playlists</h1>

    <div v-if="error" class="card" style="background: #f8d7da; color: #721c24;">
      {{ error }}
    </div>

    <div v-if="loading">Loading playlists...</div>

    <div v-else-if="playlists.length === 0 && !error">
      No user playlists found.
    </div>

    <div class="card" v-for="p in playlists" :key="p.id" style="display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h3 style="margin: 0 0 5px 0;">{{ p.title }}</h3>
        <small style="color: #7f8c8d;">{{ p.count }} tracks | ID: {{ p.id }}</small>
      </div>
      <div>
        <button
          @click="toggleSync(p)"
          :style="{ background: p.sync_enabled ? '#e74c3c' : '#2ecc71' }">
          {{ p.sync_enabled ? 'Disable Sync' : 'Enable Sync' }}
        </button>
      </div>
    </div>
  </div>
</template>
