<template>
  <div class="bg-slate-50 min-h-screen">

    <!-- Page Header -->
    <div class="bg-white border-b border-slate-200">
      <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <p class="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-600">
          Your Collection
        </p>
        <h1 class="mt-3 text-3xl font-bold text-slate-900 sm:text-4xl">
          My Favorites
        </h1>
        <p class="mt-3 max-w-2xl text-base leading-7 text-slate-600">
          Your saved destinations and stays, ready whenever you are.
        </p>
      </div>
    </div>

    <!-- Content -->
    <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">

      <!-- Loading State -->
      <div
        v-if="loading"
        class="rounded-3xl border border-slate-200 bg-white px-6 py-16 text-center shadow-sm"
      >
        <svg class="mx-auto h-8 w-8 animate-spin text-cyan-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
        </svg>
        <p class="mt-4 text-base font-medium text-slate-500">Loading your favorites...</p>
      </div>

      <!-- Empty State -->
      <div
        v-else-if="favorites.length === 0"
        class="rounded-3xl border border-slate-200 bg-white px-6 py-16 text-center shadow-sm"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17.593 3.322c1.1.128 1.907 1.077 1.907 2.185V21L12 17.25 4.5 21V5.507c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0111.186 0z" />
        </svg>
        <p class="mt-4 text-base font-medium text-slate-500">No favorites saved yet.</p>
        <p class="mt-1 text-sm text-slate-400">Start exploring and bookmark the places that catch your eye.</p>
        <router-link
          to="/listings"
          class="mt-6 inline-flex items-center justify-center rounded-2xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-slate-800 hover:shadow-lg"
        >
          Browse Listings
        </router-link>
      </div>

      <!-- Favorites Grid -->
      <div v-else>
        <p class="mb-6 text-sm font-medium text-slate-500">
          {{ favorites.length }} {{ favorites.length === 1 ? 'destination' : 'destinations' }} saved
        </p>

        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <div v-for="favorite in favorites" :key="favorite.id" class="relative">
            <DestinationCard :listing="favorite.listing" />

            <!-- Remove Favorite Button -->
            <button
              @click="removeFavorite(favorite.listing_id)"
              class="absolute left-4 top-4 z-10 flex h-9 w-9 items-center justify-center rounded-full border border-white/20 bg-white/15 text-white backdrop-blur-md transition-colors hover:bg-red-500/80 hover:text-white"
              title="Remove from favorites"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { favoritesAPI } from '../services/api';
import DestinationCard from '../components/DestinationCard.vue';

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
    favorites.value = favorites.value.filter(f => f.listing_id !== listingId);
  } catch (err) {
    console.error('Failed to remove favorite', err);
  }
};

onMounted(() => {
  fetchFavorites();
});
</script>
