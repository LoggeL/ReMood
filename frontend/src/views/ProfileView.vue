<template>
  <div class="profile-container">
    <h2>Profil Einstellungen</h2>

    <div class="profile-section">
      <h3>Benutzerdaten</h3>
      <div class="user-info">
        <p><strong>Benutzername:</strong> {{ username }}</p>
        <p><strong>Mitglied seit:</strong> {{ formatDate(joinDate) }}</p>
        <p><strong>Anzahl Einträge:</strong> {{ totalEntries }}</p>
      </div>
      <button @click="logout" class="logout-btn">
        <span class="nav-icon">🚪</span> Abmelden
      </button>
    </div>

    <div class="profile-section">
      <h3>Datenexport</h3>
      <p class="section-description">
        Exportiere deine persönlichen Einträge als JSON-Datei. Die exportierten
        Daten enthalten alle deine Einträge, einschließlich der verschlüsselten
        Inhalte.
      </p>
      <div v-if="totalEntries === 0" class="empty-state">
        <div class="empty-icon">📝</div>
        <p>Du hast noch keine Einträge erstellt</p>
        <router-link to="/new" class="create-entry-btn">Ersten Eintrag erstellen</router-link>
      </div>
      <button v-else @click="exportData" :disabled="isExporting" class="export-btn">
        {{ isExporting ? 'Exportiere...' : 'Daten exportieren' }}
      </button>
    </div>

    <div class="profile-section danger-zone">
      <h3>Gefahrenzone</h3>
      <p class="section-description">
        Achtung: Diese Aktionen können nicht rückgängig gemacht werden.
      </p>
      <button @click="confirmDeleteAccount" class="delete-btn">
        Account löschen
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useEntriesStore } from '../stores/entries'

const router = useRouter()
const authStore = useAuthStore()
const entriesStore = useEntriesStore()

const username = computed(() => authStore.username)
const joinDate = ref(new Date()) // This should come from the backend
const totalEntries = computed(() => entriesStore.entries.length)
const isExporting = ref(false)

function formatDate(date) {
  return date.toLocaleDateString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

async function exportData() {
  isExporting.value = true
  try {
    // Fetch all entries if not already loaded
    if (entriesStore.entries.length === 0) {
      await entriesStore.fetchEntries()
    }

    const exportData = {
      username: username.value,
      exportDate: new Date().toISOString(),
      entries: entriesStore.entries,
    }

    // Create and download file
    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json',
    })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `remood-export-${
      new Date().toISOString().split('T')[0]
    }.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  } catch (error) {
    alert('Fehler beim Exportieren der Daten')
  } finally {
    isExporting.value = false
  }
}

function confirmDeleteAccount() {
  const confirmed = window.confirm(
    'Bist du sicher, dass du deinen Account löschen möchtest? Diese Aktion kann nicht rückgängig gemacht werden!'
  )
  if (confirmed) {
    // TODO: Implement account deletion
    alert('Diese Funktion wird in Kürze verfügbar sein.')
  }
}

function logout() {
  authStore.logout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.profile-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.profile-section {
  background: white;
  padding: 25px;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  margin-bottom: 30px;
}

.profile-section h3 {
  color: var(--secondary-color);
  margin-bottom: 15px;
  font-size: 1.2rem;
}

.section-description {
  color: var(--text-color);
  opacity: 0.7;
  margin-bottom: 20px;
  font-size: 0.9rem;
  line-height: 1.5;
}

.user-info {
  display: grid;
  gap: 10px;
}

.user-info p {
  color: var(--text-color);
  opacity: 0.7;
}

.user-info strong {
  color: var(--text-color);
}

.export-btn {
  background-color: var(--primary-color);
  min-width: 200px;
}

.export-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.danger-zone {
  border: 1px solid #ffebee;
}

.danger-zone h3 {
  color: var(--error-color);
}

.delete-btn {
  background-color: var(--error-color);
  min-width: 200px;
}

.delete-btn:hover {
  background-color: #c0392b;
}

.logout-btn {
  margin-top: 20px;
  background-color: var(--error-color);
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  justify-content: center;
}

.logout-btn:hover {
  background-color: #c0392b;
  transform: translateY(-1px);
}

.empty-state {
  text-align: center;
  padding: 20px;
  background: var(--card-background);
  border-radius: var(--border-radius);
}

.empty-icon {
  font-size: 2rem;
  margin-bottom: 10px;
}

.empty-state p {
  color: var(--text-color);
  opacity: 0.7;
  margin-bottom: 15px;
}

.create-entry-btn {
  display: inline-block;
  background: var(--primary-color);
  color: white;
  padding: 10px 20px;
  border-radius: var(--border-radius);
  text-decoration: none;
  transition: all 0.3s;
}

.create-entry-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

@media (max-width: 768px) {
  .profile-container {
    padding: 10px;
  }

  .profile-section {
    padding: 15px;
  }
}
</style>
