<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <h1 class="text-3xl font-bold text-gray-900 mb-8">My Favorites</h1>
    
    <div v-if="loading" class="flex justify-center py-20">
      <svg class="h-8 w-8 animate-spin text-cyan-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
      </svg>
    </div>
    
    <div v-else-if="favorites.length === 0" class="text-center py-8">
      <p class="text-gray-500">You haven't added any favorites yet.</p>
      <router-link 
        to="/listings"
        class="mt-4 inline-block text-indigo-600 hover:text-indigo-700"
      >
        Browse Listings
      </router-link>
    </div>
    
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="favorite in favorites" :key="favorite.id" class="bg-white rounded-lg shadow-md overflow-hidden">
        <div class="h-48 bg-gray-200 relative">
          <img 
            v-if="favorite.listing && favorite.listing.image_urls && favorite.listing.image_urls.length > 0" 
            :src="favorite.listing.image_urls[0]" 
            :alt="favorite.listing.title"
            class="w-full h-full object-cover"
          />
          <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <button 
            @click="removeFavorite(favorite.listing_id)"
            class="absolute top-2 right-2 bg-white rounded-full p-2 shadow-md hover:bg-red-50"
            title="Remove from favorites"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
        <div class="p-6">
          <h3 class="text-lg font-semibold text-gray-900">{{ favorite.listing?.title || 'Listing' }}</h3>
          <p class="mt-2 text-gray-600">{{ favorite.listing?.address?.city }}, {{ favorite.listing?.address?.country }}</p>
          <div class="mt-4 flex items-center justify-between">
            <span class="text-indigo-600 font-bold">${{ favorite.listing?.base_price }}/night</span>
            <router-link 
              :to="`/listings/${favorite.listing_id}`"
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
import { favoritesAPI } from '../services/api';

const favorites = ref([]);
const loading = ref(true);

const fetchFavorites = async () => {
  try {
    const response = await favoritesAPI.getAll();
    favorites.value = response.data;
  } catch (err) {
    console.error('Failed to load favorites', err);
  } finally {
    loading.value = false;
  }
};

const removeFavorite = async (listingId) => {
  try {
    await favoritesAPI.remove(listingId);
    // Remove from local list
    favorites.value = favorites.value.filter(f => f.listing_id !== listingId);
  } catch (err) {
    console.error('Failed to remove favorite', err);
  }
};

onMounted(() => {
  fetchFavorites();
});
</script>
