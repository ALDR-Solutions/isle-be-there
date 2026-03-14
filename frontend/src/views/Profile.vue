<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <h1 class="text-3xl font-bold text-gray-900 mb-8">My Profile</h1>
    
    <div class="bg-white rounded-lg shadow-md p-8">
      <div class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-700">Email</label>
          <p class="mt-1 text-gray-900">{{ user?.email }}</p>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700">Username</label>
          <p class="mt-1 text-gray-900">{{ user?.username }}</p>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700">Full Name</label>
          <p class="mt-1 text-gray-900">{{ user?.first_name }} {{ user?.last_name }}</p>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700">Account Type</label>
          <p class="mt-1 text-gray-900">
            <span v-if="user?.is_business" class="text-indigo-600">Business Account</span>
            <span v-else>Regular Account</span>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useAuthStore } from '../stores/auth';

const authStore = useAuthStore();
const user = computed(() => authStore.user);
</script>
