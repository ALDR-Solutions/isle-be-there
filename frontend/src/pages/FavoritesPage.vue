<template>
  <div class="bg-slate-50 min-h-screen">
    <PageHeader
      eyebrow="Saved Places"
      title="My Favorites"
      description="Keep your favorite listings close so planning your trip stays easy."
    />

    <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <LoadingSpinner v-if="loading" />

      <InlineAlert v-else-if="error" :message="error.message || 'Unable to load favorites right now.'" />

      <PageStatus
        v-else-if="favorites.length === 0"
        title="No favorites yet"
        description="Start exploring listings and save the ones you love."
        icon="*"
      >
        <template #actions>
          <router-link
            to="/listings"
            class="inline-flex items-center justify-center rounded-2xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
          >
            Browse Listings
          </router-link>
        </template>
      </PageStatus>

      <transition-group
        v-else
        name="card"
        tag="div"
        class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3"
      >
        <DestinationCard
          v-for="favorite in favorites"
          :key="favorite.id"
          :listing="favorite.listing"
        />
      </transition-group>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import DestinationCard from '@/components/DestinationCard.vue'
import InlineAlert from '@/components/ui/InlineAlert.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import PageStatus from '@/components/ui/PageStatus.vue'
import { useFavouritesStore } from '@/stores/favourites'

const favouritesStore = useFavouritesStore()
const error = ref(null)

const favorites = computed(() => favouritesStore.items)
const loading = computed(() => favouritesStore.loading && !favouritesStore.loaded)

onMounted(async () => {
  try {
    await favouritesStore.fetchAll()
  } catch (err) {
    error.value = err
  }
})
</script>

<style scoped>
.card-enter-active,
.card-leave-active {
  transition: all 0.3s ease;
}

.card-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

.card-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

.card-move {
  transition: transform 0.3s ease;
}
</style>
