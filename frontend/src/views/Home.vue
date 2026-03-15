<template>
  <div class="bg-slate-50 text-slate-900">
    <section class="relative -mt-20 flex min-h-screen w-full items-center overflow-hidden pt-20">
      <transition-group name="fade" tag="div" class="absolute inset-0">
        <div
          v-for="(img, i) in heroImages"
          v-show="currentSlide === i"
          :key="i"
          class="absolute inset-0 bg-cover bg-center"
          :style="{ backgroundImage: `url(${img})` }"
        >
          <div class="absolute inset-0 bg-slate-950/55"></div>
          <div class="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(34,211,238,0.18),_transparent_40%)]"></div>
        </div>
      </transition-group>

      <div class="relative z-10 mx-auto flex w-full max-w-7xl items-center px-4 sm:px-6 lg:px-8">
        <div class="max-w-3xl align-content-center">

          <h1 class="text-4xl font-bold leading-tight text-white drop-shadow-lg sm:text-5xl lg:text-7xl">
            Discover the Paradise of the Caribbean Islands
          </h1>

          <p class="mt-6 max-w-2xl text-base leading-7 text-slate-200 sm:text-lg">
            Experience a once in a lifetime trip to the hidden gems of the Caribbean with stays,
            adventures, and coastal escapes curated for modern travelers.
          </p>

          <div class="mt-10 flex flex-wrap gap-4">
            <router-link
              to="/listings"
              class="inline-flex items-center justify-center rounded-2xl bg-cyan-400 px-8 py-4 text-sm font-semibold text-slate-950 shadow-xl shadow-cyan-500/20 transition hover:-translate-y-0.5 hover:bg-cyan-300"
            >
              Plan Your Trip Now
            </router-link>

            <router-link
              to="/register"
              class="inline-flex items-center justify-center rounded-2xl border border-white/20 bg-white/10 px-8 py-4 text-sm font-semibold text-white backdrop-blur-md transition hover:-translate-y-0.5 hover:bg-white/15"
            >
              Create an Account
            </router-link>
          </div>
        </div>
      </div>

      <div class="absolute bottom-8 left-1/2 z-10 flex -translate-x-1/2 gap-3">
        <button
          v-for="(_, i) in heroImages"
          :key="i"
          @click="currentSlide = i"
          class="h-3 rounded-full transition-all duration-300"
          :class="currentSlide === i ? 'w-10 bg-cyan-300' : 'w-3 bg-white/45 hover:bg-white/70'"
        />
      </div>
    </section>

    <section class="relative px-4 py-20 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-7xl">
        <div class="mb-12 flex flex-col items-start justify-between gap-6 lg:flex-row lg:items-end">
          <div class="max-w-2xl">
            <p class="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-600">
              Featured Destinations
            </p>
            <h2 class="mt-3 text-3xl font-bold text-slate-900 sm:text-4xl">
              Places worth opening a new tab for
            </h2>
            <p class="mt-4 text-base leading-7 text-slate-600">
              Browse standout stays and destinations travelers are most excited to explore next.
            </p>
          </div>

          <div class="flex items-center gap-3">
            <button
              @click="prevSlide"
              :disabled="carouselIndex === 0"
              class="flex h-12 w-12 items-center justify-center rounded-2xl border border-slate-200 bg-white text-slate-700 shadow-sm transition hover:-translate-y-0.5 hover:border-slate-300 hover:text-slate-950 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            <button
              @click="nextSlide"
              :disabled="carouselIndex >= maxIndex"
              class="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-900 text-white shadow-lg shadow-slate-900/10 transition hover:-translate-y-0.5 hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-300"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>

        <div v-if="loading" class="rounded-3xl border border-slate-200 bg-white px-6 py-16 text-center text-slate-500 shadow-sm">
          Loading destinations...
        </div>

        <div v-else-if="listings.length === 0" class="rounded-3xl border border-slate-200 bg-white px-6 py-16 text-center text-slate-500 shadow-sm">
          No destinations available.
        </div>

        <div v-else class="relative">
          <div class="overflow-hidden">
            <div
              ref="trackRef"
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
      </div>
    </section>

    <section
      class="relative mx-4 overflow-hidden rounded-[2rem] sm:mx-6 lg:mx-8"
      style="background-image: linear-gradient(rgba(2, 6, 23, 0.78), rgba(2, 6, 23, 0.82)), url('/images/bay.jpg'); background-size: cover; background-position: center;"
    >
      <div class="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(34,211,238,0.16),_transparent_35%)]"></div>

      <div class="relative mx-auto flex min-h-[460px] max-w-4xl flex-col items-center justify-center px-6 py-20 text-center text-white">
        <p class="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-300">
          Start Exploring
        </p>
        <h2 class="mt-4 text-3xl font-bold sm:text-4xl lg:text-5xl">
          Ready for your Caribbean adventure?
        </h2>
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

          <router-link
            to="/register"
            class="rounded-2xl border border-white/20 bg-white/10 px-8 py-4 text-sm font-semibold text-white backdrop-blur-md transition hover:-translate-y-0.5 hover:bg-white/15"
          >
            Sign Up
          </router-link>
        </div>
      </div>
    </section>

    <section class="px-4 py-20 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-7xl">
        <div class="mb-10 max-w-2xl">
          <p class="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-600">
            Popular Destinations
          </p>
          <h2 class="mt-3 text-3xl font-bold text-slate-900 sm:text-4xl">
            Travel inspiration, styled more cleanly
          </h2>
        </div>

        <div class="grid gap-6 md:grid-cols-3">
          <div class="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
            <p class="text-sm font-semibold text-slate-500">Beach Escapes</p>
            <h3 class="mt-3 text-xl font-bold text-slate-900">Crystal water and quiet mornings</h3>
            <p class="mt-3 text-sm leading-6 text-slate-600">
              Discover coastlines, hidden coves, and stays built for slow island days.
            </p>
          </div>

          <div class="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
            <p class="text-sm font-semibold text-slate-500">Cultural Spots</p>
            <h3 class="mt-3 text-xl font-bold text-slate-900">Local rhythm, food, and festivals</h3>
            <p class="mt-3 text-sm leading-6 text-slate-600">
              Explore destinations known for history, music, and authentic local experiences.
            </p>
          </div>

          <div class="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
            <p class="text-sm font-semibold text-slate-500">Nature Retreats</p>
            <h3 class="mt-3 text-xl font-bold text-slate-900">Rainforests, cliffs, and trails</h3>
            <p class="mt-3 text-sm leading-6 text-slate-600">
              Perfect for travelers who want hiking, views, and a little more adventure.
            </p>
          </div>
        </div>
      </div>
    </section>

    <section class="px-4 pb-20 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-7xl rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm sm:p-10">
        <div class="max-w-2xl">
          <p class="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-600">
            Hotels and Villas
          </p>
          <h2 class="mt-3 text-3xl font-bold text-slate-900 sm:text-4xl">
            Most luxurious places to stay on your trip
          </h2>
          <p class="mt-4 text-base leading-7 text-slate-600">
            Keep this section if you want a future featured collection for premium stays, villas,
            and high-end destination experiences.
          </p>
        </div>
      </div>
    </section>

    <InterestsModal v-if="showInterestsModal" @close="showInterestsModal = false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { listingsAPI } from '../services/api'
