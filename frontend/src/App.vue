<template>
  <component :is="layoutComponent">
    <router-view/>
  </component>
  <AppToast />
</template>

<script setup>
import { computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from './stores/auth';
import DefaultLayout from './layouts/DefaultLayout.vue';
import AuthLayout from './layouts/AuthLayout.vue';
import BusinessLayout from './layouts/BusinessLayout.vue';
import AppToast from './components/AppToast.vue';
import AdminLayout from './layouts/AdminLayout.vue';
import EmployeeLayout from './layouts/EmployeeLayout.vue';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

function getRoleRedirect() {
  if (authStore.role === 'admin') return { name: 'AdminHome' };
  if (authStore.role === 'business') return { name: 'BusinessHome' };
  if (authStore.role === 'employee') return { name: 'EmployeeHome' };
  return { name: 'Home' };
}

watch(
  () => [authStore.authResolved, authStore.isAuthenticated, authStore.role, route.fullPath],
  async ([authResolved, isAuthenticated]) => {
    if (!authResolved) {
      return;
    }

    if (route.meta?.guest && isAuthenticated) {
      const target = getRoleRedirect();
      if (target.name !== route.name) {
        await router.replace(target);
      }
      return;
    }

    if (!(route.meta?.requiresAuth || route.meta?.role)) {
      return;
    }

    if (!isAuthenticated) {
      if (route.name !== 'Login') {
        await router.replace({
          name: 'Login',
          query: { redirect: route.fullPath },
        });
      }
      return;
    }

    if (route.meta?.role && route.meta.role !== authStore.role) {
      const target = getRoleRedirect();
      if (target.name !== route.name) {
        await router.replace(target);
      }
    }
  },
  { immediate: true },
);

const layoutComponent = computed(() => {
  const layout = route.meta.layout || 'default';
  if (layout === 'auth') return AuthLayout;
  if (layout === 'business') return BusinessLayout;
  if (layout === 'admin') return AdminLayout;
  if (layout === 'employee') return EmployeeLayout;
  return DefaultLayout;
})
</script>

