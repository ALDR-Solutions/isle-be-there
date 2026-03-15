<template>
  <div>
    <!-- Hero Section -->
    <section class="relative h-screen w-full overflow-hidden -mt-16 pt-16">
      <!-- Carousel images -->
      <transition-group name="fade" tag="div" class="absolute inset-0">
        <div
          v-for="(img, i) in heroImages"
          v-show="currentSlide === i"
          :key="i"
          class="absolute inset-0 bg-cover bg-center transition-opacity duration-1000"
          :style="{ backgroundImage: `url(${img})` }"
        >
          <div class="absolute inset-0 bg-gradient-to-b from-black/40 to-black/60"></div>
        </div>
      </transition-group>

      <!-- Hero Content -->
      <div class="relative z-10 flex items-center justify-center h-full text-center text-white px-4">
        <div>
          <h1 class="text-4xl md:text-6xl font-bold drop-shadow-lg mb-2">
            Discover the Paradise of the Caribbean Islands
          </h1>
          <p class="text-lg md:text-xl opacity-90 mb-10 drop-shadow">
            Experience a once in a lifetime trip to the hidden gems of the Caribbean
          </p>
          <router-link
            to="/listings"
            class="inline-flex items-center gap-3 px-8 py-4 bg-white/15 backdrop-blur-md border border-white/20 text-white font-semibold hover:bg-white/25 hover:-translate-y-0.5 hover:shadow-lg transition-all duration-300"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M4 6h16M4 10h16M4 14h16M4 18h16" />
            </svg>
            PLAN YOUR TRIP NOW
          </router-link>
        </div>
      </div>

      <!-- Slide indicators -->
      <div class="absolute bottom-6 left-1/2 -translate-x-1/2 z-10 flex gap-2">
        <button
          v-for="(_, i) in heroImages"
          :key="i"
          @click="currentSlide = i"
          class="w-3 h-3 rounded-full transition-all duration-300"
          :class="currentSlide === i ? 'bg-white scale-110' : 'bg-white/50'"
        />
      </div>
    </section>

    <!-- Featured Destinations -->
    <section class="py-16 px-4">
      <div class="max-w-7xl mx-auto">
        <h2 class="text-center text-3xl md:text-4xl font-bold text-gray-900 mb-4">Featured Destinations</h2>
        <div class="w-20 h-0.5 bg-teal-700 mx-auto opacity-80 mb-4"></div>
        <p class="text-center text-lg text-gray-500 max-w-xl mx-auto mb-10">
          Come and check out these places you may like to visit
        </p>

        <div v-if="loading" class="text-center py-8 text-gray-500">Loading destinations...</div>

        <div v-else-if="listings.length === 0" class="text-center py-8 text-gray-500">
          No destinations available.
        </div>

        <!-- Carousel -->
        <div v-else class="relative px-12">
          <button
            @click="prevSlide"
            :disabled="carouselIndex === 0"
            class="absolute left-0 top-1/2 -translate-y-1/2 z-10 w-11 h-11 rounded-full bg-teal-700 text-white flex items-center justify-center shadow-lg hover:scale-110 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          <div class="overflow-hidden">
            <div
              class="flex gap-6 transition-transform duration-500 ease-in-out"
              :style="{ transform: `translateX(-${carouselOffset}px)` }"
              ref="trackRef"
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

          <button
            @click="nextSlide"
            :disabled="carouselIndex >= maxIndex"
            class="absolute right-0 top-1/2 -translate-y-1/2 z-10 w-11 h-11 rounded-full bg-teal-700 text-white flex items-center justify-center shadow-lg hover:scale-110 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="relative w-full h-[500px] flex items-center bg-fixed bg-cover bg-center"
      style="background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url('/images/bay.jpg');">
      <div class="max-w-2xl mx-auto text-center text-white px-4">
        <h2 class="text-3xl md:text-4xl font-bold mb-3">Ready for your Caribbean Adventure</h2>
        <p class="text-lg opacity-90 mb-8">Join Thousands of Travellers</p>
        <div class="flex flex-wrap justify-center gap-5">
          <router-link to="/listings"
            class="bg-teal-700 text-white px-10 py-5 rounded-full font-semibold hover:-translate-y-1 hover:shadow-xl transition-all duration-300">
            Explore Listings
          </router-link>
          <router-link to="/register"
            class="border-2 border-white/30 text-white px-10 py-5 rounded-full font-semibold hover:bg-white/10 hover:border-white/50 hover:-translate-y-1 transition-all duration-300">
            Sign Up
          </router-link>
        </div>
      </div>
    </section>

    <!-- Popular Destinations (placeholder) -->
    <section class="py-16 px-4">
      <div class="max-w-7xl mx-auto">
        <h2 class="text-center text-3xl md:text-4xl font-bold text-gray-900 mb-4">Popular Destinations</h2>
        <div class="w-20 h-0.5 bg-teal-700 mx-auto opacity-80"></div>
      </div>
    </section>

    <!-- Hotels Section (placeholder) -->
    <section class="py-16 px-4">
      <div class="max-w-7xl mx-auto text-center">
        <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Hotels and Villas</h2>
        <div class="w-20 h-0.5 bg-teal-700 mx-auto opacity-80 mb-4"></div>
        <p class="text-lg text-gray-500">Most luxurious places to stay on your trip</p>
      </div>
    </section>

    <!-- Interests Modal -->
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

// Hero carousel
const heroImages = [
  '/images/trinidad.jpg',
  '/images/barbados.jpg',
  '/images/carib-bkg.jpg',
  '/images/beach-bkg.jpg',
  '/images/island-bkg.jpg',
]
const currentSlide = ref(0)
let heroInterval = null

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

// Listings
const listings = ref([])
const loading = ref(true)

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

// Card carousel
const trackRef = ref(null)
const carouselIndex = ref(0)
const cardWidth = ref(350)
const gap = 24

function visibleCount() {
  if (window.innerWidth <= 576) return 1
  if (window.innerWidth <= 1000) return 2
  return 3
}

function updateCardWidth() {
  const containerWidth = trackRef.value?.parentElement?.offsetWidth || 900
  const count = visibleCount()
  cardWidth.value = (containerWidth - gap * (count - 1)) / count
  // Clamp index
  if (carouselIndex.value > maxIndex.value) carouselIndex.value = maxIndex.value
}

const maxIndex = computed(() => Math.max(0, listings.value.length - visibleCount()))
const carouselOffset = computed(() => carouselIndex.value * (cardWidth.value + gap))

function prevSlide() { if (carouselIndex.value > 0) carouselIndex.value-- }
function nextSlide() { if (carouselIndex.value < maxIndex.value) carouselIndex.value++ }

// Interests modal
const showInterestsModal = ref(false)
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