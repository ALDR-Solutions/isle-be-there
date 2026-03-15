<template>
  <div class="bg-white rounded-2xl overflow-hidden shadow-md hover:scale-[1.02] transition-transform duration-300 flex flex-col h-full">
    <!-- Image -->
    <img
      v-if="listing.image_urls?.length"
      :src="listing.image_urls[0]"
      :alt="listing.title"
      class="h-48 w-full object-cover"
      @error="$event.target.src = '/placeholder.jpg'"
    />
    <div v-else class="h-48 w-full bg-gray-200 flex items-center justify-center text-gray-400">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    </div>

    <!-- Content -->
    <div class="p-5 flex flex-col gap-3 flex-grow">
      <h3 class="text-lg font-semibold text-gray-900 leading-tight">{{ listing.title }}</h3>

      <!-- Location -->
      <div v-if="listing.address" class="flex items-center text-teal-700 text-sm">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M17.657 16.657L13.414 20.9a2 2 0 01-2.828 0l-4.243-4.243a8 8 0 1111.314 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <span class="truncate">{{ locationText }}</span>
      </div>

      <!-- Rating -->
      <div v-if="listing.rating" class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div class="flex">
            <svg
              v-for="i in 5"
              :key="i"
              class="h-4 w-4"
              :class="i <= Math.round(listing.rating) ? 'text-yellow-400' : 'text-gray-300'"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          </div>
          <span class="text-green-600 font-semibold text-sm">{{ listing.rating.toFixed(1) }}</span>
        </div>
        <span v-if="listing.reviews_count" class="text-teal-700 text-sm font-medium">
          {{ listing.reviews_count }} {{ listing.reviews_count === 1 ? 'Review' : 'Reviews' }}
        </span>
      </div>

      <!-- Price -->
      <div class="mt-auto text-xl font-bold text-green-500">
        ${{ parseFloat(listing.base_price || 0).toFixed(2) }}
      </div>

      <!-- CTA -->
      <router-link
        :to="`/listings/${listing.id}`"
        class="block w-full text-center bg-teal-700 hover:bg-gray-800 text-white font-semibold py-3 rounded-full transition-all duration-300"
      >
        View Details
      </router-link>
    </div>
  </div>
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