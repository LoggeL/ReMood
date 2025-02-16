import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    isDarkMode: localStorage.getItem('darkMode') === 'true'
  }),
  
  actions: {
    toggleDarkMode() {
      this.isDarkMode = !this.isDarkMode
      localStorage.setItem('darkMode', this.isDarkMode)
      
      // Apply theme to document
      if (this.isDarkMode) {
        document.documentElement.classList.add('dark-theme')
      } else {
        document.documentElement.classList.remove('dark-theme')
      }
    },
    
    initializeTheme() {
      // Apply theme on app start
      if (this.isDarkMode) {
        document.documentElement.classList.add('dark-theme')
      }
    }
  }
}) 