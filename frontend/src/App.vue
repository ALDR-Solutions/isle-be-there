<template>
  <component :is="layoutComponent">
    <router-view/>
  </component>
  <AppToast />
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from './stores/auth';
import DefaultLayout from './layouts/DefaultLayout.vue';
import AuthLayout from './layouts/AuthLayout.vue';
import BusinessLayout from './layouts/BusinessLayout.vue';
import AppToast from './components/AppToast.vue';
import AdminLayout from './layouts/AdminLayout.vue';
import EmployeeLayout from './layouts/EmployeeLayout.vue';

const route = useRoute();
const authStore = useAuthStore();

onMounted(async () => {
  await authStore.initialize();
});

const layoutComponent = computed(() => {
  const layout = route.meta.layout || 'default';
  if (layout === 'auth') return AuthLayout;
  if (layout === 'business') return BusinessLayout;
  if (layout === 'admin') return AdminLayout;
  if (layout === 'employee') return EmployeeLayout;
  return DefaultLayout;
})
</script>

