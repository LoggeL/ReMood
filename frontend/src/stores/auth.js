import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useEntriesStore } from './entries'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token'))
  const username = ref(localStorage.getItem('username'))
  const entriesStore = useEntriesStore()

  const isAuthenticated = computed(() => !!token.value)

  async function login(credentials) {
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)

    try {
      const response = await fetch('/token', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Anmeldung fehlgeschlagen')
      }

      const data = await response.json()
      token.value = data.access_token
      username.value = credentials.username
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('username', credentials.username)

      // Generate and store encryption key from password
      const key = await generateKeyFromPassword(credentials.password)
      localStorage.setItem('encryption_key', key)

      // Reload entries after successful login
      await entriesStore.reloadEntries()

      return true
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  }

  async function register(credentials) {
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)

    try {
      const response = await fetch('/register', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Registrierung fehlgeschlagen')
      }

      return true
    } catch (error) {
      console.error('Register error:', error)
      throw error
    }
  }

  function logout() {
    token.value = null
    username.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('encryption_key')
    entriesStore.entries.value = []
  }

  return {
    token,
    username,
    isAuthenticated,
    login,
    register,
    logout,
  }
})

// Helper function to generate key from password
async function generateKeyFromPassword(password) {
  // Convert password to key using Web Crypto API
  const encoder = new TextEncoder()
  const data = encoder.encode(password)
  const hash = await crypto.subtle.digest('SHA-256', data)
  const key = btoa(String.fromCharCode(...new Uint8Array(hash)))
  return key
}
