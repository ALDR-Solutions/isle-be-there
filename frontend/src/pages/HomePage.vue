<template>
  <div class="bg-slate-50 text-slate-900">
    <section class="relative -mt-20 flex min-h-screen w-full items-center overflow-hidden pt-20">
      <transition-group name="fade" tag="div" class="absolute inset-0">
        <div
          v-for="(img, index) in heroImages"
          v-show="currentSlide === index"
          :key="img"
          class="absolute inset-0 bg-cover bg-center"
          :style="{ backgroundImage: `url(${img})` }"
        >
          <div class="absolute inset-0 bg-slate-950/55"></div>
          <div class="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(34,211,238,0.18),_transparent_40%)]"></div>
        </div>
      </transition-group>

      <div class="relative z-10 mx-auto flex w-full max-w-7xl items-center justify-center px-4 sm:px-6 lg:px-8">
        <div class="flex max-w-3xl flex-col items-center text-center">
          <h1 class="text-4xl font-bold leading-tight text-white drop-shadow-lg sm:text-5xl lg:text-7xl">
            Discover the Paradise of the Caribbean Islands
          </h1>

          <p class="mt-6 max-w-2xl text-base leading-7 text-slate-200 sm:text-lg">
            Experience a once in a lifetime trip to the hidden gems of the Caribbean with stays,
            adventures, and coastal escapes curated for modern travelers.
          </p>

          <div class="mt-10 flex flex-wrap gap-4 justify-center">
            <router-link
              to="/listings"
              class="inline-flex items-center justify-center rounded-2xl border border-white/20 bg-white/10 px-8 py-4 text-sm font-semibold text-white backdrop-blur-md transition hover:-translate-y-0.5 hover:bg-white/15"
            >
              Plan Your Trip Now
            </router-link>
          </div>
        </div>
      </div>

      <div class="absolute bottom-8 left-1/2 z-10 flex -translate-x-1/2 gap-3">
        <button
          v-for="(_, index) in heroImages"
          :key="index"
          type="button"
          class="h-3 rounded-full transition-all duration-500"
          :class="currentSlide === index ? 'w-10 bg-cyan-300' : 'w-3 bg-white/45 hover:bg-white/70'"
          @click="currentSlide = index"
        />
      </div>
    </section>

    <section class="relative px-4 py-20 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-7xl">
        <div class="mb-12 flex flex-col items-start justify-between gap-6 lg:flex-row lg:items-end">
          <div class="max-w-2xl">
            <p class="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-600">Featured Destinations</p>
            <h2 class="mt-3 text-3xl font-bold text-slate-900 sm:text-4xl">Recommended for You</h2>
            <p class="mt-4 text-base leading-7 text-slate-600">
              Browse these destinations curated around your travel interests.
            </p>
          </div>

          <div class="flex items-center gap-3">
            <button
              type="button"
              class="flex h-12 w-12 items-center justify-center rounded-2xl border border-slate-200 bg-white text-slate-700 shadow-sm transition hover:-translate-y-0.5 hover:border-slate-300 hover:text-slate-950 disabled:cursor-not-allowed disabled:opacity-40"
              :disabled="carouselIndex === 0"
              @click="prevSlide"
            >
              <
            </button>

            <button
              type="button"
              class="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-900 text-white shadow-lg shadow-slate-900/10 transition hover:-translate-y-0.5 hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-300"
              :disabled="carouselIndex >= maxIndex"
              @click="nextSlide"
            >
              >
            </button>
          </div>
        </div>

        <LoadingSpinner v-if="listingsLoading" />

        <InlineAlert v-else-if="listingsError" :message="listingsError.message" />

        <PageStatus
          v-else-if="listings.length === 0"
          title="No destinations available"
          description="Try again in a little while for fresh recommendations."
          icon="[]"
        />

        <div
          v-else
          ref="carouselContainerRef"
          class="overflow-hidden"
          @touchstart.passive="onTouchStart"
          @touchend.passive="onTouchEnd"
        >
          <div
            class="flex gap-6 transition-transform duration-500 ease-out"
            :style="{ transform: `translateX(-${carouselOffset}px)` }"
          >
            <div
              v-for="listing in listings"
              :key="listing.id"
              class="shrink-0"
              :style="{ width: `${cardWidth}px` }"
            >
              <DestinationCard :listing="listing" />
            </div>
          </div>
        </div>
      </div>
    </section>

    <section
      class="relative mx-4 overflow-hidden rounded-[2rem] sm:mx-6 lg:mx-8"
      style="background-image: linear-gradient(rgba(2, 6, 23, 0.78), rgba(2, 6, 23, 0.82)), url('/images/bay.jpg'); background-size: cover; background-position: center;"
    >
      <div class="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(34,211,238,0.16),_transparent_35%)]"></div>

      <div class="relative mx-auto flex min-h-[460px] max-w-4xl flex-col items-center justify-center px-6 py-20 text-center text-white">
        <p class="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-300">Start Exploring</p>
        <h2 class="mt-4 text-3xl font-bold sm:text-4xl lg:text-5xl">Ready for your Caribbean adventure?</h2>
        <p class="mt-5 max-w-2xl text-base leading-7 text-slate-200 sm:text-lg">
          Join thousands of travelers discovering places to stay, local gems, and unforgettable
          island experiences.
        </p>

        <div class="mt-10 flex flex-wrap justify-center gap-4">
          <router-link
            to="/listings"
            class="rounded-2xl bg-cyan-400 px-8 py-4 text-sm font-semibold text-slate-950 transition hover:-translate-y-0.5 hover:bg-cyan-300"
          >
            Explore Listings
          </router-link>
        </div>
      </div>
    </section>

    <section class="px-4 py-20 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-7xl">
        <div class="mb-10 max-w-2xl">
          <p class="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-600">Popular Destinations</p>
          <h2 class="mt-3 text-3xl font-bold text-slate-900 sm:text-4xl">Travel inspiration, styled more cleanly</h2>
        </div>

        <div class="grid gap-6 md:grid-cols-3">
          <SurfaceCard padding="lg">
            <p class="text-sm font-semibold text-slate-500">Beach Escapes</p>
            <h3 class="mt-3 text-xl font-bold text-slate-900">Crystal water and quiet mornings</h3>
            <p class="mt-3 text-sm leading-6 text-slate-600">
              Discover coastlines, hidden coves, and stays built for slow island days.
            </p>
          </SurfaceCard>

          <SurfaceCard padding="lg">
            <p class="text-sm font-semibold text-slate-500">Cultural Spots</p>
            <h3 class="mt-3 text-xl font-bold text-slate-900">Local rhythm, food, and festivals</h3>
            <p class="mt-3 text-sm leading-6 text-slate-600">
              Explore destinations known for history, music, and authentic local experiences.
            </p>
          </SurfaceCard>

          <SurfaceCard padding="lg">
            <p class="text-sm font-semibold text-slate-500">Nature Retreats</p>
            <h3 class="mt-3 text-xl font-bold text-slate-900">Rainforests, cliffs, and trails</h3>
            <p class="mt-3 text-sm leading-6 text-slate-600">
              Perfect for travelers who want hiking, views, and a little more adventure.
            </p>
          </SurfaceCard>
        </div>
      </div>
    </section>

    <section class="px-4 pb-20 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-7xl rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm sm:p-10">
        <div class="max-w-2xl">
          <p class="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-600">Hotels and Villas</p>
          <h2 class="mt-3 text-3xl font-bold text-slate-900 sm:text-4xl">Most luxurious places to stay on your trip</h2>
          <p class="mt-4 text-base leading-7 text-slate-600">
            Keep this section ready for future featured collections focused on premium stays and destination experiences.
          </p>
        </div>
      </div>
    </section>

    <InterestsDialog
      v-model="showInterestsDialog"
      @interests-saved="handleInterestsSaved"
    />
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import DestinationCard from '@/components/DestinationCard.vue'
import InlineAlert from '@/components/ui/InlineAlert.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import PageStatus from '@/components/ui/PageStatus.vue'
import SurfaceCard from '@/components/ui/SurfaceCard.vue'
import { useElementSize } from '@/composables/useElementSize'
import { useAsyncData } from '@/composables/useAsyncData'
import InterestsDialog from '@/features/interests/InterestsDialog.vue'
import { listingsService } from '@/services/listingsService'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const heroImages = [
  '/images/trinidad.jpg',
  '/images/barbados.jpg',
  '/images/carib-bkg.jpg',
  '/images/beach-bkg.jpg',
  '/images/island-bkg.jpg',
]

