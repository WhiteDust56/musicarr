<template>
  <div class="app-container">
    <nav class="sidebar">
      <h2>YT Music Sync</h2>
      <ul>
        <li><router-link to="/">Dashboard</router-link></li>
        <li><router-link to="/playlists">Playlists</router-link></li>
        <li><router-link to="/settings">Settings</router-link></li>
        <li><router-link to="/youtube-auth">YT Music Auth</router-link></li>
      </ul>
    </nav>
    <main class="content">
      <router-view></router-view>
    </main>
  </div>
</template>

<style>
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  background: #f5f7fa;
  color: #333;
}
.app-container {
  display: flex;
  min-height: 100vh;
}
.sidebar {
  width: 250px;
  background: #2c3e50;
  color: white;
  padding: 20px;
}
.sidebar h2 {
  margin-top: 0;
  margin-bottom: 30px;
  font-size: 1.5rem;
}
.sidebar ul {
  list-style: none;
  padding: 0;
}
.sidebar li {
  margin-bottom: 15px;
}
.sidebar a {
  color: #ecf0f1;
  text-decoration: none;
  font-size: 1.1rem;
}
.sidebar a.router-link-exact-active {
  font-weight: bold;
  color: #3498db;
}
.content {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
}
.card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  margin-bottom: 20px;
}
button {
  background: #3498db;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}
button:hover {
  background: #2980b9;
}
input, select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 100%;
  box-sizing: border-box;
  margin-bottom: 15px;
}
.form-group {
  margin-bottom: 15px;
}
.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}
</style>
