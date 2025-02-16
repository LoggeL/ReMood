<template>
  <div id="mood-entry">
    <div class="header-actions">
      <button class="back-btn" @click="goBack">
        <span class="nav-icon">←</span> Zurück
      </button>
      <h2>{{ pageTitle }}</h2>
    </div>

    <div v-if="isLoading" class="loading">
      {{ isEditMode ? 'Lade Eintrag...' : 'Initialisiere...' }}
    </div>
    <div v-else>
      <div class="mood-selector">
        <div class="mood-icons">
          <button
            v-for="score in 5"
            :key="score"
            class="mood-btn"
            :class="{ selected: currentMood === score }"
            @click="selectMood(score)"
            :title="getMoodLabel(score)"
          >
            {{ getMoodEmoji(score) }}
          </button>
        </div>
        <div v-if="showMoodError" class="error-message">
          Bitte wähle eine Stimmung aus
        </div>
      </div>

      <form @submit.prevent="saveEntry">
        <div class="form-group">
          <label for="date">Datum:</label>
          <input
            v-model="form.date"
            type="datetime-local"
            id="date"
            :max="maxDate"
            required
            :class="{ error: showDateError }"
          />
          <div v-if="showDateError" class="error-message">
            Bitte wähle ein gültiges Datum aus
          </div>
        </div>

        <div class="form-group">
          <label for="content">Deine Gedanken:</label>
          <textarea
            v-model="form.content"
            id="content"
            rows="4"
            required
            :class="{ error: showContentError }"
          ></textarea>
          <div v-if="showContentError" class="error-message">
            Bitte teile deine Gedanken mit
          </div>
        </div>

        <div class="form-group category-group">
          <label for="category">Kategorie:</label>
          <select
            v-model="form.category"
            id="category"
            class="category-select"
            required
          >
            <option value="general">🔵 Allgemein</option>
            <option value="work">💼 Arbeit</option>
            <option value="family">👨‍👩‍👧‍👦 Familie</option>
            <option value="health">❤️ Gesundheit</option>
            <option value="social">🤝 Soziales</option>
            <option value="personal">💭 Persönlich</option>
          </select>
        </div>

        <div class="form-options">
          <div class="checkbox-group">
            <input
              v-model="form.is_breakdown"
              type="checkbox"
              id="is_breakdown"
            />
            <label for="is_breakdown">Breakdown-Moment</label>
          </div>
          <div class="checkbox-group">
            <input v-model="form.is_public" type="checkbox" id="is_public" />
            <label for="is_public">Öffentlich teilen</label>
          </div>
        </div>

        <div class="form-actions">
          <button type="button" class="cancel-btn" @click="goBack">
            Abbrechen
          </button>
          <button type="submit" :disabled="isLoading" class="save-btn">
            {{ isLoading ? 'Speichere...' : 'Speichern' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useEntriesStore } from '../stores/entries'

const router = useRouter()
const route = useRoute()
const entriesStore = useEntriesStore()

const currentMood = ref(3)
const isLoading = ref(false)
const showMoodError = ref(false)
const showDateError = ref(false)
const showContentError = ref(false)

const isEditMode = computed(() => route.name === 'edit-entry')
const pageTitle = computed(() =>
  isEditMode.value ? 'Eintrag bearbeiten' : 'Wie fühlst du dich heute?'
)

const maxDate = computed(() => {
  const now = new Date()
  return now.toISOString().slice(0, 16)
})

const form = ref({
  content: '',
  category: 'general',
  is_breakdown: false,
  is_public: false,
  date: new Date().toISOString().slice(0, 16), // Format: YYYY-MM-DDThh:mm
})

async function loadEntry() {
  if (!isEditMode.value) return

  isLoading.value = true
  try {
    const entry = await entriesStore.getEntry(route.params.id)
    if (!entry) throw new Error('Eintrag nicht gefunden')

    currentMood.value = entry.mood_score
    form.value = {
      content: entry.content,
      category: entry.category,
      is_breakdown: entry.is_breakdown,
      is_public: !entry.is_encrypted,
      date: new Date(entry.date).toISOString().slice(0, 16),
    }
  } catch (error) {
    alert(error.message)
    router.push({ name: 'entries' })
  } finally {
    isLoading.value = false
  }
}

onMounted(loadEntry)

function selectMood(score) {
  currentMood.value = score
  showMoodError.value = false
}

function getMoodEmoji(score) {
  return entriesStore.getMoodEmoji(score)
}

function getMoodLabel(score) {
  const labels = {
    1: 'Sehr schlecht',
    2: 'Schlecht',
    3: 'Neutral',
    4: 'Gut',
    5: 'Sehr gut',
  }
  return labels[score]
}

function goBack() {
  router.push({ name: 'entries' })
}

function validateForm() {
  let isValid = true

  showMoodError.value = !currentMood.value
  showDateError.value = !form.value.date
  showContentError.value = !form.value.content.trim()

  if (showMoodError.value || showDateError.value || showContentError.value) {
    isValid = false
  }

  return isValid
}

async function saveEntry() {
  if (!validateForm()) {
    return
  }

  isLoading.value = true
  try {
    const entryData = {
      mood_score: currentMood.value,
      content: form.value.content,
      category: form.value.category,
      is_encrypted: !form.value.is_public,
      is_breakdown: form.value.is_breakdown,
      date: new Date(form.value.date).toISOString(),
    }

    if (isEditMode.value) {
      await entriesStore.updateEntry(route.params.id, entryData)
    } else {
      await entriesStore.createEntry(entryData)
    }

    router.push({ name: 'entries' })
  } catch (error) {
    alert(error.message)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
}

.back-btn {
  background: none;
  color: var(--text-color);
  padding: 8px 16px;
  border: 1px solid var(--text-color);
  border-radius: var(--border-radius);
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.back-btn:hover {
  background: var(--text-color);
  color: var(--card-background);
}

.mood-selector {
  margin: 30px 0;
  background: var(--card-background);
  padding: 20px;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  transition: background-color 0.3s ease;
}

.mood-icons {
  display: flex;
  justify-content: space-between;
  max-width: 400px;
  margin: 0 auto;
  position: relative;
}

.mood-icons::before {
  content: '';
  position: absolute;
  left: 10%;
  right: 10%;
  top: 50%;
  height: 2px;
  background: linear-gradient(to right, #e74c3c, #f1c40f, #2ecc71);
  z-index: 1;
}

.mood-btn {
  font-size: 2rem;
  background: var(--card-background);
  border: 2px solid transparent;
  padding: 10px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  z-index: 2;
  border-radius: 50%;
}

.mood-btn:hover {
  transform: scale(1.2);
  background: var(--card-background);
}

.mood-btn.selected {
  border-color: var(--primary-color);
  transform: scale(1.2);
  box-shadow: 0 0 10px rgba(74, 144, 226, 0.3);
}

.form-group {
  margin-bottom: 20px;
  width: 100%;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-color);
  transition: color 0.3s ease;
}

.form-group textarea,
.form-group select,
.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 16px;
  background: var(--input-background);
  color: var(--text-color);
  transition: all 0.3s ease;
}

.form-group textarea {
  min-height: 120px;
  resize: vertical;
}

.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
}

.form-options {
  display: flex;
  gap: 20px;
  margin: 20px 0;
}

.checkbox-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.checkbox-group label {
  color: var(--text-color);
  transition: color 0.3s ease;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 30px;
}

.cancel-btn {
  background: none;
  color: var(--text-color);
  border: 1px solid var(--text-color);
}

.cancel-btn:hover {
  background: var(--text-color);
  color: var(--card-background);
}

.save-btn {
  background: var(--primary-color);
  color: white;
  min-width: 120px;
  transition: all 0.3s ease;
}

.save-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.save-btn:hover:not(:disabled) {
  background: #357abd;
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  .mood-btn {
    font-size: 1.5rem;
  }

  .form-options {
    flex-direction: column;
    gap: 10px;
  }

  .form-actions {
    flex-direction: column-reverse;
  }

  .form-actions button {
    width: 100%;
  }
}

.loading {
  text-align: center;
  padding: 40px;
  color: var(--text-color);
  background: var(--card-background);
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  margin: 20px 0;
  transition: all 0.3s ease;
}

.error-message {
  color: var(--error-color);
  font-size: 0.9rem;
  margin-top: 5px;
}

.error {
  border-color: var(--error-color) !important;
}

.error:focus {
  box-shadow: 0 0 0 2px rgba(231, 76, 60, 0.2) !important;
}

h2 {
  color: var(--text-color);
  transition: color 0.3s ease;
}
</style>
