import { useThemeStore } from '../stores/theme' const themeStore =
useThemeStore()

<template>
  <div class="nav-wrapper">
    <nav class="navbar">
      <div class="nav-content">
        <router-link to="/" class="logo">
          <h1><span class="re">Re</span>Mood</h1>
        </router-link>

        <div class="nav-links">
          <button
            class="theme-toggle"
            @click="themeStore.toggleDarkMode()"
            :title="themeStore.isDarkMode ? 'Zum hellen Design wechseln' : 'Zum dunklen Design wechseln'"
          >
            {{ themeStore.isDarkMode ? '☀️' : '🌙' }}
          </button>
          <template v-if="isAuthenticated">
            <router-link
              v-for="item in navItems"
              :key="item.name"
              :to="{ name: item.route }"
              class="nav-btn"
              :class="{ active: currentRoute === item.route }"
            >
              <span class="nav-icon">{{ item.icon }}</span>
              <span>{{ item.label }}</span>
            </router-link>
            <div class="user-info">
              <router-link :to="{ name: 'profile' }" class="username">
                {{ username }}
              </router-link>
              <button @click="logout" class="nav-btn">Abmelden</button>
            </div>
          </template>
          <template v-else>
            <router-link to="/login" class="nav-btn">Anmelden</router-link>
          </template>
        </div>
      </div>
    </nav>

    <nav v-if="isAuthenticated" class="mobile-nav">
      <button
        v-for="item in navItems"
        :key="item.name"
        class="nav-btn"
        :class="{ active: currentRoute === item.route }"
        @click="navigate(item.route)"
      >
        <span class="nav-icon">{{ item.icon }}</span>
        <span>{{ item.label }}</span>
      </button>
    </nav>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useThemeStore } from '../stores/theme'

const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)
const username = computed(() => authStore.username)
const currentRoute = computed(() => router.currentRoute.value.name)

const navItems = [
  { name: 'entries', route: 'entries', icon: '📝', label: 'Einträge' },
  { name: 'feed', route: 'feed', icon: '🌍', label: 'Feed' },
  { name: 'new', route: 'new-entry', icon: '➕', label: 'Neu' },
  { name: 'dashboard', route: 'dashboard', icon: '📊', label: 'Dashboard' },
]

const navigate = (route) => {
  router.push({ name: route })
}

const logout = () => {
  authStore.logout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.nav-wrapper {
  position: relative;
}

.navbar {
  background-color: var(--card-background);
  box-shadow: var(--box-shadow);
  padding: 1rem;
  margin-bottom: 2rem;
  transition: background-color 0.3s ease;
}

.nav-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  text-decoration: none;
}

.logo h1 {
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(45deg, var(--primary-color), #357abd);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.logo .re {
  font-weight: 300;
  color: var(--secondary-color);
  -webkit-text-fill-color: var(--secondary-color);
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.theme-toggle {
  background: none;
  border: none;
  font-size: 1.2rem;
  padding: 8px;
  cursor: pointer;
  color: var(--text-color);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s ease;
}

.theme-toggle:hover {
  transform: scale(1.1);
  background: none;
}

.nav-btn {
  background-color: var(--primary-color);
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 5px;
}

.nav-btn:hover,
.nav-btn.active {
  background-color: #357abd;
  transform: translateY(-1px);
}

.nav-icon {
  font-size: 1.2rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: 1rem;
}

.username {
  font-weight: 500;
  color: var(--text-color);
  text-decoration: none;
  transition: color 0.3s;
}

.username:hover {
  color: var(--primary-color);
}

.mobile-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--card-background);
  padding: 10px 20px;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  display: none;
  z-index: 1000;
  justify-content: space-around;
  border-top: 1px solid var(--border-color);
  transition: background-color 0.3s ease;
}

.mobile-nav .nav-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  background: none;
  color: var(--text-color);
  padding: 8px 12px;
  border-radius: var(--border-radius);
  font-size: 0.8rem;
}

.mobile-nav .nav-btn:hover,
.mobile-nav .nav-btn.active {
  background: var(--primary-color);
  color: white;
}

@media (max-width: 768px) {
  .nav-links {
    display: none;
  }
  
  .navbar {
    padding: 0.5rem;
    margin-bottom: 1rem;
  }
  
  .logo h1 {
    font-size: 1.5rem;
  }

  .mobile-nav {
    display: flex;
  }
}
</style>
