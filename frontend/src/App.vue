<template>
  <component :is="layoutComponent">
    <router-view />
  </component>
  <AppToast />
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AdminLayout from '@/layouts/AdminLayout.vue'
import AuthLayout from '@/layouts/AuthLayout.vue'
import BusinessLayout from '@/layouts/BusinessLayout.vue'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import AppToast from '@/components/AppToast.vue'
import { useAuthStore } from '@/stores/auth'
import { useFavouritesStore } from '@/stores/favourites'

const route = useRoute()
const authStore = useAuthStore()
const favouritesStore = useFavouritesStore()

onMounted(async () => {
  await authStore.initialize()
  if (authStore.isAuthenticated) {
    await favouritesStore.fetchAll()
  }
})

const layoutComponent = computed(() => {
  const layout = route.meta.layout || 'default'
  if (layout === 'auth') return AuthLayout
  if (layout === 'business') return BusinessLayout
  if (layout === 'admin') return AdminLayout
  return DefaultLayout
})
</script>

