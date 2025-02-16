<template>
  <div id="entries-container">
    <div class="tabs">
      <div class="tab-buttons">
        <button
          class="tab-btn"
          :class="{ active: $route.name === 'entries' }"
          @click="$router.push({ name: 'entries' })"
        >
          Meine Einträge
        </button>
        <button
          class="tab-btn"
          :class="{ active: $route.name === 'dashboard' }"
          @click="$router.push({ name: 'dashboard' })"
        >
          Dashboard
        </button>
      </div>
      <button
        class="new-entry-btn"
        @click="$router.push({ name: 'new-entry' })"
      >
        <span class="nav-icon">➕</span> Neuer Eintrag
      </button>
    </div>

    <div v-if="isLoading" class="loading">Lade Dashboard...</div>
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    <div v-else class="dashboard">
      <div class="dashboard-grid">
        <div
          v-if="moodBoostRecommendations.length > 0"
          class="chart-container mood-boost"
        >
          <h3>🌟 Mood Boost Empfehlungen</h3>
          <div class="recommendations">
            <div
              v-for="(rec, index) in moodBoostRecommendations"
              :key="index"
              class="recommendation-card"
            >
              <div class="recommendation-header">
                <span class="mood-emoji">{{
                  getMoodEmoji(rec.entry.mood_score)
                }}</span>
                <span
                  class="category-badge"
                  :style="{
                    backgroundColor: entriesStore.getCategoryColor(
                      rec.category
                    ),
                  }"
                >
                  {{ entriesStore.formatCategory(rec.category) }}
                </span>
                <span class="entry-date">{{
                  new Date(rec.entry.date).toLocaleDateString('de-DE')
                }}</span>
              </div>
              <div class="recommendation-content">
                {{ rec.entry.content }}
              </div>
              <div class="recommendation-reason">
                {{ rec.reason }}
              </div>
            </div>
          </div>
        </div>

        <div class="chart-container">
          <h3>Stimmungsverlauf</h3>
          <Line :data="moodTrendData" :options="moodTrendOptions" />
        </div>
        <div class="chart-container">
          <h3>Stimmungsverteilung</h3>
          <Doughnut
            :data="moodDistributionData"
            :options="moodDistributionOptions"
          />
        </div>
        <div class="stats-container">
          <div class="stat-card">
            <h4>Durchschnittliche Stimmung</h4>
            <div class="stat-value">
              {{ averageMood.toFixed(1) }}
              {{ getMoodEmoji(Math.round(averageMood)) }}
            </div>
          </div>
          <div class="stat-card">
            <h4>Häufigste Stimmung</h4>
            <div class="stat-value">
              {{ commonMood }} {{ getMoodEmoji(parseInt(commonMood)) }}
            </div>
          </div>
          <div class="stat-card">
            <h4>Einträge gesamt</h4>
            <div class="stat-value">{{ totalEntries }}</div>
          </div>
          <div v-if="categoryStats.best.category" class="stat-card positive">
            <h4>Beste Kategorie</h4>
            <div class="stat-value category-stat">
              <span class="category-name">
                {{ entriesStore.formatCategory(categoryStats.best.category) }}
              </span>
              <span class="category-score">
                {{ categoryStats.best.average.toFixed(1) }}
                {{ getMoodEmoji(Math.round(categoryStats.best.average)) }}
              </span>
            </div>
          </div>
          <div v-if="categoryStats.worst.category" class="stat-card negative">
            <h4>Schlechteste Kategorie</h4>
            <div class="stat-value category-stat">
              <span class="category-name">
                {{ entriesStore.formatCategory(categoryStats.worst.category) }}
              </span>
              <span class="category-score">
                {{ categoryStats.worst.average.toFixed(1) }}
                {{ getMoodEmoji(Math.round(categoryStats.worst.average)) }}
              </span>
            </div>
          </div>
        </div>
        <div class="chart-container">
          <h3>Kategorieverteilung</h3>
          <Pie
            :data="categoryDistributionData"
            :options="categoryDistributionOptions"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Line, Doughnut, Pie } from 'vue-chartjs'
import { useEntriesStore } from '../stores/entries'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
)

const entriesStore = useEntriesStore()
const entries = ref([])
const isLoading = ref(true)
const error = ref(null)