import { useAuthStore } from '../stores/auth'
import DestinationCard from '../components/DestinationCard.vue'
import InterestsModal from '../components/InterestsModal.vue'

const authStore = useAuthStore()

const heroImages = [
  '/images/trinidad.jpg',
  '/images/barbados.jpg',
  '/images/carib-bkg.jpg',
  '/images/beach-bkg.jpg',
  '/images/island-bkg.jpg',
]

const currentSlide = ref(0)
let heroInterval = null

const listings = ref([])
const loading = ref(true)

const trackRef = ref(null)
const carouselIndex = ref(0)
const cardWidth = ref(350)
const gap = 24

const showInterestsModal = ref(false)

onMounted(() => {
  heroInterval = setInterval(() => {
    currentSlide.value = (currentSlide.value + 1) % heroImages.length
  }, 4000)

  fetchListings()
  window.addEventListener('resize', updateCardWidth)
  updateCardWidth()
})

onUnmounted(() => {
  clearInterval(heroInterval)
  window.removeEventListener('resize', updateCardWidth)
})

async function fetchListings() {
  try {
    const res = await listingsAPI.getAll()
    listings.value = res.data
  } catch (e) {
    console.error('Failed to load listings', e)
  } finally {
    loading.value = false
  }
}

function visibleCount() {
  if (window.innerWidth <= 576) return 1
  if (window.innerWidth <= 1000) return 2
  return 3
}

function updateCardWidth() {
  const containerWidth = trackRef.value?.parentElement?.offsetWidth || 900
  const count = visibleCount()
  cardWidth.value = (containerWidth - gap * (count - 1)) / count

  if (carouselIndex.value > maxIndex.value) {
    carouselIndex.value = maxIndex.value
  }
}

const maxIndex = computed(() => Math.max(0, listings.value.length - visibleCount()))
const carouselOffset = computed(() => carouselIndex.value * (cardWidth.value + gap))

function prevSlide() {
  if (carouselIndex.value > 0) carouselIndex.value--
}

function nextSlide() {
  if (carouselIndex.value < maxIndex.value) carouselIndex.value++
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
