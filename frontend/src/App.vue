<template>
  <div class="container">
    <NavBar />

    <main>
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useThemeStore } from './stores/theme'
import NavBar from './components/NavBar.vue'

const themeStore = useThemeStore()

onMounted(() => {
  themeStore.initializeTheme()
})
</script>

<style>
:root {
  --primary-color: #4a90e2;
  --secondary-color: #2c3e50;
  --background-color: #f5f6fa;
  --text-color: #2c3e50;
  --error-color: #e74c3c;
  --success-color: #2ecc71;
  --border-radius: 8px;
  --box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Roboto', sans-serif;
  background-color: var(--background-color);
  color: var(--text-color);
  line-height: 1.6;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  body {
    padding-bottom: 70px;
  }

  .container {
    padding: 10px;
  }
}
</style>
