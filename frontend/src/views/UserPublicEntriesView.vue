<template>
  <div id="entries-container">
    <div class="header">
      <button class="back-btn" @click="$router.back()">
        <span class="nav-icon">←</span> Zurück
      </button>
      <h2>Öffentliche Einträge von {{ username }}</h2>
    </div>

    <div v-if="isLoading" class="loading">Lade öffentliche Einträge...</div>
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    <div v-else-if="entries.length === 0" class="empty-state">
      Keine öffentlichen Einträge vorhanden
    </div>
    <EntryList v-else :entries="entries" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useEntriesStore } from '../stores/entries'
import EntryList from '../components/EntryList.vue'

const route = useRoute()
const entriesStore = useEntriesStore()
const entries = ref([])
const isLoading = ref(true)
const error = ref(null)
const username = ref(route.params.username)

onMounted(async () => {
  try {
    entries.value = await entriesStore.fetchUserPublicEntries(username.value)
  } catch (e) {
    error.value = e.message
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
.header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
}

.back-btn {
  background: none;
  color: var(--secondary-color);
  padding: 8px 16px;
  border: 1px solid var(--secondary-color);
  border-radius: var(--border-radius);
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.back-btn:hover {
  background: var(--secondary-color);
  color: white;
}

.loading,
.error,
.empty-state {
  text-align: center;
  padding: 20px;
  color: #666;
}

.error {
  color: var(--error-color);
}

.empty-state {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  padding: 40px;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>
