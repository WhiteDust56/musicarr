<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const API_BASE = '/api'
const status = ref({ authenticated: false })
const authUrl = ref('')
const authCode = ref('')
const loading = ref(false)
const message = ref('')

const checkStatus = async () => {
  try {
    const res = await axios.get(`${API_BASE}/youtube/auth/status`)
    status.value = res.data
  } catch (err) {
    console.error(err)
  }
}

onMounted(checkStatus)

const startAuth = async () => {
  loading.value = true
  message.value = ''
  try {
    const res = await axios.get(`${API_BASE}/youtube/auth/start`)
    if (res.data.success) {
      authUrl.value = res.data.url
      authCode.value = res.data.code
    } else {
      message.value = 'Failed to start auth: ' + res.data.message
    }
  } catch (err) {
    message.value = 'Error starting auth'
  }
  loading.value = false
}

const completeAuth = async () => {
  loading.value = true
  try {
    const res = await axios.post(`${API_BASE}/youtube/auth/complete`)
    if (res.data.success) {
      message.value = 'Authentication successful!'
      authUrl.value = ''
      authCode.value = ''
      await checkStatus()
    } else {
      message.value = 'Auth failed: ' + res.data.message
    }
  } catch (err) {
    message.value = 'Error completing auth. Did you approve it in the browser?'
  }
  loading.value = false
}

const logout = async () => {
  await axios.post(`${API_BASE}/youtube/auth/logout`)
  await checkStatus()
}
</script>

<template>
  <div>
    <h1>YouTube Music Authentication</h1>

    <div class="card">
      <div v-if="status.authenticated">
        <h3 style="color: green;">✅ Authenticated</h3>
        <p>Your application is connected to YouTube Music.</p>
        <button @click="logout" style="background: #e74c3c;">Logout</button>
      </div>

      <div v-else>
        <h3 style="color: #e67e22;">❌ Not Authenticated</h3>
        <p>You need to authenticate to sync your playlists.</p>

        <div v-if="!authUrl">
          <button @click="startAuth" :disabled="loading">
            {{ loading ? 'Starting...' : 'Start Authentication Flow' }}
          </button>
        </div>

        <div v-else style="margin-top: 20px; padding: 20px; border: 1px dashed #ccc;">
          <h3>Step 1: Go to this URL in your browser</h3>
          <p><a :href="authUrl" target="_blank">{{ authUrl }}</a></p>

          <h3>Step 2: Enter this code</h3>
          <h2 style="letter-spacing: 5px; background: #eee; display: inline-block; padding: 10px;">{{ authCode }}</h2>

          <h3>Step 3: Click Complete</h3>
          <p>After you have entered the code and approved access, click the button below.</p>
          <button @click="completeAuth" :disabled="loading" style="background: #2ecc71;">
            {{ loading ? 'Verifying...' : 'Complete Authentication' }}
          </button>
        </div>
      </div>

      <div v-if="message" style="margin-top: 20px; padding: 10px; background: #f8f9fa;">
        {{ message }}
      </div>
    </div>
  </div>
</template>
