<template>
  <div class="bg-slate-50 min-h-screen">

    <!-- Page Header -->
    <div class="bg-white border-b border-slate-200">
      <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <p class="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-600">
          Browse All
        </p>
        <h1 class="mt-3 text-3xl font-bold text-slate-900 sm:text-4xl">
          Explore Listings
        </h1>
        <p class="mt-3 max-w-2xl text-base leading-7 text-slate-600">
          Discover handpicked stays, adventures, and coastal escapes across the Caribbean.
        </p>
      </div>
    </div>

    <!-- Listings Grid -->
    <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">

      <!-- Loading State -->
      <div
        v-if="loading"
        class="rounded-3xl border border-slate-200 bg-white px-6 py-16 text-center text-slate-500 shadow-sm"
      >
        Loading listings...
      </div>

      <!-- Empty State -->
      <div
        v-else-if="listings.length === 0"
        class="rounded-3xl border border-slate-200 bg-white px-6 py-16 text-center shadow-sm"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <p class="mt-4 text-base font-medium text-slate-500">No listings available yet.</p>
        <p class="mt-1 text-sm text-slate-400">Check back soon for new destinations.</p>
      </div>

      <!-- Grid -->
      <div v-else class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="listing in listings"
          :key="listing.id"
          class="group overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-md"
        >
          <!-- Image -->
          <div class="relative h-52 bg-slate-100 overflow-hidden">
            <img
              v-if="listing.image_urls && listing.image_urls.length > 0"
              :src="listing.image_urls[0]"
              :alt="listing.title"
              class="h-full w-full object-cover transition duration-500 group-hover:scale-105"
              @error="handleImageError($event)"
            />
            <div v-else class="flex h-full w-full items-center justify-center text-slate-300">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-14 w-14" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
          </div>

          <!-- Content -->
          <div class="p-6">
            <h3 class="text-base font-bold text-slate-900 leading-snug">
              {{ listing.title }}
            </h3>
            <p class="mt-1 flex items-center gap-1 text-sm text-slate-500">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 shrink-0 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              {{ listing.address?.city }}, {{ listing.address?.country }}
            </p>

            <div class="mt-5 flex items-center justify-between">
              <div>
                <span class="text-lg font-bold text-slate-900">${{ listing.base_price }}</span>
                <span class="text-sm text-slate-400"> / night</span>
              </div>
              <router-link
                :to="`/listings/${listing.id}`"
                class="rounded-2xl bg-slate-900 px-5 py-2 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-slate-800"
              >
                View Details
              </router-link>
            </div>
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
  try{
    const response = await listingsAPI.getAll();
    listings.value = response.data;
  }catch (err) {
    console.error('Failed to load listings', err);
  }finally{
    loading.value = false;
  }
};

const handleImageError = (event) => {
  event.target.style.display = 'none';
  event.target.parentElement.innerHTML = `
    <div class="flex h-full w-full items-center justify-center text-slate-300">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-14 w-14" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    </div>
  `;
};

onMounted(() => {
  fetchListings();
});
</script>