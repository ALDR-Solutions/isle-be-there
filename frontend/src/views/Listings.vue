<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <h1 class="text-3xl font-bold text-gray-900 mb-8">Explore Listings</h1>
    
    <div v-if="loading" class="text-center py-8">
      <p class="text-gray-500">Loading listings...</p>
    </div>
    
    <div v-else-if="listings.length === 0" class="text-center py-8">
      <p class="text-gray-500">No listings available.</p>
    </div>
    
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="listing in listings" :key="listing.id" class="bg-white rounded-lg shadow-md overflow-hidden">
        <div class="h-48 bg-gray-200 relative">
          <img 
            v-if="listing.image_urls && listing.image_urls.length > 0" 
            :src="listing.image_urls[0]" 
            :alt="listing.title"
            class="w-full h-full object-cover"
            @error="handleImageError($event)"
          />
          <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        </div>
        <div class="p-6">
          <h3 class="text-lg font-semibold text-gray-900">{{ listing.title }}</h3>
          <p class="mt-2 text-gray-600">{{ listing.address?.city }}, {{ listing.address?.country }}</p>
          <div class="mt-4 flex items-center justify-between">
            <span class="text-indigo-600 font-bold">${{ listing.base_price }}/night</span>
            <router-link 
              :to="`/listings/${listing.id}`"
              class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
            >
              View Details
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { listingsAPI } from '../services/api';

const listings = ref([]);
const loading = ref(true);

const fetchListings = async () => {
  try {
    const response = await listingsAPI.getAll();
    listings.value = response.data;
  } catch (err) {
    console.error('Failed to load listings', err);
  } finally {
    loading.value = false;
  }
};

const handleImageError = (event) => {
  // Replace broken image with placeholder
  event.target.style.display = 'none';
  event.target.parentElement.innerHTML = `
    <div class="w-full h-full flex items-center justify-center text-gray-400">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    </div>
  `;
};

onMounted(() => {
  fetchListings();
});
</script>
