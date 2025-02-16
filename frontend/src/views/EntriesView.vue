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

    <div v-if="isLoading" class="loading">Lade Einträge...</div>
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    <EntryList v-else :entries="entries" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useEntriesStore } from '../stores/entries'
import EntryList from '../components/EntryList.vue'

const entriesStore = useEntriesStore()
const entries = ref([])
const isLoading = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    entries.value = await entriesStore.fetchEntries()
  } catch (e) {
    error.value = 'Fehler beim Laden der Einträge'
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

@media (max-width: 768px) {
  .tabs {
    display: none;
  }
}
</style>
