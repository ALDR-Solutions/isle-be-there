<template>
  <div class="bg-slate-50 min-h-screen">
    <LoadingSpinner v-if="loading" />

    <div v-else-if="error" class="mx-auto max-w-4xl px-4 py-16 sm:px-6 lg:px-8">
      <InlineAlert :message="error.message" />
    </div>

    <div v-else-if="!listing" class="mx-auto max-w-4xl px-4 py-16 sm:px-6 lg:px-8">
      <PageStatus
        title="Listing not found"
        description="The listing may have been removed or is no longer available."
        icon="?"
      >
        <template #actions>
          <router-link
            to="/listings"
            class="inline-flex items-center justify-center rounded-2xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
          >
            Back to Listings
          </router-link>
        </template>
      </PageStatus>
    </div>

    <div v-else>
      <div class="relative h-72 w-full overflow-hidden bg-slate-200 sm:h-96 lg:h-[480px]">
        <AppImage
          :src="listingImage"
          :alt="listing.title"
          wrapper-class="h-full w-full"
          img-class="h-full w-full"
          fallback-label="Image unavailable"
        />
        <div class="absolute inset-0 bg-gradient-to-t from-slate-950/60 via-transparent to-transparent"></div>
        <div class="absolute left-4 top-4 sm:left-6 lg:left-8">
          <router-link
            to="/listings"
            class="inline-flex items-center gap-2 rounded-2xl border border-white/20 bg-white/10 px-4 py-2 text-sm font-semibold text-white backdrop-blur-md transition hover:bg-white/20"
          >
            Back
          </router-link>
        </div>
        <div class="absolute bottom-6 left-4 right-4 sm:left-6 sm:right-6 lg:left-8 lg:right-8">
          <p class="text-sm font-semibold uppercase tracking-[0.25em] text-cyan-300">
            {{ listing.address?.country }}
          </p>
          <h1 class="mt-1 text-2xl font-bold text-white drop-shadow sm:text-3xl lg:text-4xl">
            {{ listing.title }}
          </h1>
        </div>
      </div>

      <div class="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
          <div class="space-y-6 lg:col-span-2">
            <SurfaceCard>
              <div class="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p class="flex items-center gap-1.5 text-sm text-slate-500">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-cyan-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    {{ locationText || 'Location unavailable' }}
                  </p>
                </div>
                <div v-if="listing.avg_rating" class="flex items-center gap-2">
                  <div class="flex">
                    <svg
                      v-for="i in 5"
                      :key="i"
                      class="h-4 w-4"
                      :class="i <= Math.round(listing.avg_rating) ? 'text-amber-400' : 'text-slate-200'"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  </div>
                  <span class="text-sm font-semibold text-slate-700">{{ listing.avg_rating.toFixed(1) }}</span>
                  <span v-if="listing.review_count" class="text-sm text-slate-400">
                    ({{ listing.review_count }} {{ listing.review_count === 1 ? 'review' : 'reviews' }})
                  </span>
                </div>
              </div>
            </SurfaceCard>

            <SurfaceCard>
              <p class="text-sm font-semibold uppercase tracking-[0.25em] text-cyan-600">About this place</p>
              <p class="mt-3 text-base leading-7 text-slate-600">
                {{ listing.description || 'No description provided.' }}
              </p>
            </SurfaceCard>
          </div>

          <div>
            <SurfaceCard class="sticky top-24">
              <p class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-400">Starting from</p>
              <div class="mt-1 flex items-end gap-1">
                <span class="text-4xl font-bold text-slate-900">{{ formatCurrency(listing.base_price) }}</span>
                <span class="mb-1 text-sm text-slate-400">/ night</span>
              </div>
              <div class="my-6 border-t border-slate-100"></div>
              <button
                type="button"
                class="w-full rounded-2xl bg-slate-900 py-3.5 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-slate-800"
                @click="toastStore.show('Booking flow is not implemented yet.', 'info')"
              >
                Book Now
              </button>
              <p class="mt-3 text-center text-xs text-slate-400">You won't be charged yet</p>
            </SurfaceCard>
          </div>
        </div>

        <div class="mt-10">
          <div class="mb-6">
            <p class="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-600">Guest Feedback</p>
            <h2 class="mt-2 text-2xl font-bold text-slate-900">Reviews</h2>
          </div>

          <PageStatus
            v-if="reviews.length === 0"
            title="No reviews yet"
            description="Be the first to share your experience."
            icon="*"
          />

          <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <SurfaceCard v-for="review in reviews" :key="review.id">
              <div class="flex items-start justify-between gap-4">
                <div class="flex items-center gap-3">
                  <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-cyan-50 text-sm font-bold text-cyan-700">
                    {{ review.user?.username ? review.user.username.charAt(0).toUpperCase() : '?' }}
                  </div>
                  <div>
                    <p class="text-sm font-semibold text-slate-900">{{ review.user?.username || 'Anonymous' }}</p>
                    <p class="text-xs text-slate-400">{{ formatDate(review.created_at) }}</p>
                  </div>
                </div>
                <div class="flex shrink-0">
                  <svg
                    v-for="i in 5"
                    :key="i"
                    class="h-4 w-4"
                    :class="i <= review.rating ? 'text-amber-400' : 'text-slate-200'"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                </div>
              </div>
              <p v-if="review.comment" class="mt-4 text-sm leading-6 text-slate-600">
                {{ review.comment }}
              </p>
            </SurfaceCard>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppImage from '@/components/ui/AppImage.vue'
import InlineAlert from '@/components/ui/InlineAlert.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import PageStatus from '@/components/ui/PageStatus.vue'
import SurfaceCard from '@/components/ui/SurfaceCard.vue'
import { useAsyncData } from '@/composables/useAsyncData'
import { listingsService } from '@/services/listingsService'
import { reviewsService } from '@/services/reviewsService'
import { useToastStore } from '@/stores/toast'
import { formatCurrency, formatDate } from '@/utils/formatters'
import { getListingImage, getListingLocation } from '@/utils/listings'

const route = useRoute()
const toastStore = useToastStore()

const state = useAsyncData(async ({ signal }) => {
  const [listing, reviews] = await Promise.all([
    listingsService.getById(route.params.id, { signal }),
    reviewsService.getAll({ listing_id: route.params.id }, { signal }),
  ])

  return { listing, reviews }
}, {
  initialData: { listing: null, reviews: [] },
  isEmpty: (value) => !value?.listing,
})
const { error, loading } = state

const listing = computed(() => state.data.value?.listing || null)
const reviews = computed(() => state.data.value?.reviews || [])
const listingImage = computed(() => getListingImage(listing.value))
const locationText = computed(() => getListingLocation(listing.value))

onMounted(() => {
  state.load().catch(() => {})
})
</script>
