<template>
  <AppShell
    home-link="/business"
    :account-links="accountLinks"
    portal-label="Business Portal"
  >
    <slot />
  </AppShell>
</template>

<script setup>
import AppShell from '@/components/layout/AppShell.vue'

const accountLinks = [
  { label: 'Profile', to: '/business/profile' },
]
</script>
