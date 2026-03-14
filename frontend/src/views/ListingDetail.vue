<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <div v-if="loading" class="text-center py-8">
      <p class="text-gray-500">Loading...</p>
    </div>
    
    <div v-else-if="listing">
      <div class="bg-white rounded-lg shadow-lg overflow-hidden">
        <div class="h-64 bg-gray-200 relative">
          <img 
            v-if="listing.image_urls && listing.image_urls.length > 0" 
            :src="listing.image_urls[0]" 
            :alt="listing.title"
            class="w-full h-full object-cover"
            @error="handleImageError($event)"
          />
          <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        </div>
        
        <div class="p-8">
          <div class="flex justify-between items-start">
            <div>
              <h1 class="text-3xl font-bold text-gray-900">{{ listing.title }}</h1>
              <p class="mt-2 text-gray-600">{{ listing.address?.city }}, {{ listing.address?.country }}</p>
            </div>
            <p class="text-2xl font-bold text-indigo-600">${{ listing.base_price }}<span class="text-sm text-gray-500">/night</span></p>
          </div>
          
          <p class="mt-4 text-gray-600">{{ listing.description }}</p>
          
          <button 
            @click="showBooking = true"
            class="mt-6 w-full bg-indigo-600 text-white py-3 rounded-md hover:bg-indigo-700"
          >
            Book Now
          </button>
        </div>
      </div>
      
      <div class="mt-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-4">Reviews</h2>
        
        <div v-if="reviews.length === 0" class="text-center py-8">
          <p class="text-gray-500">No reviews yet.</p>
        </div>
        
        <div v-else class="space-y-4">
          <ReviewCard v-for="review in reviews" :key="review.id" :review="review" />
        </div>
      </div>
    </div>
    
    <div v-else class="text-center py-8">
      <p class="text-gray-500">Listing not found.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { listingsAPI, reviewsAPI } from '../services/api';
import ReviewCard from '../components/ReviewCard.vue';

const route = useRoute();
const listing = ref(null);
const reviews = ref([]);
const loading = ref(true);
const showBooking = ref(false);

const fetchListing = async () => {
  try {
    const response = await listingsAPI.getById(route.params.id);
    listing.value = response.data;
    
    const reviewsResponse = await reviewsAPI.getAll({ listing_id: route.params.id });
    reviews.value = reviewsResponse.data;
  } catch (err) {
    console.error('Failed to load listing', err);
  } finally {
    loading.value = false;
  }
};

const handleImageError = (event) => {
  // Replace broken image with placeholder
  event.target.style.display = 'none';
  event.target.parentElement.innerHTML = `
    <div class="w-full h-full flex items-center justify-center text-gray-400">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    </div>
  `;
};

onMounted(() => {
  fetchListing();
});
</script>
