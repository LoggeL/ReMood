<template>
  <div
    class="entry"
    :class="{
      private: entry.is_encrypted,
      breakdown: entry.is_breakdown,
      'decryption-failed': entry.decryptionFailed,
      [`mood-${entry.mood_score}`]: true,
    }"
  >
    <div class="entry-header">
      <span class="mood-emoji">{{ getMoodEmoji(entry.mood_score) }}</span>
      <span class="entry-date">{{ formatDate(entry.date) }}</span>
      <span
        class="category-badge"
        :class="entry.category"
        :style="{ backgroundColor: getCategoryColor(entry.category) }"
      >
        {{ formatCategory(entry.category) }}
      </span>
      <span v-if="entry.is_breakdown" class="breakdown-badge"> Breakdown </span>
      <button
        v-if="isOwnEntry"
        @click="editEntry"
        class="edit-btn"
        title="Eintrag bearbeiten"
      >
        ✏️
      </button>
    </div>
    <div v-if="entry.decryption_failed" class="decryption-error">
      <div class="error-message">
        <span class="error-icon">⚠️</span>
        Entschlüsselung fehlgeschlagen
      </div>
      <div class="error-details">
        Bitte melden Sie sich erneut an, um den Eintrag zu lesen.
      </div>
      <button @click="handleRelogin" class="relogin-btn">
        Erneut anmelden
      </button>
    </div>
    <div v-else class="entry-content">{{ entry.content }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useEntriesStore } from '../stores/entries'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const router = useRouter()
const entriesStore = useEntriesStore()
const authStore = useAuthStore()

const props = defineProps({
  entry: {
    type: Object,
    required: true,
  },
})

const isOwnEntry = computed(() => {
  return authStore.username === props.entry.username
})

function editEntry() {
  router.push({
    name: 'edit-entry',
    params: { id: props.entry.id },
  })
}

function handleRelogin() {
  authStore.logout()
  router.push({ name: 'login' })
}

function getMoodEmoji(score) {
  return entriesStore.getMoodEmoji(score)
}

function formatCategory(category) {
  return entriesStore.formatCategory(category)
}

function getCategoryColor(category) {
  return entriesStore.getCategoryColor(category)
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<style scoped>
.entry {
  background: var(--card-background);
  padding: 20px;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  transition: all 0.3s ease;
  position: relative;
}

.entry.private .entry-content {
  filter: blur(5px);
  transition: filter 0.3s ease;
}

.entry.private:hover .entry-content {
  filter: blur(0);
}

.entry.private {
  position: relative;
}

.entry.private::before {
  content: '🔒';
  position: absolute;
  top: 10px;
  right: 45px;
  font-size: 1.2rem;
  opacity: 0.7;
}

.entry.breakdown {
  border-left: 4px solid var(--error-color);
}

.entry-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.mood-emoji {
  font-size: 1.5rem;
}

.entry-date {
  color: var(--text-color);
  opacity: 0.7;
  font-size: 0.9rem;
}

.category-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  color: var(--card-background);
  opacity: 0.8;
}

.breakdown-badge {
  background: var(--error-color);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
}

.entry-content {
  white-space: pre-wrap;
  line-height: 1.5;
  color: var(--text-color);
}

.entry.decryption-failed {
  border: 1px solid var(--error-color);
  background: var(--card-background);
}

.decryption-error {
  color: var(--error-color);
}

.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  margin-bottom: 8px;
}

.error-icon {
  font-size: 1.2rem;
}

.error-details {
  font-size: 0.9rem;
  color: var(--text-color);
  opacity: 0.7;
  white-space: pre-wrap;
  line-height: 1.5;
}

.edit-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: var(--border-radius);
  transition: all 0.3s;
  margin-left: auto;
  opacity: 0;
  position: absolute;
  top: 10px;
  right: 10px;
  color: var(--text-color);
}

.entry:hover .edit-btn {
  opacity: 1;
}

.edit-btn:hover {
  background: var(--hover-background);
  transform: scale(1.1);
}

.relogin-btn {
  background: var(--primary-color);
  color: white;
  border: none;
  font-size: 0.9rem;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: var(--border-radius);
  transition: all 0.3s;
  margin-left: auto;
  margin-top: 8px;
}

.relogin-btn:hover {
  background: #357abd;
  transform: scale(1.05);
}
</style>
