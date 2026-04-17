import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { pinia } from './pinia'
import Home from './views/Home.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { role: 'user' }
  },

  {
    path: '/business',
    name: 'BusinessHome',
    component: () => import('./views/BusinessHome.vue'),
    meta: { requiresAuth: true, layout: 'business', role: 'business' }
  },

  {
    path: '/business/profile',
    name: 'BusinessProfile',
    component: () => import('./views/BusinessProfile.vue'),
    meta: { requiresAuth: true, layout: 'business', role: 'business'}
  },

  {
    path: '/business/account',
    name: 'BusinessAccount',
    component: () => import('./views/BusinessAccount.vue'),
    meta: { requiresAuth: true, layout: 'business', role: 'business' }
  },

  {
    path: '/business/employees',
    name: 'BusinessEmployees',
    component: () => import('./views/BusinessEmployees.vue'),
    meta: { requiresAuth: true, layout: 'business', role: 'business' }
  },

  {
    path: '/employee',
    name: 'EmployeeHome',
    component: () => import('./views/EmployeeHome.vue'),
    meta: { requiresAuth: true, layout: 'employee', role: 'employee' }
  },

  {
    path: '/admin',
    name: 'AdminHome',
    component: () => import('./views/Admin.vue'),
    meta: { requiresAuth: true, layout: 'admin', role: 'admin' }
  },

  {
    path: '/login',
    name: 'Login',
    component: () => import('./views/Login.vue'),
    meta: { guest: true, layout:'auth' }
  },

  
  {
    path: '/register',
    name: 'Register',
    component: () => import('./views/Register.vue'),
    meta: { guest: true, layout:'auth'}
  },
  {
    path: '/listings',
    name: 'Listings',
    component: () => import('./views/Listings.vue')
  },
  {
    path: '/listings/:id',
    name: 'ListingDetail',
    component: () => import('./views/ListingDetail.vue')
  },
  {
    path: '/itinerary',
    name: 'ItineraryPlanner',
    component: () => import('./views/Itinerary.vue')
  },
  {
    path: '/bookings',
    name: 'Bookings',
    component: () => import('./views/Bookings.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('./views/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/favourites',
    name: 'Favourites',
    component: () => import('./views/Favourites.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/favorites',
    redirect: '/favourites'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

// Route guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore(pinia)
  await authStore.initialize()

  // Not logged in trying to access a protected route
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next({ name: 'Login', query: { redirect: to.fullPath } })
  }

  // Logged-in users trying to access guest-only routes (login/register)
  if (to.meta.guest && authStore.isAuthenticated) {
    if (authStore.role === 'admin') return next({ name: 'AdminHome' })
    if (authStore.role === 'business') return next({ name: 'BusinessHome' })
    if (authStore.role === 'employee') return next({ name: 'EmployeeHome' })
    return next({ name: 'Home' })
  }

  // Role-restricted routes
  if (to.meta.role && authStore.isAuthenticated) {
    if (to.meta.role !== authStore.role) {
      if (authStore.role === 'admin') return next({ name: 'AdminHome' })
      if (authStore.role === 'business') return next({ name: 'BusinessHome' })
      if (authStore.role === 'employee') return next({ name: 'EmployeeHome' })
      return next({ name: 'Home' })
    }
  }

  next()
})

export default router
