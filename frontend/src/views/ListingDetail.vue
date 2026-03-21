<template>
  <div class="bg-slate-50 min-h-screen">
    <div v-if="loading" class="flex justify-center py-20">
      <svg class="h-8 w-8 animate-spin text-cyan-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
      </svg>
    </div>

    <div v-else-if="!listing" class="flex min-h-screen items-center justify-center">
      <div class="rounded-3xl border border-slate-200 bg-white px-12 py-16 text-center shadow-sm">
        <p class="text-base font-medium text-slate-500">Listing not found.</p>
        <router-link
          to="/listings"
          class="mt-6 inline-block rounded-2xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
        >
          Back to Listings
        </router-link>
      </div>
    </div>

    <!-- Listing Content -->
    <div v-else>

      <!-- Hero Image -->
      <div class="relative h-72 w-full overflow-hidden bg-slate-200 sm:h-96 lg:h-[480px]">
        <img
          v-if="listing.image_urls && listing.image_urls.length > 0"
          :src="listing.image_urls[0]"
          :alt="listing.title"
          class="h-full w-full object-cover"
          @error="handleImageError($event)"
        />
        <div v-else class="flex h-full w-full items-center justify-center text-slate-300">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-20 w-20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
        <!-- Gradient overlay -->
        <div class="absolute inset-0 bg-gradient-to-t from-slate-950/60 via-transparent to-transparent"></div>
        <!-- Back button -->
        <div class="absolute left-4 top-4 sm:left-6 lg:left-8">
          <router-link
            to="/listings"
            class="inline-flex items-center gap-2 rounded-2xl border border-white/20 bg-white/10 px-4 py-2 text-sm font-semibold text-white backdrop-blur-md transition hover:bg-white/20"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
            Back
          </router-link>
        </div>
        <!-- Title overlay at bottom of hero -->
        <div class="absolute bottom-6 left-4 right-4 sm:left-6 sm:right-6 lg:left-8 lg:right-8">
          <p class="text-sm font-semibold uppercase tracking-[0.25em] text-cyan-300">
            {{ listing.address?.country }}
          </p>
          <h1 class="mt-1 text-2xl font-bold text-white drop-shadow sm:text-3xl lg:text-4xl">
            {{ listing.title }}
          </h1>
        </div>
      </div>

      <!-- Main Content -->
      <div class="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 gap-8 lg:grid-cols-3">

          <!-- Left: Details -->
          <div class="lg:col-span-2 space-y-6">

            <!-- Location & Meta -->
            <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <div class="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p class="flex items-center gap-1.5 text-sm text-slate-500">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-cyan-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    {{ listing.address?.street ? listing.address.street + ', ' : '' }}{{ listing.address?.city }}, {{ listing.address?.country }}
                  </p>
                </div>
                <div v-if="listing.rating" class="flex items-center gap-2">
                  <div class="flex">
                    <svg
                      v-for="i in 5"
                      :key="i"
                      class="h-4 w-4"
                      :class="i <= Math.round(listing.rating) ? 'text-amber-400' : 'text-slate-200'"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  </div>
                  <span class="text-sm font-semibold text-slate-700">{{ listing.rating.toFixed(1) }}</span>
                  <span v-if="listing.reviews_count" class="text-sm text-slate-400">
                    ({{ listing.reviews_count }} {{ listing.reviews_count === 1 ? 'review' : 'reviews' }})
                  </span>
                </div>
              </div>
            </div>

            <!-- Description -->
            <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <p class="text-sm font-semibold uppercase tracking-[0.25em] text-cyan-600">About this place</p>
              <p class="mt-3 text-base leading-7 text-slate-600">
                {{ listing.description || 'No description provided.' }}
              </p>
            </div>

          </div>

          <!-- Right: Booking Card -->
          <div class="lg:col-span-1">
            <div class="sticky top-6 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-400">Starting from</p>
              <div class="mt-1 flex items-end gap-1">
                <span class="text-4xl font-bold text-slate-900">${{ listing.base_price }}</span>
                <span class="mb-1 text-sm text-slate-400">/ night</span>
              </div>

              <div class="my-6 border-t border-slate-100"></div>

              <button
                @click="showBooking = true"
                class="w-full rounded-2xl bg-slate-900 py-3.5 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-slate-800"
              >
                Book Now
              </button>

              <p class="mt-3 text-center text-xs text-slate-400">
                You won't be charged yet
              </p>
            </div>
          </div>

        </div>

        <!-- Reviews Section -->
        <div class="mt-10">
          <div class="mb-6">
            <p class="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-600">Guest Feedback</p>
            <h2 class="mt-2 text-2xl font-bold text-slate-900">Reviews</h2>
          </div>

          <!-- No Reviews -->
          <div
            v-if="reviews.length === 0"
            class="rounded-3xl border border-slate-200 bg-white px-6 py-12 text-center shadow-sm"
          >
            <p class="text-base font-medium text-slate-500">No reviews yet.</p>
            <p class="mt-1 text-sm text-slate-400">Be the first to share your experience.</p>
          </div>

          <!-- Reviews Grid -->
          <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div
              v-for="review in reviews"
              :key="review.id"
              class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
            >
              <div class="flex items-start justify-between gap-4">
                <div class="flex items-center gap-3">
                  <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-cyan-50 text-sm font-bold text-cyan-700">
                    {{ review.user?.username ? review.user.username.charAt(0).toUpperCase() : '?' }}
                  </div>
                  <div>
                    <p class="text-sm font-semibold text-slate-900">{{ review.user?.username || 'Anonymous' }}</p>
                    <p class="text-xs text-slate-400">{{ new Date(review.created_at).toLocaleDateString() }}</p>
                  </div>
                </div>
                <div class="flex shrink-0">
                  <svg
                    v-for="i in 5"
                    :key="i"
                    class="h-4 w-4"
                    :class="i <= review.rating ? 'text-amber-400' : 'text-slate-200'"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                </div>
              </div>
              <p v-if="review.comment" class="mt-4 text-sm leading-6 text-slate-600">
                {{ review.comment }}
              </p>
            </div>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted} from 'vue';
import {useRoute } from 'vue-router';
import { listingsAPI, reviewsAPI } from '../services/api';

const route = useRoute();
const listing = ref(null)
const reviews = ref([]);
const loading = ref(true);
const showBooking = ref(false);

const fetchListings = async () => {
  try {
    const response = await listingsAPI.getById(route.params.id);
    listing.value = response.data;

    const reviewResponse = await reviewsAPI.getAll({ listing_id:route.params.id});
    reviews.value = reviewResponse.data;
  }catch (err){
    console.error('Failed to load listing', err);
  }finally{
    loading.value = false;
  }
};

const handleImageError = (event) => {
  event.target.style.display = 'none';
  event.target.parentElement.innerHTML = `
    <div class="flex h-full w-full items-center justify-center text-slate-300">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-20 w-20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    </div>
  `;
};

onMounted(() => {
  fetchListings();
});
</script>