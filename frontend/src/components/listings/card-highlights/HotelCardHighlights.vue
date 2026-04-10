<template>
  <div class="mb-4 flex flex-wrap items-center gap-2">
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
