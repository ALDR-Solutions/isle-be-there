<template>
  <div class="rounded-2xl border border-slate-200 bg-white p-6">
    <h2 class="mb-4 text-lg font-bold text-slate-900">Restaurant Details</h2>

    <div class="space-y-4">
      <div class="flex items-center gap-3">
        <span class="w-36 text-sm text-slate-500">Services</span>
        <div class="flex flex-wrap gap-2">
          <span v-if="details.has_dining" class="rounded-full bg-cyan-50 px-2.5 py-0.5 text-xs font-medium text-cyan-700">Dine-in</span>
          <span v-if="details.has_take_out" class="rounded-full bg-cyan-50 px-2.5 py-0.5 text-xs font-medium text-cyan-700">Takeout</span>
          <span v-if="details.has_delivery" class="rounded-full bg-cyan-50 px-2.5 py-0.5 text-xs font-medium text-cyan-700">Delivery</span>
          <span v-if="!details.has_dining && !details.has_take_out && !details.has_delivery" class="text-sm text-slate-400">
            Not specified
          </span>
        </div>
      </div>

      <div v-if="details.table_seating != null" class="flex items-center gap-3">
        <span class="w-36 text-sm text-slate-500">Table seating</span>
        <span class="text-sm font-medium text-slate-800">
          {{ details.table_seating ? 'Available' : 'Not available' }}
        </span>
      </div>

      <div v-if="details.service_availability" class="flex items-center gap-3">
        <span class="w-36 text-sm text-slate-500">Hours</span>
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
