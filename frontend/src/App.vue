<template>
  <component :is="layoutComponent">
    <router-view/>
  </component>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from './stores/auth';
import DefaultLayout from './layouts/DefaultLayout.vue';
import AuthLayout from './layouts/AuthLayout.vue';

const route = useRoute();
const authStore = useAuthStore();

onMounted(() => {
  authStore.initialize();
});

const layoutComponent = computed(() => {
  const layout = route.meta.layout || 'default';
  return layout === 'auth' ? AuthLayout : DefaultLayout;
})
</script>

