<template>
  <div class="min-h-screen bg-slate-50 text-slate-900">
    <AppHeader
      :home-link="homeLink"
      :navigation="navigation"
      :account-links="accountLinks"
      :portal-label="portalLabel"
    />
    <main>
      <slot />
    </main>
    <AppFooter v-if="showFooter" />
  </div>
</template>

<script setup>
import AppFooter from '@/components/layout/AppFooter.vue'
import AppHeader from '@/components/layout/AppHeader.vue'

defineProps({
  homeLink: {
    type: String,
    default: '/',
  },
  navigation: {
    type: Array,
    default: () => [],
  },
  accountLinks: {
    type: Array,
    default: () => [],
  },
  portalLabel: {
    type: String,
    default: '',
  },
  showFooter: {
    type: Boolean,
    default: true,
  },
})
</script>