// Stats
const totalEntries = computed(() => entries.value.length)
const averageMood = computed(() => {
  const sum = entries.value.reduce((acc, entry) => acc + entry.mood_score, 0)
  return sum / totalEntries.value
})
const commonMood = computed(() => {
  const moodCounts = entries.value.reduce((acc, entry) => {
    acc[entry.mood_score] = (acc[entry.mood_score] || 0) + 1
    return acc
  }, {})
  return Object.entries(moodCounts).reduce((a, b) => (b[1] > a[1] ? b : a))[0]
})

// Category Stats
const categoryStats = computed(() => {
  const stats = entries.value.reduce((acc, entry) => {
    if (!acc[entry.category]) {
      acc[entry.category] = {
        totalMood: 0,
        count: 0,
        scores: [],
        positiveEntries: [],
      }
    }
    acc[entry.category].totalMood += entry.mood_score
    acc[entry.category].count++
    acc[entry.category].scores.push(entry.mood_score)

    if (entry.mood_score >= 4) {
      acc[entry.category].positiveEntries.push(entry)
    }

    return acc
  }, {})

  // Calculate averages and find best/worst
  let bestCategory = { category: null, average: 0 }
  let worstCategory = { category: null, average: 6 }

  Object.entries(stats).forEach(([category, data]) => {
    const average = data.totalMood / data.count
    if (average > bestCategory.average && data.count >= 3) {
      bestCategory = { category, average }
    }
    if (average < worstCategory.average && data.count >= 3) {
      worstCategory = { category, average }
    }
  })

  return {
    best: bestCategory,
    worst: worstCategory,
    categoryData: stats,
  }
})

// Add computed property for mood boost recommendations
const moodBoostRecommendations = computed(() => {
  if (!entries.value.length) return []

  const stats = categoryStats.value.categoryData
  const recommendations = []

  // Get categories with below-average mood scores
  Object.entries(stats).forEach(([category, data]) => {
    const average = data.totalMood / data.count
    if (average < 3.5 && data.positiveEntries.length > 0) {
      // Get a random positive entry from this category
      const randomIndex = Math.floor(
        Math.random() * data.positiveEntries.length
      )
      const recommendation = data.positiveEntries[randomIndex]
      recommendations.push({
        category,
        entry: recommendation,
        reason: `Dieser positive Eintrag aus der Kategorie "${entriesStore.formatCategory(
          category
        )}" könnte dich aufmuntern.`,
      })
    }
  })

  // If no category-based recommendations, suggest random positive entries
  if (recommendations.length === 0) {
    const allPositiveEntries = entries.value.filter(
      (entry) => entry.mood_score >= 4
    )
    if (allPositiveEntries.length > 0) {
      const randomEntry =
        allPositiveEntries[
          Math.floor(Math.random() * allPositiveEntries.length)
        ]
      recommendations.push({
        category: randomEntry.category,
        entry: randomEntry,
        reason: 'Ein positiver Moment, der dich inspirieren könnte.',
      })
    }
  }

  return recommendations.slice(0, 3) // Limit to 3 recommendations
})

