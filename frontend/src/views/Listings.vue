<template>
  <div class="bg-slate-50 min-h-screen">
    <div class="bg-white border-b border-slate-200">
      <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <p
          class="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-600"
        >
          {{ hasSearchQuery ? "Search Results" : "Browse All" }}
        </p>
        <h1 class="mt-3 text-3xl font-bold text-slate-900 sm:text-4xl">
          {{
            hasSearchQuery ? `Results for "${searchQuery}"` : "Explore Listings"
          }}
        </h1>
        <p class="mt-3 max-w-2xl text-base leading-7 text-slate-600">
          {{
            hasSearchQuery
              ? "Discover matching stays, adventures, and coastal escapes across the Caribbean."
              : "Discover handpicked stays, adventures, and coastal escapes across the Caribbean."
          }}
        </p>
      </div>
    </div>
    <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <div v-if="loading" class="flex justify-center py-20">
        <svg
          class="h-8 w-8 animate-spin text-cyan-500"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            class="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            stroke-width="4"
          />
          <path
            class="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
          />
        </svg>
      </div>

      <div
        v-else-if="listings.length === 0"
        class="rounded-3xl border border-slate-200 bg-white px-6 py-16 text-center shadow-sm"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="mx-auto h-12 w-12 text-slate-300"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="1.5"
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
        <p class="mt-4 text-base font-medium text-slate-500">
          {{
            hasSearchQuery
              ? "No matching listings found."
              : "No listings available yet."
          }}
        </p>
        <p class="mt-1 text-sm text-slate-400">
          {{
            hasSearchQuery
              ? "Try another keyword."
              : "Check back soon for new destinations."
          }}
        </p>
      </div>
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
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { listingsAPI } from "../services/api";
import DestinationCard from "../components/DestinationCard.vue";

const listings = ref([]);
const loading = ref(true);
const route = useRoute();

const searchQuery = computed(() => {
  const rawQ = route.query.q;
  return typeof rawQ === "string" ? rawQ.trim() : "";
});

const hasSearchQuery = computed(() => Boolean(searchQuery.value));

async function fetchListings() {
  loading.value = true;

  try {
    const response = hasSearchQuery.value
      ? await listingsAPI.search(searchQuery.value)
      : await listingsAPI.getAll();
    listings.value = response.data;
  } catch (err) {
    console.error("Failed to load listings", err);
    listings.value = [];
  } finally {
    loading.value = false;
  }
}

watch(
  () => route.query.q,
  () => {
    fetchListings();
  },
  { immediate: true },
);
</script>
