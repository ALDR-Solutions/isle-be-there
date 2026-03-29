import { createRouter, createWebHistory } from 'vue-router'
import { APP_NAME } from '@/app/config'
import { pinia } from '@/app/pinia'
import { routes } from '@/router/routes'
import { useAuthStore } from '@/stores/auth'
import { getUserRole, hasAnyRole } from '@/utils/auth'

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore(pinia)

  if (!authStore.initialized) {
    await authStore.initialize()
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return { name: 'Login', query: { redirect: to.fullPath } }
  }

  if (to.meta.guestOnly && authStore.isAuthenticated) {
    const role = getUserRole(authStore.user)

    if (role === 'admin') return { name: 'AdminHome' }
    if (role === 'business') return { name: 'BusinessHome' }
    return { name: 'Home' }
  }

  if (to.meta.allowedRoles?.length && !hasAnyRole(authStore.user, to.meta.allowedRoles)) {
    const role = getUserRole(authStore.user)

    if (role === 'admin') return { name: 'AdminHome' }
    if (role === 'business') return { name: 'BusinessHome' }
    if (role === 'user') return { name: 'Home' }
    return { name: 'Login', query: { redirect: to.fullPath } }
  }

  return true
})

router.afterEach((to) => {
  const pageTitle = to.meta.pageTitle ? `${to.meta.pageTitle} | ${APP_NAME}` : APP_NAME
  document.title = pageTitle
})

export default router
