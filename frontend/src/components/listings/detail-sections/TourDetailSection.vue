<template>
  <div class="rounded-2xl border border-slate-200 bg-white p-6">
    <h2 class="mb-4 text-lg font-bold text-slate-900">Tour Details</h2>

    <div class="space-y-4">
      <div v-if="details.duration" class="flex items-center gap-3">
        <span class="w-36 text-sm text-slate-500">Duration</span>
        <span class="text-sm font-medium text-slate-800">
          {{ details.duration }} {{ details.duration === 1 ? 'hour' : 'hours' }}
        </span>
      </div>

      <div v-if="details.available_slots != null || details.max_capacity != null" class="flex items-center gap-3">
        <span class="w-36 text-sm text-slate-500">Availability</span>
        <span class="text-sm font-medium" :class="details.available_slots > 0 ? 'text-emerald-700' : 'text-red-600'">
          {{ details.available_slots ?? '—' }} / {{ details.max_capacity ?? '—' }} slots available
        </span>
      </div>

      <div v-if="details.available_days?.length" class="flex items-start gap-3">
        <span class="w-36 shrink-0 text-sm text-slate-500">Available days</span>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="day in details.available_days"
            :key="day"
            class="rounded-full bg-violet-50 px-2.5 py-0.5 text-xs font-medium text-violet-700"
          >
            {{ day }}
          </span>
        </div>
      </div>

      <div v-if="details.service_availability" class="flex items-center gap-3">
        <span class="w-36 text-sm text-slate-500">Schedule</span>
        <span class="text-sm font-medium text-slate-800">{{ details.service_availability }}</span>
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
