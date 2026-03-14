<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex">
            <router-link to="/" class="flex-shrink-0 flex items-center">
              <span class="text-xl font-bold text-indigo-600">Isle Be There</span>
            </router-link>
          </div>
          <div class="flex items-center space-x-4">
            <router-link to="/listings" class="text-gray-600 hover:text-gray-900">Listings</router-link>
            <template v-if="authStore.isAuthenticated">
              <router-link to="/bookings" class="text-gray-600 hover:text-gray-900">Bookings</router-link>
              <router-link to="/profile" class="text-gray-600 hover:text-gray-900">Profile</router-link>
              <span class="text-gray-600">{{ authStore.user?.email }}</span>
              <button 
                @click="handleLogout"
                class="text-gray-600 hover:text-gray-900"
              >
                Logout
              </button>
            </template>
            <template v-else>
              <router-link to="/login" class="text-gray-600 hover:text-gray-900">Login</router-link>
              <router-link to="/register" class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700">Sign Up</router-link>
            </template>
          </div>
        </div>
      </div>
    </nav>
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from './stores/auth';

const router = useRouter();
const authStore = useAuthStore();

onMounted(() => {
  authStore.initialize();
});

const handleLogout = () => {
  authStore.logout();
  router.push('/');
};
</script>
