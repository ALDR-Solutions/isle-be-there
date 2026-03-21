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
        <DestinationCard
          v-for="listing in listings"
          :key="listing.id"
          :listing="listing"
        />
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { listingsAPI } from '../services/api';
import DestinationCard from '../components/DestinationCard.vue';

const listings = ref([]);
const loading = ref(true);

onMounted(async () => {
  try {
    const response = await listingsAPI.getAll();
    listings.value = response.data;
  } catch (err) {
    console.error('Failed to load listings', err);
  } finally {
    loading.value = false;
  }
});
</script>
