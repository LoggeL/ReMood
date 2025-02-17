<template>
  <div id="entries-container">
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
.loading,
.error {
  text-align: center;
  padding: 20px;
  color: #666;
}

.error {
  color: var(--error-color);
}
</style>
