<template>
  <div class="mb-4 flex flex-wrap items-center gap-2">
    <span v-if="details.has_dining" class="rounded-full bg-cyan-50 px-2.5 py-0.5 text-xs font-medium text-cyan-700">
      Dine-in
    </span>
    <span v-if="details.has_take_out" class="rounded-full bg-cyan-50 px-2.5 py-0.5 text-xs font-medium text-cyan-700">
      Takeout
    </span>
    <span v-if="details.has_delivery" class="rounded-full bg-cyan-50 px-2.5 py-0.5 text-xs font-medium text-cyan-700">
      Delivery
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
