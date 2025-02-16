import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './auth'
import { useRouter } from 'vue-router'
import { encryptText, decryptText } from '../utils/encryption'

export const useEntriesStore = defineStore('entries', () => {
  const entries = ref([])
  const publicEntries = ref([])
  const authStore = useAuthStore()
  const router = useRouter()

  function handleUnauthorized() {
    authStore.logout()
    router.push({ name: 'login' })
  }

  async function fetchEntries() {
    try {
      const response = await fetch('/api/entries', {
        headers: {
          Authorization: `Bearer ${authStore.token}`,
        },
      })

      if (response.status === 401) {
        handleUnauthorized()
        throw new Error('Nicht autorisiert')
      }

      if (!response.ok) {
        throw new Error('Fehler beim Laden der Einträge')
      }

      const data = await response.json()

      // Process entries sequentially to maintain order
      entries.value = await Promise.all(
        data.map(async (entry) => {
          // If the entry is encrypted and belongs to the current user, try to decrypt it
          if (entry.is_encrypted && entry.username === authStore.username) {
            try {
              const key = localStorage.getItem('encryption_key')
              if (key) {
                entry.content = await decryptText(entry.content, key)
                entry.decryption_failed = false
              } else {
                entry.decryption_failed = true
              }
            } catch (error) {
              console.error('Decryption failed:', error)
              entry.decryption_failed = true
              entry.content =
                'Entschlüsselung fehlgeschlagen. Bitte melden Sie sich erneut an.'
            }
          }
          return entry
        })
      )

      return entries.value
    } catch (error) {
      console.error('Error fetching entries:', error)
      throw error
    }
  }

  async function reloadEntries() {
    entries.value = []
    return await fetchEntries()
  }

  async function fetchPublicEntries() {
    try {
      const response = await fetch('/api/public-entries')

      if (!response.ok) {
        throw new Error('Fehler beim Laden der öffentlichen Einträge')
      }

      publicEntries.value = await response.json()
      return publicEntries.value
    } catch (error) {
      console.error('Error fetching public entries:', error)
      throw error
    }
  }

  async function fetchUserPublicEntries(username) {
    try {
      const response = await fetch(`/api/users/${username}/public-entries`)

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Benutzer nicht gefunden')
        }
        throw new Error('Fehler beim Laden der öffentlichen Einträge')
      }

      const entries = await response.json()
      return entries
    } catch (error) {
      console.error('Error fetching user public entries:', error)
      throw error
    }
  }

  async function createEntry(entryData) {
    try {
      // If entry is private, encrypt the content before sending
      if (entryData.is_encrypted) {
        const key = localStorage.getItem('encryption_key')
        if (!key) {
          throw new Error('Encryption key not found. Please log in again.')
        }
        entryData.content = await encryptText(entryData.content, key)
      }

      const response = await fetch('/api/entries', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authStore.token}`,
        },
        body: JSON.stringify(entryData),
      })

      if (response.status === 401) {
        handleUnauthorized()
        throw new Error('Nicht autorisiert')
      }

      if (!response.ok) {
        throw new Error('Fehler beim Speichern des Eintrags')
      }

      const newEntry = await response.json()

      // If entry is private, decrypt it before adding to local state
      if (newEntry.is_encrypted) {
        try {
          const key = localStorage.getItem('encryption_key')
          if (key) {
            newEntry.content = await decryptText(newEntry.content, key)
            newEntry.decryption_failed = false
          } else {
            newEntry.decryption_failed = true
          }
        } catch (error) {
          console.error('Decryption failed:', error)
          newEntry.decryption_failed = true
          newEntry.content =
            'Entschlüsselung fehlgeschlagen. Bitte melden Sie sich erneut an.'
        }
      }

      entries.value.push(newEntry)

      if (!entryData.is_encrypted) {
        publicEntries.value.push(newEntry)
      }

      return newEntry
    } catch (error) {
      console.error('Error creating entry:', error)
      throw error
    }
  }

  async function getEntry(id) {
    // First try to find in local state
    let entry = entries.value.find((e) => e.id === parseInt(id))

    // If not found, fetch from server
    if (!entry) {
      try {
        const response = await fetch(`/api/entries/${id}`, {
          headers: {
            Authorization: `Bearer ${authStore.token}`,
          },
        })

        if (response.status === 401) {
          handleUnauthorized()
          throw new Error('Nicht autorisiert')
        }

        if (!response.ok) {
          throw new Error('Eintrag nicht gefunden')
        }

        entry = await response.json()
      } catch (error) {
        console.error('Error fetching entry:', error)
        throw error
      }
    }

    return entry
  }

  async function updateEntry(id, entryData) {
    try {
      // If entry is private, encrypt the content before sending
      if (entryData.is_encrypted) {
        const key = localStorage.getItem('encryption_key')
        if (!key) {
          throw new Error('Encryption key not found. Please log in again.')
        }
        entryData.content = await encryptText(entryData.content, key)
      }

      const response = await fetch(`/api/entries/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authStore.token}`,
        },
        body: JSON.stringify(entryData),
      })

      if (response.status === 401) {
        handleUnauthorized()
        throw new Error('Nicht autorisiert')
      }

      if (!response.ok) {
        throw new Error('Fehler beim Aktualisieren des Eintrags')
      }

      const updatedEntry = await response.json()

      // If entry is private, decrypt it before updating local state
      if (updatedEntry.is_encrypted) {
        try {
          const key = localStorage.getItem('encryption_key')
          if (key) {
            updatedEntry.content = await decryptText(updatedEntry.content, key)
            updatedEntry.decryption_failed = false
          } else {
            updatedEntry.decryption_failed = true
          }
        } catch (error) {
          console.error('Decryption failed:', error)
          updatedEntry.decryption_failed = true
          updatedEntry.content =
            'Entschlüsselung fehlgeschlagen. Bitte melden Sie sich erneut an.'
        }
      }

      // Update the entry in our local state
      const index = entries.value.findIndex((e) => e.id === parseInt(id))
      if (index !== -1) {
        entries.value[index] = updatedEntry
      }

      return updatedEntry
    } catch (error) {
      console.error('Error updating entry:', error)
      throw error
    }
  }

  function getMoodEmoji(score) {
    const emojis = ['😢', '😕', '😐', '🙂', '😊']
    return emojis[score - 1]
  }

  function formatCategory(category) {
    const categories = {
      work: 'Arbeit',
      family: 'Familie',
      health: 'Gesundheit',
      social: 'Soziales',
      personal: 'Persönlich',
      general: 'Allgemein',
    }
    return categories[category] || 'Allgemein'
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

  return {
    entries,
    publicEntries,
    fetchEntries,
    reloadEntries,
    fetchPublicEntries,
    fetchUserPublicEntries,
    createEntry,
    getEntry,
    updateEntry,
    getMoodEmoji,
    formatCategory,
    getCategoryColor,
  }
})
