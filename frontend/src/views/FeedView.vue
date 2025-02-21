<template>
  <div id="entries-container">
    <div v-if="isLoading" class="loading">Lade Feed...</div>
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    <div v-else>
      <div v-if="currentUsername" class="feed-header">
        <button class="back-btn" @click="resetFeed">
          <span class="nav-icon">←</span> Zurück zum Feed
        </button>
        <h2>Öffentliche Einträge von {{ currentUsername }}</h2>
        <button class="share-btn" @click="shareUserFeed" title="Feed teilen">
          <span class="nav-icon">🔗</span> Teilen
        </button>
      </div>
      <div v-else class="feed-header">
        <h2>Öffentliche Einträge</h2>
      </div>

      <div v-if="currentUsername && entries.length > 0" class="chart-container">
        <h3>Stimmungsverlauf</h3>
        <Line
          :data="moodTrendData"
          :options="moodTrendOptions"
          class="mood-chart"
        />
      </div>

      <div v-if="!isAuthenticated" class="login-prompt">
        <p>
          Melde dich an, um nach Benutzern zu suchen und deine eigenen Einträge
          zu teilen!
        </p>
        <router-link to="/login" class="login-btn">Anmelden</router-link>
      </div>

      <div v-else class="search-container">
        <div class="search-box">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Benutzername suchen..."
            @keyup.enter="searchUser"
          />
          <button @click="searchUser" class="search-btn">Suchen</button>
        </div>
        <div v-if="recentUsers.length > 0" class="recent-users">
          <h3>Kürzlich angesehen</h3>
          <div class="user-chips">
            <button
              v-for="username in recentUsers"
              :key="username"
              class="user-chip"
              @click="loadUserFeed(username)"
            >
              {{ username }}
            </button>
          </div>
        </div>
      </div>

      <div v-if="entries.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <h3>
          {{
            currentUsername
              ? `${currentUsername} hat noch keine öffentlichen Einträge`
              : 'Keine öffentlichen Einträge gefunden'
          }}
        </h3>
        <p>
          {{
            currentUsername
              ? 'Schaue später wieder vorbei!'
              : 'Sei der Erste, der einen Eintrag teilt!'
          }}
        </p>
      </div>
      <div v-else class="feed-container">
        <div class="entries-list">
          <div
            v-for="entry in entries"
            :key="entry.id"
            class="entry-card"
            :class="{
              'private-entry': entry.is_encrypted,
              'breakdown-entry': entry.is_breakdown,
            }"
          >
            <div class="entry-header">
              <span class="mood-emoji">{{
                getMoodEmoji(entry.mood_score)
              }}</span>
              <a
                class="username"
                @click.prevent="loadUserFeed(entry.username)"
                href="#"
                >@{{ entry.username }}</a
              >
              <span v-if="entry.is_breakdown" class="breakdown-badge">
                <span class="breakdown-icon">💔</span> Breakdown
              </span>
              <span class="date">{{ formatDate(entry.date) }}</span>
            </div>
            <div class="entry-content">
              <p>{{ entry.content }}</p>
              <span v-if="entry.is_encrypted" class="private-badge"
                >🔒 Privater Eintrag</span
              >
            </div>
            <div class="entry-footer">
              <span
                class="category-badge"
                :style="{ backgroundColor: getCategoryColor(entry.category) }"
              >
                {{ formatCategory(entry.category) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useEntriesStore } from '../stores/entries'
import { useAuthStore } from '../stores/auth'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const route = useRoute()
const router = useRouter()
const entriesStore = useEntriesStore()
const authStore = useAuthStore()
const entries = ref([])
const isLoading = ref(true)
const error = ref(null)
const searchQuery = ref('')
const currentUsername = ref('')
const recentUsers = ref([])

const isAuthenticated = computed(() => authStore.isAuthenticated)

const MAX_RECENT_USERS = 5

function addToRecentUsers(username) {
  if (!recentUsers.value.includes(username)) {
    recentUsers.value.unshift(username)
    if (recentUsers.value.length > MAX_RECENT_USERS) {
      recentUsers.value.pop()
    }
    // Save to localStorage
    localStorage.setItem('recentUsers', JSON.stringify(recentUsers.value))
  }
}

function loadRecentUsers() {
  const saved = localStorage.getItem('recentUsers')
  if (saved) {
    recentUsers.value = JSON.parse(saved)
  }
}

async function loadUserFeed(username) {
  isLoading.value = true
  error.value = null
  currentUsername.value = username
  searchQuery.value = username

  try {
    entries.value = await entriesStore.fetchUserPublicEntries(username)
    if (isAuthenticated.value) {
      addToRecentUsers(username)
    }
  } catch (e) {
    error.value = e.message
  } finally {
    isLoading.value = false
  }
}

async function loadPublicFeed() {
  isLoading.value = true
  error.value = null
  currentUsername.value = ''
  searchQuery.value = ''

  try {
    entries.value = await entriesStore.fetchPublicEntries()
  } catch (e) {
    error.value = e.message
  } finally {
    isLoading.value = false
  }
}

function searchUser() {
  if (searchQuery.value.trim()) {
    loadUserFeed(searchQuery.value.trim())
  } else {
    loadPublicFeed()
  }
}

function resetFeed() {
  router.push({ name: 'feed' })
  loadPublicFeed()
}

function shareUserFeed() {
  const shareUrl = `${window.location.origin}/share/${currentUsername.value}`

  if (navigator.share) {
    navigator
      .share({
        title: `ReMood - ${currentUsername.value}'s Feed`,
        text: `Schaue dir die öffentlichen Einträge von ${currentUsername.value} an!`,
        url: shareUrl,
      })
      .catch(console.error)
  } else {
    navigator.clipboard
      .writeText(shareUrl)
      .then(() => alert('Link in die Zwischenablage kopiert!'))
      .catch(() => alert('Link konnte nicht kopiert werden: ' + shareUrl))
  }
}

function getMoodEmoji(score) {
  const emojis = ['😊', '🙂', '😐', '😕', '😢']
  return emojis[5 - score] || '😐'
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('de-DE', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// Add computed properties for chart data
const moodTrendData = computed(() => {
  const sortedEntries = [...entries.value].sort(
    (a, b) => new Date(a.date) - new Date(b.date)
  )

  return {
    labels: sortedEntries.map((entry) =>
      new Date(entry.date).toLocaleDateString('de-DE', {
        month: 'short',
        day: 'numeric',
      })
    ),
    datasets: [
      {
        label: 'Stimmung',
        data: sortedEntries.map((entry) => entry.mood_score),
        borderColor: '#4a90e2',
        backgroundColor: 'rgba(74, 144, 226, 0.1)',
        fill: true,
        tension: 0.4,
        pointBackgroundColor: sortedEntries.map((entry) =>
          entry.is_encrypted ? '#95a5a6' : getCategoryColor(entry.category)
        ),
        pointStyle: sortedEntries.map((entry) =>
          entry.is_encrypted ? 'rectRot' : 'circle'
        ),
        pointRadius: sortedEntries.map((entry) => (entry.is_encrypted ? 5 : 6)),
        pointHoverRadius: 8,
        pointBorderColor: sortedEntries.map((entry) =>
          entry.is_encrypted ? '#ffffff' : 'transparent'
        ),
        pointBorderWidth: sortedEntries.map((entry) =>
          entry.is_encrypted ? 2 : 0
        ),
      },
    ],
  }
})

const moodTrendOptions = {
  responsive: true,
  maintainAspectRatio: true,
  aspectRatio: 2,
  scales: {
    y: {
      min: 1,
      max: 5,
      reverse: false,
      ticks: {
        stepSize: 1,
        callback: (value) => `${value} ${getMoodEmoji(value)}`,
        color: 'var(--text-color)',
      },
      grid: {
        color: 'var(--border-color)',
        drawBorder: false,
      },
    },
    x: {
      ticks: {
        color: 'var(--text-color)',
      },
      grid: {
        display: false,
      },
    },
  },
  plugins: {
    legend: {
      display: false,
      labels: {
        color: 'var(--text-color)',
      },
    },
    tooltip: {
      enabled: true,
      backgroundColor: '#2d2d2d',
      titleColor: '#e2e8f0',
      bodyColor: '#e2e8f0',
      borderColor: '#404040',
      borderWidth: 1,
      padding: 12,
      displayColors: false,
      callbacks: {
        title: function (tooltipItems) {
          return tooltipItems[0].label
        },
        label: function (context) {
          return `Stimmung: ${context.raw} ${getMoodEmoji(context.raw)}`
        },
      },
      titleFont: {
        family: "'Roboto', sans-serif",
        size: 14,
        weight: 'bold',
      },
      bodyFont: {
        family: "'Roboto', sans-serif",
        size: 14,
      },
      titleMarginBottom: 10,
      caretSize: 8,
      caretPadding: 6,
    },
  },
}

function getCategoryColor(category) {
  const colors = {
    work: '#e67e22',
    family: '#3498db',
    health: '#2ecc71',
    social: '#9b59b6',
    personal: '#f1c40f',
    general: '#95a5a6',
  }
  return colors[category] || colors.general
}

function formatCategory(category) {
  const categories = {
    general: 'Allgemein',
    personal: 'Persönlich',
    social: 'Soziales',
    health: 'Gesundheit',
    family: 'Familie',
    work: 'Arbeit',
  }
  return categories[category.toLowerCase()] || 'Allgemein'
}

onMounted(() => {
  if (route.name === 'shared-feed' && route.params.username) {
    loadUserFeed(route.params.username)
  } else {
    loadPublicFeed()
  }
  if (isAuthenticated.value) {
    loadRecentUsers()
  }
})
</script>

<style scoped>
.search-container {
  margin: 20px 0;
}

.search-box {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-box input {
  flex: 1;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--input-background);
  color: var(--text-color);
}

.search-box input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.search-btn {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: background-color 0.3s;
}

.search-btn:hover {
  background: var(--primary-color-hover);
}

.recent-users {
  margin-top: 20px;
}

.recent-users h3 {
  color: var(--text-color);
  margin-bottom: 10px;
  font-size: 1rem;
}

.user-chips {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.user-chip {
  background: var(--card-background);
  border: 1px solid var(--border-color);
  color: var(--text-color);
  padding: 6px 12px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.user-chip:hover {
  background: var(--hover-background);
  border-color: var(--primary-color);
}

.share-btn {
  background: var(--success-color);
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.share-btn:hover {
  background: #27ae60;
  transform: translateY(-1px);
}

.login-prompt {
  text-align: center;
  padding: 20px;
  background: var(--card-background);
  border-radius: var(--border-radius);
  margin: 20px 0;
}

.login-prompt p {
  color: var(--text-color);
  margin-bottom: 15px;
}

.login-btn {
  display: inline-block;
  background: var(--primary-color);
  color: white;
  padding: 10px 20px;
  border-radius: var(--border-radius);
  text-decoration: none;
  transition: background-color 0.3s;
}

.login-btn:hover {
  background: var(--primary-color-hover);
}

.feed-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.feed-header h2 {
  color: var(--text-color);
  margin: 0;
  flex: 1;
}

.back-btn,
.share-btn {
  background: var(--card-background);
  border: 1px solid var(--border-color);
  color: var(--text-color);
  padding: 8px 16px;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.back-btn:hover,
.share-btn:hover {
  background: var(--hover-background);
  border-color: var(--primary-color);
}

.nav-icon {
  font-size: 1.2rem;
}

.loading,
.error {
  text-align: center;
  padding: 20px;
  color: var(--text-color);
}

.error {
  color: var(--error-color);
}

@media (max-width: 768px) {
  .search-box {
    flex-direction: column;
  }

  .search-btn {
    width: 100%;
  }

  .feed-header {
    flex-direction: column;
    align-items: stretch;
  }

  .share-btn {
    width: 100%;
    justify-content: center;
  }
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: var(--text-color);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}

.empty-state h3 {
  margin-bottom: 10px;
}

.empty-state p {
  opacity: 0.7;
}

.feed-container {
  margin-top: 20px;
}

.entries-list {
  display: grid;
  gap: 20px;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
}

.entry-card {
  background: var(--card-background);
  border-radius: var(--border-radius);
  padding: 20px;
  box-shadow: var(--box-shadow);
  transition: all 0.3s ease;
}

.entry-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.entry-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.mood-emoji {
  font-size: 1.5rem;
}

.username {
  color: var(--primary-color);
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: opacity 0.3s;
}

.username:hover {
  opacity: 0.8;
}

.date {
  color: var(--text-color);
  opacity: 0.7;
  font-size: 0.9rem;
  margin-left: auto;
}

.entry-content {
  color: var(--text-color);
  line-height: 1.5;
  margin: 10px 0;
  white-space: pre-wrap;
}

.entry-footer {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
}

.category-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--card-background);
}

.private-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--text-color);
  opacity: 0.7;
  font-size: 0.9rem;
}

.private-entry {
  background: var(--card-background);
  border: 1px solid var(--border-color);
  opacity: 0.8;
}

.breakdown-entry {
  border-left: 4px solid var(--error-color);
  background: var(--card-background);
  position: relative;
}

.breakdown-entry::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--error-color);
  opacity: 0.1;
  pointer-events: none;
  border-radius: var(--border-radius);
}

.breakdown-entry:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.breakdown-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: var(--card-background);
  color: var(--error-color);
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  border: 1px solid var(--error-color);
}

.breakdown-icon {
  font-size: 1rem;
  color: var(--error-color);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

.chart-container {
  background: var(--card-background);
  padding: 20px;
  border-radius: var(--border-radius);
  margin-bottom: 20px;
}

.chart-container h3 {
  color: var(--text-color);
  margin-bottom: 15px;
}

.mood-chart {
  width: 100%;
  height: 300px;
}

@media (max-width: 768px) {
  .mood-chart {
    max-height: 300px;
  }
}
</style>
