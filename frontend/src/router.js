import { createRouter, createWebHistory } from 'vue-router'
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
    path: '/favorites',
    name: 'Favorites',
    component: () => import('./views/Favorites.vue'),
    meta: { requiresAuth: true }
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
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('access_token')
  const role = localStorage.getItem('user_role') // 'user' | 'business' | 'admin' | null

  // Not logged in trying to access a protected route
  if (to.meta.requiresAuth && !isAuthenticated) {
    return next({ name: 'Login', query: { redirect: to.fullPath } })
  }

  // Logged-in users trying to access guest-only routes (login/register)
  if (to.meta.guest && isAuthenticated) {
    if (role === 'admin') return next({ name: 'AdminHome' })
    if (role === 'business') return next({ name: 'BusinessHome' })
    return next({ name: 'Home' })
  }

  // Role-restricted routes
  if (to.meta.role && isAuthenticated) {
    if (to.meta.role === 'admin' && role !== 'admin') {
      return next({ name: role === 'business' ? 'BusinessHome' : 'Home' })
    }
    if (to.meta.role === 'business' && role !== 'business') {
      return next({ name: role === 'admin' ? 'AdminHome' : 'Home' })
    }
    if (to.meta.role === 'user' && (role === 'admin' || role === 'business')) {
      return next({ name: role === 'admin' ? 'AdminHome' : 'BusinessHome' })
    }
  }

  next()
})

export default router
