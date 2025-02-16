import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'entries',
      component: () => import('../views/EntriesView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/feed',
      name: 'feed',
      component: () => import('../views/FeedView.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/share/:username',
      name: 'shared-feed',
      component: () => import('../views/FeedView.vue'),
      meta: { requiresAuth: false },
      props: true,
    },
    {
      path: '/new',
      name: 'new-entry',
      component: () => import('../views/NewEntryView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/edit/:id',
      name: 'edit-entry',
      component: () => import('../views/NewEntryView.vue'),
      meta: { requiresAuth: true },
      props: true,
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { requiresAuth: false },
    },
  ],
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login' })
  } else if (to.name === 'login' && authStore.isAuthenticated) {
    next({ name: 'entries' })
  } else {
    next()
  }
})

export default router
