<template>
  <div class="auth-container">
    <div v-if="!isRegistering" class="form-container">
      <h2>Anmelden</h2>
      <form @submit.prevent="handleLogin">
        <input
          v-model="loginForm.username"
          type="text"
          placeholder="Benutzername"
          required
        />
        <input
          v-model="loginForm.password"
          type="password"
          placeholder="Passwort"
          required
        />
        <button type="submit" :disabled="isLoading">Anmelden</button>
      </form>
      <p>
        Noch kein Konto?
        <a href="#" @click.prevent="toggleForm">Registrieren</a>
      </p>
    </div>

    <div v-else class="form-container">
      <h2>Registrieren</h2>
      <form @submit.prevent="handleRegister">
        <input
          v-model="registerForm.username"
          type="text"
          placeholder="Benutzername"
          required
        />
        <input
          v-model="registerForm.password"
          type="password"
          placeholder="Passwort"
          required
        />
        <input
          v-model="registerForm.confirmPassword"
          type="password"
          placeholder="Passwort bestätigen"
          required
        />
        <button type="submit" :disabled="isLoading">Registrieren</button>
      </form>
      <p>
        Bereits registriert?
        <a href="#" @click.prevent="toggleForm">Anmelden</a>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isRegistering = ref(false)
const isLoading = ref(false)

const loginForm = ref({
  username: '',
  password: '',
})

const registerForm = ref({
  username: '',
  password: '',
  confirmPassword: '',
})

const toggleForm = () => {
  isRegistering.value = !isRegistering.value
  loginForm.value = { username: '', password: '' }
  registerForm.value = { username: '', password: '', confirmPassword: '' }
}

const handleLogin = async () => {
  isLoading.value = true
  try {
    await authStore.login(loginForm.value)
    router.push({ name: 'entries' })
  } catch (error) {
    alert(error.message)
  } finally {
    isLoading.value = false
  }
}

const handleRegister = async () => {
  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    alert('Passwörter stimmen nicht überein!')
    return
  }

  isLoading.value = true
  try {
    await authStore.register({
      username: registerForm.value.username,
      password: registerForm.value.password,
    })
    alert('Registrierung erfolgreich! Bitte melde dich an.')
    isRegistering.value = false
  } catch (error) {
    alert(error.message)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.auth-container {
  max-width: 400px;
  margin: 0 auto;
}

.form-container {
  background: var(--card-background);
  padding: 30px;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
}

.form-container h2 {
  margin-bottom: 20px;
  color: var(--secondary-color);
}

form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

input {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: var(--border-radius);
  font-size: 16px;
}

button {
  background-color: var(--primary-color);
  color: white;
  padding: 12px;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

button:hover:not(:disabled) {
  background-color: #357abd;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

p {
  margin-top: 20px;
  text-align: center;
  color: #666;
}

a {
  color: var(--primary-color);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}
</style>
