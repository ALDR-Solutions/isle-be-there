<template>
  <div class="rounded-2xl border border-slate-200 bg-white p-6">
    <h2 class="mb-4 text-lg font-bold text-slate-900">Restaurant Details</h2>

    <div class="space-y-4">
      <div class="flex items-center gap-3">
        <span class="w-36 text-sm text-slate-500">Services</span>
        <div class="flex flex-wrap gap-2">
          <span
            v-if="details.has_dining"
            class="rounded-full bg-cyan-50 px-2.5 py-0.5 text-xs font-medium text-cyan-700"
          >
            Dine-in
          </span>
          <span
            v-if="details.has_take_out"
            class="rounded-full bg-cyan-50 px-2.5 py-0.5 text-xs font-medium text-cyan-700"
          >
            Takeout
          </span>
          <span
            v-if="details.has_delivery"
            class="rounded-full bg-cyan-50 px-2.5 py-0.5 text-xs font-medium text-cyan-700"
          >
            Delivery
          </span>
          <span
            v-if="!details.has_dining && !details.has_take_out && !details.has_delivery"
            class="text-sm text-slate-400"
          >
            Not specified
          </span>
        </div>
      </div>

      <div v-if="details.table_seating != null" class="flex items-center gap-3">
        <span class="w-36 text-sm text-slate-500">Table seating</span>
        <span class="text-sm font-medium text-slate-800">
          {{ details.table_seating ? "Available" : "Not available" }}
        </span>
      </div>

      <div v-if="details.service_availability" class="flex items-center gap-3">
        <span class="w-36 text-sm text-slate-500">Hours</span>
        <span class="text-sm font-medium text-slate-800">{{ details.service_availability }}</span>
      </div>
    </div>

    <div v-if="menuSections.length" class="mt-6">
      <h3 class="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-600">Menu</h3>
      <div class="mt-3 space-y-4">
        <div
          v-for="(section, sectionIndex) in menuSections"
          :key="`${section.name}-${sectionIndex}`"
          class="rounded-2xl border border-slate-200 bg-slate-50 p-4"
        >
          <p class="text-sm font-semibold text-slate-900">{{ section.name }}</p>
          <div v-if="section.items?.length" class="mt-2 divide-y divide-slate-200">
            <div
              v-for="(item, itemIndex) in section.items"
              :key="`${item.name}-${itemIndex}`"
              class="py-2"
            >
              <div class="flex items-start justify-between gap-3">
                <div>
                  <p class="text-sm font-medium text-slate-800">{{ item.name }}</p>
                  <p v-if="item.description" class="mt-0.5 text-xs text-slate-500">
                    {{ item.description }}
                  </p>
                </div>
                <span
                  v-if="item.price != null"
                  class="shrink-0 text-sm font-semibold text-cyan-700"
                >
                  ${{ formatPrice(item.price) }}
                </span>
              </div>
            </div>
          </div>
          <p v-else class="mt-2 text-xs text-slate-400">No items in this section.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  details: {
    type: Object,
    default: () => ({}),
  },
});

const menuSections = computed(() => {
  const sections = props.details?.menu?.sections;
  return Array.isArray(sections) ? sections : [];
});

function formatPrice(value) {
  const numericValue = Number(value);
  return Number.isFinite(numericValue) ? numericValue.toFixed(2) : "0.00";
}
</script>
