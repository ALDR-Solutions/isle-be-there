<template>
  <div class="mb-4 flex flex-wrap items-center gap-2">
    <span v-if="details.duration" class="rounded-full bg-violet-50 px-2.5 py-0.5 text-xs font-medium text-violet-700">
      {{ details.duration }} {{ details.duration === 1 ? 'hr' : 'hrs' }}
    </span>

    <span
      v-if="details.available_slots != null"
      class="rounded-full px-2.5 py-0.5 text-xs font-medium"
      :class="details.available_slots > 0 ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-600'"
    >
      {{ details.available_slots > 0 ? `${details.available_slots} slots left` : 'Fully booked' }}
    </span>

    <span v-if="details.service_availability" class="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600">
      {{ details.service_availability }}
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
