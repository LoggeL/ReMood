<template>
  <div id="entries-container">
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
          <div class="chart-wrapper">
            <Line
              v-if="chartData.mood"
              :data="chartData.mood"
              :options="chartOptions.mood"
            />
          </div>
        </div>
        <div class="chart-container">
          <h3>Stimmungsverteilung</h3>
          <div class="chart-wrapper">
            <Doughnut
              v-if="chartData.distribution"
              :data="chartData.distribution"
              :options="chartOptions.distribution"
            />
          </div>
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
          <div class="chart-wrapper">
            <Doughnut
              v-if="chartData.categories"
              :data="chartData.categories"
              :options="chartOptions.categories"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Line, Doughnut } from 'vue-chartjs'
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
  ArcElement,
  TimeScale,
} from 'chart.js'
import 'chartjs-adapter-date-fns'
import { de } from 'date-fns/locale'
import { useEntriesStore } from '../stores/entries'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  ArcElement,
  TimeScale
)

// Set German locale for date-fns
ChartJS.defaults.locale = de

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

// Chart Data
const chartData = computed(() => {
  const sortedEntries = [...entries.value].sort(
    (a, b) => new Date(a.date) - new Date(b.date)
  )

  // Mood trend data
  const moodData = {
    datasets: [
      {
        label: 'Stimmung',
        data: sortedEntries.map((entry) => ({
          x: new Date(entry.date),
          y: entry.mood_score,
        })),
        fill: true,
        borderColor: '#4a90e2',
        backgroundColor: 'rgba(74, 144, 226, 0.1)',
        tension: 0.4,
      },
    ],
  }

  // Mood distribution data
  const moodCounts = entries.value.reduce((acc, entry) => {
    acc[entry.mood_score] = (acc[entry.mood_score] || 0) + 1
    return acc
  }, {})

  const distributionData = {
    labels: [1, 2, 3, 4, 5].map((score) => `${score} ${getMoodEmoji(score)}`),
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

  // Category distribution data
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

  const colors = {
    work: '#e67e22',
    family: '#3498db',
    health: '#2ecc71',
    social: '#9b59b6',
    personal: '#f1c40f',
    general: '#95a5a6',
  }

  const categoryData = {
    labels: Object.keys(categories).map((key) => {
      const label = categories[key]
      if (key === categoryStats.value.best.category) {
        return `${label} 🌟`
      } else if (key === categoryStats.value.worst.category) {
        return `${label} ⚠️`
      }
      return label
    }),
    datasets: [
      {
        data: Object.keys(categories).map((key) => categoryCounts[key] || 0),
        backgroundColor: Object.keys(categories).map((key) => {
          if (key === categoryStats.value.best.category) {
            return '#2ecc71' // Success color for best category
          } else if (key === categoryStats.value.worst.category) {
            return '#e74c3c' // Error color for worst category
          }
          return colors[key]
        }),
        borderWidth: Object.keys(categories).map((key) =>
          key === categoryStats.value.best.category ||
          key === categoryStats.value.worst.category
            ? 2
            : 0
        ),
        borderColor: Object.keys(categories).map((key) =>
          key === categoryStats.value.best.category
            ? '#27ae60'
            : key === categoryStats.value.worst.category
            ? '#c0392b'
            : 'transparent'
        ),
      },
    ],
  }

  return {
    mood: moodData,
    distribution: distributionData,
    categories: categoryData,
  }
})

// Chart Options
const chartOptions = computed(() => ({
  mood: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: (context) => `${context.raw.y} ${getMoodEmoji(context.raw.y)}`,
          title: (context) => {
            const date = new Date(context[0].raw.x)
            return date.toLocaleDateString('de-DE', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })
          },
        },
      },
    },
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'day',
          displayFormats: {
            day: 'dd.MM.yy',
          },
        },
        ticks: {
          maxRotation: 45,
          minRotation: 45,
        },
      },
      y: {
        min: 1,
        max: 5,
        ticks: {
          stepSize: 1,
          callback: (value) => `${value} ${getMoodEmoji(value)}`,
        },
      },
    },
    animation: false,
  },
  distribution: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
    },
    animation: false,
  },
  categories: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right',
        labels: {
          font: {
            size: 12,
          },
          padding: 15,
          generateLabels: (chart) => {
            const data = chart.data
            if (data.labels.length && data.datasets.length) {
              return data.labels.map((label, i) => ({
                text: label,
                fillStyle: data.datasets[0].backgroundColor[i],
                strokeStyle: data.datasets[0].borderColor[i],
                lineWidth: data.datasets[0].borderWidth[i],
                hidden: false,
                index: i,
              }))
            }
            return []
          },
        },
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const value = context.raw || 0
            return `${value} Einträge`
          },
        },
      },
    },
    animation: false,
  },
}))

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
  height: 400px;
}

.chart-container h3 {
  color: var(--text-color);
  margin-bottom: 15px;
  font-size: 1.1rem;
}

.chart-wrapper {
  height: calc(100% - 45px); /* Container height minus header and padding */
  position: relative;
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
    height: 350px;
  }
}
</style>
