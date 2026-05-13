<template>
  <div class="bg-slate-50 min-h-screen">
    <div v-if="loading" class="flex justify-center py-20">
      <svg class="h-8 w-8 animate-spin text-cyan-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
      </svg>
    </div>

    <div v-else-if="!listing" class="flex min-h-screen items-center justify-center">
      <div class="rounded-3xl border border-slate-200 bg-white px-12 py-16 text-center shadow-sm">
        <p class="text-base font-medium text-slate-500">Listing not found.</p>
        <router-link
          to="/listings"
          class="mt-6 inline-block rounded-2xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
        >
          Back to Listings
        </router-link>
      </div>
    </div>

    <div v-else>

      <div class="relative h-72 w-full overflow-hidden bg-slate-200 sm:h-96 lg:h-[480px]">

      <template v-if="images.length">
        <transition name="fade" mode="out-in">
          <img
            :key="currentImage"
            :src="currentImage"
            :alt="listing.title"
            class="h-full w-full object-cover"
            @error="handleImageError"
          />
        </transition>

        <button
          v-if="images.length > 1"
          @click="prevImage"
          class="absolute left-4 top-1/2 z-20 flex h-11 w-11 -translate-y-1/2 items-center justify-center rounded-full bg-black/35 text-white backdrop-blur-sm transition hover:bg-black/50"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>

        <button
          v-if="images.length > 1"
          @click="nextImage"
          class="absolute right-4 top-1/2 z-20 flex h-11 w-11 -translate-y-1/2 items-center justify-center rounded-full bg-black/35 text-white backdrop-blur-sm transition hover:bg-black/50"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>

        <div
          v-if="images.length > 1"
          class="absolute bottom-24 left-1/2 z-20 flex -translate-x-1/2 gap-2"
        >
          <button
            v-for="(image, index) in images"
            :key="image"
            @click="goToImage(index)"
            class="h-3 rounded-full transition-all duration-300"
            :class="currentImageIndex === index ? 'w-8 bg-cyan-300' : 'w-3 bg-white/50 hover:bg-white/80'"
          />
        </div>
      </template>
        <div v-else class="flex h-full w-full items-center justify-center text-slate-300">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-20 w-20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
        <div class="absolute inset-0 bg-gradient-to-t from-slate-950/60 via-transparent to-transparent"></div>
        <div class="absolute left-4 top-4 sm:left-6 lg:left-8">
          <router-link
            to="/listings"
            class="inline-flex items-center gap-2 rounded-2xl border border-white/20 bg-white/10 px-4 py-2 text-sm font-semibold text-white backdrop-blur-md transition hover:bg-white/20"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
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

          <div class="lg:col-span-2 space-y-6">

  
            <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <div class="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p class="flex items-center gap-1.5 text-sm text-slate-500">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-cyan-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    {{ listing.address?.street ? listing.address.street + ', ' : '' }}{{ listing.address?.city }}, {{ listing.address?.country }}
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
            </div>

            <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <p class="text-sm font-semibold uppercase tracking-[0.25em] text-cyan-600">About this place</p>
              <p class="mt-3 text-base leading-7 text-slate-600">
                {{ listing.description || 'No description provided.' }}
              </p>
            </div>

            <div
              v-if="hasLocation"
              class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
            >
              <div class="flex items-center justify-between gap-3">
                <p class="text-sm font-semibold uppercase tracking-[0.25em] text-cyan-600">
                  Map Location
                </p>
                <a
                  :href="mapExternalUrl"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-xs font-semibold text-cyan-700 transition hover:text-cyan-600"
                >
                  Open in maps
                </a>
              </div>

              <div class="mt-3 overflow-hidden rounded-2xl border border-slate-200">
                <iframe
                  :src="mapEmbedUrl"
                  title="Listing location map"
                  class="h-72 w-full"
                  loading="lazy"
                  referrerpolicy="no-referrer-when-downgrade"
                ></iframe>
              </div>
            </div>

            <component
              :is="detailsComponent"
              v-if="detailsComponent && listing.details"
              :details="listing.details"
            />

          </div>

          <div class="lg:col-span-1">
            <div class="sticky top-6 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-400">Starting from</p>
              <div class="mt-1 flex items-end gap-1">
                <span class="text-4xl font-bold text-slate-900">${{ listing.base_price }}</span>
                <span class="mb-1 text-sm text-slate-400">/ night</span>
              </div>

              <div class="my-6 border-t border-slate-100"></div>

              <button
                @click="handleOpenBooking"
                class="w-full rounded-2xl bg-slate-900 py-3.5 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-slate-800"
              >
                Book Now
              </button>

              <p class="mt-3 text-center text-xs text-slate-400">
                You won't be charged yet
              </p>
            </div>
          </div>

        </div>

        <div class="mt-10">
          <div class="mb-6">
            <p class="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-600">Guest Feedback</p>
            <h2 class="mt-2 text-2xl font-bold text-slate-900">Reviews</h2>
          </div>

          <div
            v-if="reviews.length === 0"
            class="rounded-3xl border border-slate-200 bg-white px-6 py-12 text-center shadow-sm">
            <p class="text-base font-medium text-slate-500">No reviews yet.</p>
            <p class="mt-1 text-sm text-slate-400">Be the first to share your experience.</p>
          </div>

          <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div
              v-for="review in reviews"
              :key="review.id"
              class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
            >
              <div class="flex items-start justify-between gap-4">
                <div class="flex items-center gap-3">
                  <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-cyan-50 text-sm font-bold text-cyan-700">
                    {{ reviewAuthorInitial(review) }}
                  </div>
                  <div>
                    <p class="text-sm font-semibold text-slate-900">{{ reviewAuthorLabel(review) }}</p>
                    <p class="text-xs text-slate-400">{{ new Date(review.created_at).toLocaleDateString() }}</p>
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
            </div>
          </div>
        </div>

      </div>
    </div>

    <Teleport to="body">
      <div
        v-if="showBooking"
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 px-4 py-8"
        @click.self="handleCloseBooking"
      >
        <div class="w-full max-w-2xl rounded-3xl border border-slate-200 bg-white shadow-2xl">
          <div class="flex items-start justify-between gap-4 border-b border-slate-100 px-6 py-5">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-600">Book Listing</p>
              <h2 class="mt-2 text-xl font-bold text-slate-900">{{ listing.title }}</h2>
              <p class="mt-1 text-sm text-slate-500">
                Choose a real service for this listing and complete your booking details.
              </p>
            </div>
            <button
              type="button"
              class="flex h-10 w-10 items-center justify-center rounded-2xl border border-slate-200 text-slate-500 transition hover:bg-slate-50"
              @click="handleCloseBooking"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="space-y-5 px-6 py-6">
            <div v-if="bookingError" class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {{ bookingError }}
            </div>

            <div>
              <label class="block text-sm font-semibold text-slate-700">
                Service <span class="text-red-500">*</span>
              </label>
              <select
                v-model="bookingForm.service_id"
                class="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100"
                :disabled="bookingServicesLoading || bookingServices.length === 0"
              >
                <option value="">
                  {{ bookingServicesLoading ? 'Loading services...' : bookingServices.length === 0 ? 'No active services available' : '-- Select a service --' }}
                </option>
                <option
                  v-for="service in bookingServices"
                  :key="service.service_id"
                  :value="service.service_id"
                >
                  {{ bookingServiceLabel(service) }}
                </option>
              </select>
              <p v-if="bookingServices.length > 1" class="mt-1 text-xs text-slate-500">
                This listing has multiple services. Pick the exact one you want to reserve.
              </p>
              <p v-if="bookingServices.length === 0 && !bookingServicesLoading" class="mt-1 text-xs text-amber-600">
                This listing is not bookable right now because it has no active services.
              </p>
            </div>

            <div class="grid gap-5 md:grid-cols-2">
              <label class="block">
                <span class="text-sm font-semibold text-slate-700">
                  Booker's name <span class="text-red-500">*</span>
                </span>
                <input
                  v-model="bookingForm.bookers_name"
                  type="text"
                  class="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100"
                  placeholder="Enter your full name"
                />
              </label>

              <label class="block">
                <span class="text-sm font-semibold text-slate-700">Number of people</span>
                <input
                  v-model.number="bookingForm.amount_of_people"
                  type="number"
                  min="1"
                  class="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100"
                />
              </label>
            </div>

            <div v-if="isHotelType" class="grid gap-5 md:grid-cols-2">
              <label class="block">
                <span class="text-sm font-semibold text-slate-700">
                  Check-in date <span class="text-red-500">*</span>
                </span>
                <input
                  :value="hotelCheckInDate"
                  type="date"
                  class="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100"
                  @input="updateHotelCheckIn($event.target.value)"
                />
              </label>

              <label class="block">
                <span class="text-sm font-semibold text-slate-700">
                  Check-out date <span class="text-red-500">*</span>
                </span>
                <input
                  :value="hotelCheckOutDate"
                  type="date"
                  class="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100"
                  @input="updateHotelCheckOut($event.target.value)"
                />
              </label>
            </div>

            <div v-else class="grid gap-5 md:grid-cols-2">
              <label class="block">
                <span class="text-sm font-semibold text-slate-700">
                  Booking start <span class="text-red-500">*</span>
                </span>
                <input
                  v-model="bookingForm.booking_from_time"
                  type="datetime-local"
                  class="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100"
                />
              </label>

              <label class="block">
                <span class="text-sm font-semibold text-slate-700">
                  Booking end <span class="text-red-500">*</span>
                </span>
                <input
                  v-model="bookingForm.booking_to_time"
                  type="datetime-local"
                  class="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100"
                />
              </label>
            </div>

            <label class="block">
              <span class="text-sm font-semibold text-slate-700">Special requests</span>
              <textarea
                v-model="bookingForm.special_requests"
                rows="3"
                class="mt-2 w-full resize-none rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100"
                placeholder="Accessibility needs, timing notes, or other requests"
              ></textarea>
            </label>
          </div>

          <div class="flex gap-3 border-t border-slate-100 bg-slate-50 px-6 py-5">
            <button
              type="button"
              class="flex-1 rounded-2xl border border-slate-200 bg-white py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
              @click="handleCloseBooking"
            >
              Cancel
            </button>
            <button
              type="button"
              class="flex-1 rounded-2xl bg-slate-900 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
              :disabled="bookingSubmitting || bookingServicesLoading || bookingServices.length === 0"
              @click="submitBooking"
            >
              {{ bookingSubmitting ? 'Booking...' : 'Confirm Booking' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { bookingsAPI, listingsAPI, reviewsAPI, servicesAPI } from '../services/api';
import { useAuthStore } from '../stores/auth';
import { useToastStore } from '../stores/toast';
import HotelDetailSection from '../components/listings/detail-sections/HotelDetailSection.vue'
import RestaurantDetailSection from '../components/listings/detail-sections/RestaurantDetailSection.vue'
import TourDetailSection from '../components/listings/detail-sections/TourDetailSection.vue'
import ActivityDetailSection from '../components/listings/detail-sections/ActivityDetailSection.vue'

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const toastStore = useToastStore();
const listing = ref(null)
const reviews = ref([]);
const loading = ref(true);
const showBooking = ref(false);
const bookingServices = ref([]);
const bookingServicesLoading = ref(false);
const bookingSubmitting = ref(false);
const bookingError = ref('');
const currentImageIndex = ref(0);
const brokenImages = ref(new Set());
let heroInterval = null;
const bookingForm = reactive({
  service_id: '',
  bookers_name: '',
  amount_of_people: 1,
  booking_from_time: '',
  booking_to_time: '',
  special_requests: '',
});

const detailsComponent = computed(() => {
  switch (listing.value?.business_type_name) {
    case 'Hotel':      return HotelDetailSection
    case 'Restaurant': return RestaurantDetailSection
    case 'Tour Operator':      return TourDetailSection
    case 'Activity Provider':  return ActivityDetailSection
    default:           return null
  }
})

const isHotelType = computed(() => listing.value?.business_type_name === 'Hotel')
const hotelCheckInDate = computed(() => bookingForm.booking_from_time ? bookingForm.booking_from_time.slice(0, 10) : '')
const hotelCheckOutDate = computed(() => bookingForm.booking_to_time ? bookingForm.booking_to_time.slice(0, 10) : '')

const mapCoordinates = computed(() => {
  const lat = Number(listing.value?.location?.lat)
  const lng = Number(listing.value?.location?.lng)

  if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null
  return { lat, lng }
})

const hasLocation = computed(() => !!mapCoordinates.value)

const mapEmbedUrl = computed(() => {
  if (!mapCoordinates.value) return ''

  const { lat, lng } = mapCoordinates.value
  const delta = 0.01
  const left = lng - delta
  const right = lng + delta
  const top = lat + delta
  const bottom = lat - delta

  return `https://www.openstreetmap.org/export/embed.html?bbox=${left}%2C${bottom}%2C${right}%2C${top}&layer=mapnik&marker=${lat}%2C${lng}`
})

const mapExternalUrl = computed(() => {
  if (!mapCoordinates.value) return '#'

  const { lat, lng } = mapCoordinates.value
  return `https://www.openstreetmap.org/?mlat=${lat}&mlon=${lng}#map=15/${lat}/${lng}`
})

const images = computed(() => {
  return (listing.value?.image_urls ?? []).filter(
    (url) => url && !brokenImages.value.has(url)
  );
});

const currentImage = computed(() => {
  return images.value[currentImageIndex.value] ?? images.value[0] ?? null;

});

const nextImage = () => {
  if (!images.value.length) return;
  currentImageIndex.value = (currentImageIndex.value + 1) % images.value.length;
};

const prevImage = () => {
  if(!images.value.length) return;
  currentImageIndex.value = 
    (currentImageIndex.value - 1 + images.value.length) % images.value.length;
};

const goToImage = (index) => {
  currentImageIndex.value = index;
  startSlideshow();
};

const startSlideshow = () => {
  stopSlideshow();

  if (images.value.length <= 1) return;

  heroInterval = setInterval(() => {
    nextImage();
  }, 4000);
};

const stopSlideshow = () => {
  if (heroInterval) {
    clearInterval(heroInterval);
    heroInterval = null;
  }
};

function capitalizeName(name) {
  if (!name) return '';
  return name
    .split(' ')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

function getUserFullName() {
  const user = authStore.user;
  if (!user) return '';
  return capitalizeName(`${user.first_name || ''} ${user.last_name || ''}`.trim());
}

function resetBookingForm() {
  bookingForm.service_id = '';
  bookingForm.bookers_name = getUserFullName();
  bookingForm.amount_of_people = 1;
  bookingForm.booking_from_time = '';
  bookingForm.booking_to_time = '';
  bookingForm.special_requests = '';
  bookingError.value = '';
}

function applySingleServiceDefault() {
  if (bookingServices.value.length === 1) {
    bookingForm.service_id = bookingServices.value[0].service_id;
    return;
  }

  const stillValid = bookingServices.value.some(
    (service) => service.service_id === bookingForm.service_id
  );
  if (!stillValid) {
    bookingForm.service_id = '';
  }
}

async function loadBookingServices() {
  if (!listing.value?.id) {
    bookingServices.value = [];
    return;
  }

  bookingServicesLoading.value = true;
  bookingError.value = '';
  try {
    const response = await servicesAPI.getAll({ listing_id: listing.value.id });
    bookingServices.value = Array.isArray(response.data) ? response.data : [];
    applySingleServiceDefault();
  } catch (err) {
    bookingServices.value = [];
    bookingError.value = 'Failed to load active services for this listing.';
  } finally {
    bookingServicesLoading.value = false;
  }
}

async function handleOpenBooking() {
  await authStore.initialize();
  if (!authStore.isAuthenticated) {
    router.push({ name: 'Login', query: { redirect: route.fullPath } });
    return;
  }

  resetBookingForm();
  showBooking.value = true;
  await loadBookingServices();
}

function handleCloseBooking() {
  showBooking.value = false;
  bookingError.value = '';
}

function updateHotelCheckIn(date) {
  bookingForm.booking_from_time = date ? `${date}T14:00:00` : '';
}

function updateHotelCheckOut(date) {
  bookingForm.booking_to_time = date ? `${date}T11:00:00` : '';
}

function bookingServiceLabel(service) {
  if (service?.price !== null && service?.price !== undefined) {
    const price = Number(service.price);
    if (Number.isFinite(price)) {
      return `${service.name} ($${price.toFixed(2)})`;
    }
  }
  return service?.name || 'Unnamed service';
}

function validateListingBooking() {
  bookingError.value = '';

  if (bookingServicesLoading.value) {
    bookingError.value = 'Services are still loading. Please wait a moment.';
    return false;
  }
  if (bookingServices.value.length === 0) {
    bookingError.value = 'This listing is not bookable right now because it has no active services.';
    return false;
  }
  if (!bookingForm.service_id) {
    bookingError.value = 'Please choose a service before continuing.';
    return false;
  }
  if (!bookingForm.bookers_name.trim()) {
    bookingError.value = "Booker's name is required.";
    return false;
  }
  if (!bookingForm.booking_from_time || !bookingForm.booking_to_time) {
    bookingError.value = isHotelType.value
      ? 'Please choose both check-in and check-out dates.'
      : 'Please choose both a booking start and end time.';
    return false;
  }
  if (new Date(bookingForm.booking_to_time) <= new Date(bookingForm.booking_from_time)) {
    bookingError.value = isHotelType.value
      ? 'Check-out must be after check-in.'
      : 'Booking end time must be after the start time.';
    return false;
  }

  return true;
}

async function submitBooking() {
  if (!validateListingBooking()) {
    return;
  }

  bookingSubmitting.value = true;
  try {
    await bookingsAPI.create({
      service_id: bookingForm.service_id,
      bookers_name: bookingForm.bookers_name.trim(),
      amount_of_people: bookingForm.amount_of_people || 1,
      booking_from_time: new Date(bookingForm.booking_from_time).toISOString(),
      booking_to_time: new Date(bookingForm.booking_to_time).toISOString(),
      special_requests: bookingForm.special_requests.trim() || null,
    });
    toastStore.show('Booking created successfully.', 'success');
    handleCloseBooking();
    router.push({ name: 'Bookings' });
  } catch (err) {
    bookingError.value = err.response?.data?.detail || 'Failed to create booking.';
    toastStore.show('Failed to create booking.', 'error');
  } finally {
    bookingSubmitting.value = false;
  }
}

const fetchListings = async () => {
  try {
    const response = await listingsAPI.getById(route.params.id);
    listing.value = response.data;

    const reviewResponse = await reviewsAPI.getAll({ listing_id:route.params.id});
    reviews.value = reviewResponse.data;
  }catch (err){
    console.error('Failed to load listing', err);
  }finally{
    loading.value = false;
  }
};

const handleImageError = (event) => {
  event.target.style.display = 'none';
  event.target.parentElement.innerHTML = `
    <div class="flex h-full w-full items-center justify-center text-slate-300">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-20 w-20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    </div>
  `;
};

const reviewAuthorLabel = () => 'Guest';
const reviewAuthorInitial = () => 'G';

onMounted(() => {
  fetchListings();
});
</script>
