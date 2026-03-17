import { createRouter, createWebHistory } from 'vue-router'
import Home from './views/Home.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },

  {
    path:'/BusinessHome',
    name: 'BusinessHome',
    component: () => import('./views/BusinessHome.vue'),
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
  routes
})

// Route guards
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('access_token')
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    // Redirect to login if not authenticated
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.meta.guest && isAuthenticated) {
    // Redirect to home if already authenticated (for guest routes like login/register)
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
