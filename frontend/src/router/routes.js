export const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/pages/HomePage.vue'),
    meta: {
      layout: 'default',
      pageTitle: 'Discover Caribbean Travel',
    },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/LoginPage.vue'),
    meta: {
      layout: 'auth',
      guestOnly: true,
      pageTitle: 'Sign In',
    },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/pages/RegisterPage.vue'),
    meta: {
      layout: 'auth',
      guestOnly: true,
      pageTitle: 'Create Account',
    },
  },
  {
    path: '/listings',
    name: 'Listings',
    component: () => import('@/pages/ListingsPage.vue'),
    meta: {
      layout: 'default',
      pageTitle: 'Browse Listings',
    },
  },
  {
    path: '/listings/:id',
    name: 'ListingDetail',
    component: () => import('@/pages/ListingDetailPage.vue'),
    meta: {
      layout: 'default',
      pageTitle: 'Listing Details',
    },
  },
  {
    path: '/bookings',
    name: 'Bookings',
    component: () => import('@/pages/BookingsPage.vue'),
    meta: {
      layout: 'default',
      requiresAuth: true,
      allowedRoles: ['user'],
      pageTitle: 'My Bookings',
    },
  },
  {
    path: '/favorites',
    name: 'Favorites',
    component: () => import('@/pages/FavoritesPage.vue'),
    meta: {
      layout: 'default',
      requiresAuth: true,
      allowedRoles: ['user'],
      pageTitle: 'My Favorites',
    },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/pages/ProfilePage.vue'),
    meta: {
      layout: 'default',
      requiresAuth: true,
      allowedRoles: ['user'],
      pageTitle: 'My Profile',
    },
  },
  {
    path: '/business',
    name: 'BusinessHome',
    component: () => import('@/pages/BusinessHomePage.vue'),
    meta: {
      layout: 'business',
      requiresAuth: true,
      allowedRoles: ['business'],
      pageTitle: 'Business Dashboard',
    },
  },
  {
    path: '/business/profile',
    name: 'BusinessProfile',
    component: () => import('@/pages/BusinessProfilePage.vue'),
    meta: {
      layout: 'business',
      requiresAuth: true,
      allowedRoles: ['business'],
      pageTitle: 'Business Profile',
    },
  },
  {
    path: '/admin',
    name: 'AdminHome',
    component: () => import('@/pages/AdminPage.vue'),
    meta: {
      layout: 'admin',
      requiresAuth: true,
      allowedRoles: ['admin'],
      pageTitle: 'Admin Dashboard',
    },
  },
]