const currentSlide = ref(0)
const showInterestsDialog = ref(false)
let heroInterval = null

const listingsState = useAsyncData(async ({ signal }) => {
  if (authStore.isAuthenticated) {
    try {
      return await listingsService.getPersonalized({ limit: 20 }, { signal })
    } catch {
      return listingsService.getAll({ limit: 20 }, { signal })
    }
  }

  return listingsService.getAll({ limit: 20 }, { signal })
}, {
  initialData: [],
})
const { data: listings, error: listingsError, loading: listingsLoading } = listingsState

const carouselContainerRef = ref(null)
const { width: carouselWidth } = useElementSize(carouselContainerRef)
const carouselIndex = ref(0)
const gap = 24
let touchStartX = 0

const visibleCount = computed(() => {
  if (carouselWidth.value <= 576) return 1
  if (carouselWidth.value <= 1000) return 2
  return 3
})

const cardWidth = computed(() => {
  const width = carouselWidth.value || 900
  return (width - gap * (visibleCount.value - 1)) / visibleCount.value
})

const maxIndex = computed(() => Math.max(0, listings.value.length - visibleCount.value))
const carouselOffset = computed(() => carouselIndex.value * (cardWidth.value + gap))

onMounted(async () => {
  heroInterval = window.setInterval(() => {
    currentSlide.value = (currentSlide.value + 1) % heroImages.length
  }, 4000)

  await listingsState.load().catch(() => {})

  if (authStore.isAuthenticated && !authStore.user?.interests_handled) {
    window.setTimeout(() => {
      showInterestsDialog.value = true
    }, 700)
  }
})

onBeforeUnmount(() => {
  clearInterval(heroInterval)
})

function prevSlide() {
  if (carouselIndex.value > 0) {
    carouselIndex.value -= 1
  }
}

function nextSlide() {
  if (carouselIndex.value < maxIndex.value) {
    carouselIndex.value += 1
  }
}

function onTouchStart(event) {
  touchStartX = event.touches[0].clientX
}

function onTouchEnd(event) {
  const delta = touchStartX - event.changedTouches[0].clientX
  if (Math.abs(delta) < 50) return
  if (delta > 0) nextSlide()
  else prevSlide()
}

async function handleInterestsSaved() {
  await authStore.fetchUser()
  await listingsState.refresh().catch(() => {})
  await nextTick()
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 1s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
