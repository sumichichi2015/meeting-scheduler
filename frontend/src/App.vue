<template>
  <div class="app">
    <header>
      <h1>会議調整アプリ</h1>
    </header>
    <main>
      <router-view></router-view>
    </main>
  </div>
</template>

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
  background-color: var(--background-color);
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
