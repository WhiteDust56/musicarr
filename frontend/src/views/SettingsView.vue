<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const API_BASE = '/api'
const settings = ref({
  indexer_url: '',
  indexer_api_key: '',
  sabnzbd_url: '',
  sabnzbd_api_key: '',
  quality: 'MP3',
  sync_interval_minutes: 60,
  download_path: './downloads'
})
const message = ref('')

onMounted(async () => {
  try {
    const res = await axios.get(`${API_BASE}/settings/`)
    settings.value = res.data
  } catch (err) {
    console.error(err)
  }
})

const saveSettings = async () => {
  try {
    const res = await axios.put(`${API_BASE}/settings/`, settings.value)
    settings.value = res.data
    message.value = 'Settings saved successfully!'
    setTimeout(() => message.value = '', 3000)
  } catch (err) {
    message.value = 'Failed to save settings.'
  }
}

const testIndexer = async () => {
  try {
    const res = await axios.post(`${API_BASE}/settings/test-indexer`, settings.value)
    alert(res.data.message)
  } catch (err) {
    alert('Test failed')
  }
}

const testSabnzbd = async () => {
  try {
    const res = await axios.post(`${API_BASE}/settings/test-sabnzbd`, settings.value)
    alert(res.data.message)
  } catch (err) {
    alert('Test failed')
  }
}
</script>

<template>
  <div>
    <h1>Settings</h1>
    <div v-if="message" class="card" style="background: #d4edda; color: #155724; padding: 10px; margin-bottom: 20px;">
      {{ message }}
    </div>

    <div class="card">
      <h2>Indexer Configuration</h2>
      <div class="form-group">
        <label>Newznab API URL</label>
        <input v-model="settings.indexer_url" placeholder="http://indexer.com" />
      </div>
      <div class="form-group">
        <label>Indexer API Key</label>
        <input v-model="settings.indexer_api_key" type="password" />
      </div>
      <button @click="testIndexer">Test Indexer Connection</button>
    </div>

    <div class="card">
      <h2>SABnzbd Configuration</h2>
      <div class="form-group">
        <label>SABnzbd URL</label>
        <input v-model="settings.sabnzbd_url" placeholder="http://localhost:8080" />
      </div>
      <div class="form-group">
        <label>SABnzbd API Key</label>
        <input v-model="settings.sabnzbd_api_key" type="password" />
      </div>
      <button @click="testSabnzbd">Test SABnzbd Connection</button>
    </div>

    <div class="card">
      <h2>Preferences & Fallback</h2>
      <div class="form-group">
        <label>Preferred Quality</label>
        <select v-model="settings.quality">
          <option value="MP3">MP3</option>
          <option value="FLAC">FLAC</option>
        </select>
      </div>
      <div class="form-group">
        <label>Sync Interval (Minutes)</label>
        <input v-model.number="settings.sync_interval_minutes" type="number" />
      </div>
      <div class="form-group">
        <label>YT-DLP Fallback Download Path</label>
        <input v-model="settings.download_path" placeholder="./downloads" />
      </div>
    </div>

    <button @click="saveSettings" style="width: 100%; font-size: 1.2rem; padding: 15px;">Save Settings</button>
  </div>
</template>
