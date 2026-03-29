<template>
  <AppShell home-link="/admin" portal-label="Admin Portal">
    <slot />
  </AppShell>
</template>

<script setup>
import AppShell from '@/components/layout/AppShell.vue'
</script>
