<template>
  <div
    class="group overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-md"
    :class="{ 'opacity-60': listing.status === 'inactive' }"
  >
    <div class="relative h-48 overflow-hidden bg-slate-100">
      <AppImage
        :src="listingImage"
        :alt="listing.title"
        wrapper-class="h-48 w-full"
        img-class="transition duration-500 group-hover:scale-105"
      />
      <div class="absolute top-3 left-3">
        <StatusBadge :label="statusLabel" :tone="statusTone" />
      </div>
      <div v-if="typeName" class="absolute top-3 right-3">
        <span class="rounded-xl bg-slate-900/70 px-3 py-1 text-xs font-semibold text-white backdrop-blur-sm">
          {{ typeName }}
        </span>
      </div>
    </div>

    <div class="p-6">
      <h3 class="text-base font-bold leading-snug text-slate-900">{{ listing.title }}</h3>
      <p class="mt-1 flex items-center gap-1 text-sm text-slate-500">
        <span class="line-clamp-2">{{ locationText }}</span>
      </p>
      <p class="mt-2 line-clamp-2 text-sm text-slate-500">{{ listing.description }}</p>

      <div class="mt-4 flex items-center justify-between">
        <div>
          <span class="text-lg font-bold text-slate-900">{{ formattedPrice }}</span>
          <span class="text-sm text-slate-400"> / night</span>
        </div>
      </div>

      <div class="mt-4 flex gap-2 border-t border-slate-100 pt-4">
        <button
          v-if="listing.status !== 'inactive'"
          type="button"
          class="flex-1 rounded-2xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50"
          @click="$emit('edit', listing)"
        >
          Edit
        </button>
        <button
          v-if="listing.status !== 'inactive'"
          type="button"
          class="flex-1 rounded-2xl border border-red-100 px-4 py-2 text-sm font-semibold text-red-500 transition hover:bg-red-50"
          @click="$emit('archive', listing)"
        >
          Archive
        </button>
        <button
          v-if="listing.status === 'inactive'"
          type="button"
          class="flex-1 rounded-2xl border border-emerald-100 px-4 py-2 text-sm font-semibold text-emerald-600 transition hover:bg-emerald-50"
          @click="$emit('unarchive', listing)"
        >
          Unarchive
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import AppImage from '@/components/ui/AppImage.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import { formatCurrency } from '@/utils/formatters'
import { getListingImage, getListingLocation, getListingTypeName } from '@/utils/listings'

const props = defineProps({
  listing: {
    type: Object,
    required: true,
  },
  businessTypes: {
    type: Array,
    default: () => [],
  },
})

defineEmits(['edit', 'archive', 'unarchive'])

const listingImage = computed(() => getListingImage(props.listing))
const locationText = computed(() => getListingLocation(props.listing))
const typeName = computed(() => getListingTypeName(props.listing.business_type, props.businessTypes))
const formattedPrice = computed(() => formatCurrency(props.listing.base_price))
const statusLabel = computed(() => {
  if (props.listing.status === 'active') return 'Active'
  if (props.listing.status === 'pending') return 'Pending Approval'
  if (props.listing.status === 'inactive') return 'Archived'
  return props.listing.status
})
const statusTone = computed(() => {
  if (props.listing.status === 'active') return 'success'
  if (props.listing.status === 'pending') return 'warning'
  if (props.listing.status === 'inactive') return 'neutral'
  return 'neutral'
})
</script>
