<template>
  <AppShell :navigation="navigation" :account-links="accountLinks">
    <slot />
  </AppShell>
</template>

<script setup>
import AppShell from '@/components/layout/AppShell.vue'

const navigation = [
  { label: 'Home', to: '/' },
  { label: 'Listings', to: '/listings' },
  { label: 'Bookings', to: '/bookings' },
]

const accountLinks = [
  { label: 'Profile', to: '/profile' },
  { label: 'Favorites', to: '/favorites' },
]
</script>
