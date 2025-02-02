<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold text-center mb-8">会議調整アプリ</h1>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <div class="bg-white p-6 rounded-lg shadow-lg">
        <h2 class="text-xl font-semibold mb-4">新しい会議を作成</h2>
        <CreateMeeting />
      </div>
      
      <div class="bg-white p-6 rounded-lg shadow-lg">
        <h2 class="text-xl font-semibold mb-4">会議に参加</h2>
        <JoinMeeting />
      </div>
    </div>
  </div>
</template>

<script setup>
import CreateMeeting from './components/CreateMeeting.vue'
import JoinMeeting from './components/JoinMeeting.vue'
</script>

<style>
:root {
  --primary-color: #4CAF50;
  --secondary-color: #FFC107;
  --danger-color: #f44336;
  --text-color: #333;
  --background-color: #f5f5f5;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  color: var(--text-color);
  background-color: #f3f4f6;
  line-height: 1.6;
}

.app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

header {
  text-align: center;
  margin-bottom: 40px;
}

h1 {
  color: var(--primary-color);
  font-size: 2rem;
}

main {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>
