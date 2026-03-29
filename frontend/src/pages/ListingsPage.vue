<template>
  <div class="bg-slate-50 min-h-screen">
    <PageHeader
      eyebrow="Browse All"
      title="Explore Listings"
      description="Discover handpicked stays, adventures, and coastal escapes across the Caribbean."
    />

    <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <LoadingSpinner v-if="loading" />

      <InlineAlert v-else-if="error" :message="error.message" />

      <PageStatus
        v-else-if="isEmpty"
        title="No listings available yet."
        description="Check back soon for new destinations."
        icon="[]"
      />

      <div v-else class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <DestinationCard
          v-for="listing in data"
          :key="listing.id"
          :listing="listing"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import DestinationCard from '@/components/DestinationCard.vue'
import InlineAlert from '@/components/ui/InlineAlert.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import PageStatus from '@/components/ui/PageStatus.vue'
import { useAsyncData } from '@/composables/useAsyncData'
import { listingsService } from '@/services/listingsService'

const state = useAsyncData(
  ({ signal }) => listingsService.getAll({}, { signal }),
  { initialData: [] }
)
const { data, error, isEmpty, loading } = state

onMounted(() => {
  state.load().catch(() => {})
})
</script>