// Chart Data
const moodTrendData = computed(() => {
  const sortedEntries = [...entries.value].sort(
    (a, b) => new Date(a.date) - new Date(b.date)
  )
  return {
    labels: sortedEntries.map((entry) =>
      new Date(entry.date).toLocaleDateString('de-DE')
    ),
    datasets: [
      {
        label: 'Stimmung',
        data: sortedEntries.map((entry) => entry.mood_score),
        borderColor: '#4a90e2',
        backgroundColor: 'rgba(74, 144, 226, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  }
})

const moodTrendOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      min: 1,
      max: 5,
      ticks: {
        stepSize: 1,
        callback: (value) => value + ' ' + getMoodEmoji(value),
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
    title: {
      display: true,
      text: 'Stimmungsverlauf über Zeit',
      color: 'var(--text-color)',
    },
    legend: {
      labels: {
        color: 'var(--text-color)',
      },
    },
  },
}

const moodDistributionData = computed(() => {
  const moodCounts = entries.value.reduce((acc, entry) => {
    acc[entry.mood_score] = (acc[entry.mood_score] || 0) + 1
    return acc
  }, {})

  return {
    labels: [1, 2, 3, 4, 5].map((score) => score + ' ' + getMoodEmoji(score)),
    datasets: [
      {
        data: [1, 2, 3, 4, 5].map((score) => moodCounts[score] || 0),
        backgroundColor: [
          '#e74c3c',
          '#e67e22',
          '#f1c40f',
          '#2ecc71',
          '#3498db',
        ],
      },
    ],
  }
})

const moodDistributionOptions = {
  responsive: true,
  plugins: {
    title: {
      display: true,
      text: 'Verteilung der Stimmungen',
      color: 'var(--text-color)',
    },
    legend: {
      labels: {
        color: 'var(--text-color)',
      },
    },
  },
}

const categoryDistributionData = computed(() => {
  const categoryCounts = entries.value.reduce((acc, entry) => {
    acc[entry.category] = (acc[entry.category] || 0) + 1
    return acc
  }, {})

  const categories = {
    work: 'Arbeit',
    family: 'Familie',
    health: 'Gesundheit',
    social: 'Soziales',
    personal: 'Persönlich',
    general: 'Allgemein',
  }

  return {
    labels: Object.keys(categories).map((key) => categories[key]),
    datasets: [
      {
        data: Object.keys(categories).map((key) => categoryCounts[key] || 0),
        backgroundColor: [
          '#e67e22',
          '#3498db',
          '#2ecc71',
          '#9b59b6',
          '#f1c40f',
          '#95a5a6',
        ],
      },
    ],
  }
})

const categoryDistributionOptions = {
  responsive: true,
  plugins: {
    title: {
      display: true,
      text: 'Verteilung nach Kategorien',
      color: 'var(--text-color)',
    },
    legend: {
      labels: {
        color: 'var(--text-color)',
      },
    },
  },
}

function getMoodEmoji(score) {
  return entriesStore.getMoodEmoji(score)
}

onMounted(async () => {
  try {
    entries.value = await entriesStore.fetchEntries()
  } catch (e) {
    error.value = 'Fehler beim Laden der Daten'
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  align-items: center;
  justify-content: space-between;
}

.tab-buttons {
  display: flex;
  gap: 10px;
}

.loading,
.error {
  text-align: center;
  padding: 20px;
  color: #666;
}

.error {
  color: var(--error-color);
}

.dashboard {
  background: var(--card-background);
  padding: 20px;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-top: 20px;
}

.chart-container {
  background: var(--card-background);
  padding: 20px;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  position: relative;
  height: 300px;
}

.chart-container h3 {
  color: var(--text-color);
  margin-bottom: 15px;
  font-size: 1.1rem;
}

.stats-container {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background: var(--card-background);
  padding: 20px;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  text-align: center;
  transition: transform 0.3s ease;
  border-top: 3px solid transparent;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-card.positive {
  border-top-color: var(--success-color);
}

.stat-card.negative {
  border-top-color: var(--error-color);
}

.stat-card h4 {
  color: var(--text-color);
  font-size: 0.9rem;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary-color);
}

.category-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  font-size: 1.2rem;
}

.category-name {
  font-size: 1rem;
  color: var(--text-color);
}

.category-score {
  display: flex;
  align-items: center;
  gap: 5px;
}

.mood-boost {
  grid-column: 1 / -1;
}

.recommendations {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 15px;
}

.recommendation-card {
  background: var(--card-background);
  border-radius: var(--border-radius);
  padding: 15px;
  border-left: 4px solid var(--primary-color);
  transition: transform 0.3s ease;
  box-shadow: var(--box-shadow);
}

.recommendation-card:hover {
  transform: translateY(-2px);
}

.recommendation-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.mood-emoji {
  font-size: 1.2rem;
}

.category-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--card-background);
}

.entry-date {
  font-size: 0.8rem;
  color: var(--text-color);
  opacity: 0.7;
  margin-left: auto;
}

.recommendation-content {
  font-size: 0.9rem;
  line-height: 1.5;
  margin-bottom: 10px;
  color: var(--text-color);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.recommendation-reason {
  font-size: 0.8rem;
  color: var(--text-color);
  opacity: 0.7;
  font-style: italic;
  border-top: 1px solid var(--border-color);
  padding-top: 10px;
}

@media (max-width: 768px) {
  .tabs {
    display: none;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .stats-container {
    grid-template-columns: 1fr;
  }

  .stat-card {
    padding: 15px;
  }

  .stat-value {
    font-size: 1.5rem;
  }

  .recommendations {
    grid-template-columns: 1fr;
  }

  .chart-container {
    height: 400px;
    margin-bottom: 30px;
  }
}
</style>
