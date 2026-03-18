<template>
  <article class="group flex h-full flex-col overflow-hidden rounded-[1.75rem] border border-slate-200 bg-white shadow-sm transition duration-300 hover:-translate-y-1 hover:shadow-xl">
    <div class="relative overflow-hidden">
      <img
        v-if="listing.image_urls?.length"
        :src="listing.image_urls[0]"
        :alt="listing.title"
        class="h-56 w-full object-cover transition duration-500 group-hover:scale-105"
        @error="$event.target.src = '/placeholder.jpg'"
      />

      <div
        v-else
        class="flex h-56 w-full items-center justify-center bg-slate-200 text-slate-400"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
      </div>

      <div class="absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-slate-950/55 to-transparent"></div>

      <div class="absolute left-4 top-4">
        <span class="rounded-full border border-white/20 bg-white/15 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-white backdrop-blur-md">
          Featured
        </span>
      </div>

      <div class="absolute bottom-4 left-4 right-4 flex items-end justify-between">
        <div v-if="listing.rating" class="rounded-full bg-white/90 px-3 py-1.5 text-xs font-semibold text-slate-900 shadow-sm">
          {{ listing.rating.toFixed(1) }} / 5 rating
        </div>
      </div>
    </div>

    <div class="flex flex-1 flex-col p-6">
      <div class="mb-4">
        <h3 class="text-xl font-bold leading-tight text-slate-900">
          {{ listing.title }}
        </h3>

        <div v-if="listing.address" class="mt-3 flex items-start text-sm text-slate-500">
          <svg xmlns="http://www.w3.org/2000/svg" class="mr-2 mt-0.5 h-4 w-4 shrink-0 text-cyan-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M17.657 16.657L13.414 20.9a2 2 0 01-2.828 0l-4.243-4.243a8 8 0 1111.314 0z"
            />
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
            />
          </svg>
          <span class="line-clamp-2">{{ locationText }}</span>
        </div>
      </div>

      <div v-if="listing.rating" class="mb-5 flex items-center justify-between">
        <div class="flex items-center gap-2">
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
        </div>

        <span v-if="listing.reviews_count" class="text-sm font-medium text-cyan-700">
          {{ listing.reviews_count }} {{ listing.reviews_count === 1 ? 'Review' : 'Reviews' }}
        </span>
      </div>

      <div v-else class="mb-5 text-sm text-slate-400">
        New listing
      </div>

      <div class="mt-auto flex items-center justify-between gap-4">
        <div>
          <p class="text-xs uppercase tracking-[0.2em] text-slate-400">Starting from</p>
          <p class="text-2xl font-bold text-slate-900">
            ${{ parseFloat(listing.base_price || 0).toFixed(2) }}
          </p>
        </div>

        <router-link
          :to="`/listings/${listing.id}`"
          class="inline-flex items-center justify-center rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
        >
          View Details
        </router-link>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  listing: {
    type: Object,
    required: true,
  },
})

const locationText = computed(() => {
  const a = props.listing.address
  if (!a) return ''
  return [a.street, a.city, a.state, a.postal_code, a.country].filter(Boolean).join(', ')
})
</script>
