<template>
  <div class="mb-4 flex flex-wrap items-center gap-2">
    <div v-if="details.star_level" class="flex items-center gap-1">
      <svg
        v-for="i in 5"
        :key="i"
        class="h-3.5 w-3.5"
        :class="i <= details.star_level ? 'text-amber-400' : 'text-slate-200'"
        fill="currentColor"
        viewBox="0 0 20 20"
      >
        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
      </svg>
    </div>

    <span
      v-if="details.available_rooms != null"
      class="rounded-full px-2.5 py-0.5 text-xs font-medium"
      :class="details.available_rooms > 0 ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-600'"
    >
      {{ details.available_rooms > 0 ? `${details.available_rooms} rooms available` : 'Fully booked' }}
    </span>

    <span v-if="details.deposit_required" class="rounded-full bg-amber-50 px-2.5 py-0.5 text-xs font-medium text-amber-700">
      Deposit required
    </span>
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
