<template>
  <div class="rounded-2xl border border-slate-200 bg-white p-6">
    <h2 class="mb-4 text-lg font-bold text-slate-900">Hotel Details</h2>

    <div class="space-y-4">
      <div v-if="details.star_level" class="flex items-center gap-3">
        <span class="w-36 text-sm text-slate-500">Star rating</span>
        <div class="flex items-center gap-1">
          <svg
            v-for="i in 5"
            :key="i"
            class="h-5 w-5"
            :class="i <= details.star_level ? 'text-amber-400' : 'text-slate-200'"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
        </div>
      </div>

      <div v-if="details.available_rooms != null || details.total_rooms != null" class="flex items-center gap-3">
        <span class="w-36 text-sm text-slate-500">Availability</span>
        <span class="text-sm font-medium text-slate-800">
          {{ details.available_rooms ?? '—' }} / {{ details.total_rooms ?? '—' }} rooms available
        </span>
      </div>

      <div v-if="details.cancellation_until_hours != null" class="flex items-center gap-3">
        <span class="w-36 text-sm text-slate-500">Cancellation</span>
        <span class="text-sm font-medium text-slate-800">
          Free cancellation up to {{ details.cancellation_until_hours }} hours before check-in
        </span>
      </div>

      <div v-if="details.deposit_required != null" class="flex items-center gap-3">
        <span class="w-36 text-sm text-slate-500">Deposit</span>
        <span
          class="rounded-full px-2.5 py-0.5 text-xs font-medium"
          :class="details.deposit_required ? 'bg-amber-50 text-amber-700' : 'bg-emerald-50 text-emerald-700'"
        >
          {{ details.deposit_required ? 'Required' : 'Not required' }}
        </span>
      </div>

      <div v-if="details.hotel_amenities?.length">
        <p class="mb-2 text-sm text-slate-500">Amenities</p>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="amenity in details.hotel_amenities"
            :key="amenity"
            class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700"
          >
            {{ amenity }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  details: {
    type: Object,
    default: () => ({}),
  },
})
</script>
