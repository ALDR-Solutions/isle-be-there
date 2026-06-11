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

            <ListingBookingServiceCarousel
              :services="bookingServices"
              :selected-service-id="selectedServiceId"
              :loading="bookingServicesLoading"
              :business-type-name="listing.business_type_name"
              @select="handleSelectService"
            />

          </div>

          <div class="lg:col-span-1">
            <div
              v-if="selectedServiceImages.length"
              class="mb-4 rounded-3xl border border-slate-200 bg-white p-4 shadow-sm"
            >
              <div class="flex items-start justify-between gap-3">
                <div>
                  <p class="text-xs font-semibold uppercase tracking-[0.25em] text-cyan-600">Service Gallery</p>
                  <p class="mt-2 text-lg font-bold text-slate-900">{{ selectedService?.name }}</p>
                </div>
                <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-500">
                  {{ selectedServiceImages.length }} image{{ selectedServiceImages.length > 1 ? 's' : '' }}
                </span>
              </div>

              <div class="relative mt-4 overflow-hidden rounded-2xl bg-slate-100">
                <img
                  :src="selectedServiceCurrentImage"
                  :alt="selectedService?.name || 'Selected service image'"
                  class="h-64 w-full object-cover"
                />

                <button
                  v-if="selectedServiceImages.length > 1"
                  type="button"
                  @click="showPreviousSelectedServiceImage"
                  class="absolute left-3 top-1/2 flex h-10 w-10 -translate-y-1/2 items-center justify-center rounded-full bg-slate-950/55 text-white backdrop-blur-sm transition hover:bg-slate-950/75"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                  </svg>
                </button>

                <button
                  v-if="selectedServiceImages.length > 1"
                  type="button"
                  @click="showNextSelectedServiceImage"
                  class="absolute right-3 top-1/2 flex h-10 w-10 -translate-y-1/2 items-center justify-center rounded-full bg-slate-950/55 text-white backdrop-blur-sm transition hover:bg-slate-950/75"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>

              <div
                v-if="selectedServiceImages.length > 1"
                class="mt-3 grid grid-cols-4 gap-2"
              >
                <button
                  v-for="(image, index) in selectedServiceImages"
                  :key="`${image}-${index}`"
                  type="button"
                  @click="goToSelectedServiceImage(index)"
                  class="overflow-hidden rounded-2xl border-2 transition"
                  :class="selectedServiceImageIndex === index ? 'border-cyan-500' : 'border-transparent hover:border-slate-200'"
                >
                  <img
                    :src="image"
                    :alt="`${selectedService?.name || 'Service'} thumbnail ${index + 1}`"
                    class="h-16 w-full object-cover"
                  />
                </button>
              </div>
            </div>

            <div class="sticky top-24 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-400">
                {{ isRestaurantType ? 'Average spend' : selectedService ? 'Selected service' : 'Starting from' }}
              </p>
              <div class="mt-1 flex items-end gap-2">
                <span class="text-4xl font-bold text-slate-900">${{ displaySidebarPrice }}</span>
                <span class="mb-1 text-sm text-slate-400">
                  {{ sidebarPriceSuffix }}
                </span>
              </div>

              <div class="mt-4 rounded-2xl bg-slate-50 px-4 py-4">
                <p class="text-sm font-semibold text-slate-900">
                  {{ selectedService?.name || 'Choose a service below' }}
                </p>
                <p class="mt-1 text-sm leading-6 text-slate-500">
                  {{ sidebarHelperText }}
                </p>
              </div>

              <div class="my-6 border-t border-slate-100"></div>

              <button
                @click="handleOpenBooking"
                :disabled="bookingServicesLoading || bookingServices.length === 0 || !selectedService"
                class="w-full rounded-2xl bg-slate-900 py-3.5 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0"
              >
                {{ primaryCtaLabel }}
              </button>

              <p class="mt-3 text-center text-xs text-slate-400">
                {{ sidebarFootnote }}
              </p>
            </div>
          </div>

        </div>

        <div class="mt-10">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-600">Guest Feedback</p>
              <h2 class="mt-2 text-2xl font-bold text-slate-900">Reviews</h2>
            </div>
            <div v-if="listing.avg_rating" class="flex items-center gap-2">
              <span class="text-2xl font-bold text-slate-900">{{ listing.avg_rating.toFixed(1) }}</span>
              <span class="text-sm text-slate-400">({{ listing.review_count }} {{ listing.review_count === 1 ? 'review' : 'reviews' }})</span>
            </div>
          </div>

          <button
            v-if="canWriteReview"
            @click="openSubmitModal"
            class="mt-4 rounded-2xl bg-cyan-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-cyan-700"
          >
            Write a Review
          </button>

          <ListingReviewsPanel
            ref="reviewsPanelRef"
            :listing-id="listing.id"
            :can-reply="canReply"
            :can-manage-reply="canManageReply"
            empty-subtext="Be the first to share your experience."
          >
            <template #review-actions="{ review }">
              <div v-if="isOwner(review)" class="mt-4 flex gap-3 border-t border-slate-100 pt-4">
                <button @click="openEditModal(review)" class="text-sm text-cyan-600 hover:text-cyan-700">Edit</button>
                <button @click="confirmDelete(review)" class="text-sm text-red-600 hover:text-red-700">Delete</button>
              </div>
            </template>
          </ListingReviewsPanel>
        </div>

        <ReviewModal
          v-if="showReviewModal"
          :mode="editingReview ? 'edit' : 'submit'"
          :review="editingReview"
          :listing-id="listing.id"
          @close="showReviewModal = false"
          @success="handleReviewSuccess"
        />

      </div>
    </div>

    <Teleport to="body">
      <div
        v-if="showBooking"
        class="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-slate-950/60 px-4 py-8"
        @click.self="handleCloseBooking"
      >
        <div class="flex max-h-[calc(100vh-4rem)] w-full max-w-2xl flex-col overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-2xl">
          <div class="shrink-0 flex items-start justify-between gap-4 border-b border-slate-100 px-6 py-5">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-600">
                {{ isRestaurantType ? 'Reserve Listing' : 'Book Listing' }}
              </p>
              <h2 class="mt-2 text-xl font-bold text-slate-900">{{ listing.title }}</h2>
              <p class="mt-1 text-sm text-slate-500">
                {{ modalDescription }}
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

          <div class="flex-1 space-y-5 overflow-y-auto px-6 py-6">
            <div v-if="bookingError" class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {{ bookingError }}
            </div>

            <div class="rounded-3xl border border-slate-200 bg-slate-50 px-5 py-4">
              <div class="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                    {{ isRestaurantType ? 'Selected reservation option' : 'Selected service' }}
                  </p>
                  <p class="mt-1 text-base font-semibold text-slate-900">
                    {{ selectedService?.name || 'No service selected' }}
                  </p>
                  <p class="mt-1 text-sm text-slate-500">
                    {{ selectedService?.description || 'You can change this from the service carousel on the page.' }}
                  </p>
                </div>
                <div class="text-right">
                  <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                    {{ isRestaurantType ? 'Average spend' : 'Price' }}
                  </p>
                  <p class="mt-1 text-xl font-bold text-slate-900">
                    ${{ selectedServicePrice }}
                  </p>
                </div>
              </div>
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

            <template v-if="isHotelType">
              <div class="grid gap-5 md:grid-cols-2">
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

              <div
                v-if="bookingLoadingAvailability"
                class="mt-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-500"
              >
                Loading hotel availability...
              </div>
              <div
                v-else-if="bookingAvailabilityError"
                class="mt-3 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-500"
              >
                {{ bookingAvailabilityError }}
              </div>
              <div
                v-else-if="bookingDateValue && bookingAvailability && bookingAvailability.is_open === false"
                class="mt-3 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700"
              >
                This service is unavailable for the selected check-in date. Try another date.
              </div>
            </template>

            <div v-else>
              <!-- Date picker -->
              <label class="block">
                <span class="text-sm font-semibold text-slate-700">
                  {{ isRestaurantType ? 'Reservation date' : 'Date' }}
                </span>
                <input
                  :value="bookingDateValue"
                  type="date"
                  class="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100"
                  @input="updateBookingDate($event.target.value)"
                />
              </label>

              <!-- Availability loading/error -->
              <div v-if="bookingLoadingAvailability" class="mt-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-500">
                Loading availability...
              </div>
              <div v-else-if="bookingAvailabilityError" class="mt-3 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-500">
                {{ bookingAvailabilityError }}
              </div>

              <!-- Slot Selector -->
              <div v-if="bookingAvailableSlots.length > 0" class="mt-3">
                <span class="text-sm font-semibold text-slate-700">
                  {{ isRestaurantType ? 'Choose a reservation time' : 'Choose a time slot' }}
                </span>
                <div class="mt-2 grid grid-cols-2 gap-2 sm:grid-cols-3">
                  <button
                    v-for="slot in bookingAvailableSlots"
                    :key="slot.slot_id"
                    type="button"
                    :disabled="slot.remaining_capacity < (bookingForm.amount_of_people || 1)"
                    :class="[
                      'rounded-2xl border px-4 py-3 text-center text-sm font-semibold transition',
                      bookingForm.selectedSlotId === String(slot.slot_id)
                        ? 'border-cyan-500 bg-cyan-50 text-cyan-700 ring-2 ring-cyan-200'
                        : 'border-slate-200 bg-white text-slate-700 hover:border-cyan-300 hover:bg-cyan-50',
                      slot.remaining_capacity < (bookingForm.amount_of_people || 1)
                        ? 'cursor-not-allowed opacity-50'
                        : ''
                    ]"
                    @click="selectBookingSlot(String(slot.slot_id))"
                  >
                    <div class="text-base">{{ formatSlotTime(slot.start_time) }}</div>
                    <div class="text-xs text-slate-400">{{ formatSlotTime(slot.end_time) }}</div>
                    <div
                      v-if="slot.remaining_capacity < (bookingForm.amount_of_people || 1)"
                      class="mt-1 text-xs text-red-500"
                    >
                      {{ slot.remaining_capacity }} left
                    </div>
                    <div v-else class="mt-1 text-xs text-green-600">
                      {{ slot.remaining_capacity }} spots
                    </div>
                  </button>
                </div>
              </div>

              <div
                v-else-if="noSlotsForSelectedDate"
                class="mt-3 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700"
              >
                No time slots are available for the selected date. Please choose a different date.
              </div>
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

          <div class="shrink-0 flex gap-3 border-t border-slate-100 bg-slate-50 px-6 py-5">
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
              :disabled="bookingSubmitting || bookingServicesLoading || bookingServices.length === 0 || !canSubmitBooking"
              @click="submitBooking"
            >
              {{ bookingSubmitting ? submitPendingLabel : modalSubmitLabel }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Receipt Modal - shown after validate, before API call -->
    <Teleport to="body">
      <div v-if="showReceiptModal" class="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 p-4">
        <div class="w-full max-w-md rounded-3xl bg-white shadow-2xl">
          <!-- Header -->
          <div class="rounded-t-3xl border-b border-slate-100 bg-slate-50 px-6 py-5">
            <h2 class="text-xl font-bold text-slate-900">Booking Receipt</h2>
          </div>

          <!-- Body -->
          <div class="max-h-[60vh] overflow-y-auto px-6 py-5">
            <!-- Service name -->
            <p class="text-base font-semibold text-slate-900">{{ selectedService?.name }}</p>

            <!-- Per-person or flat fee breakdown -->
            <div class="mt-2 text-sm text-slate-500">
              <template v-if="isHotelType">
                <p>1 room x ${{ (selectedService?.price || 0).toFixed(2) }} x {{ hotelNightsForReceipt }} night{{ hotelNightsForReceipt !== 1 ? 's' : '' }}</p>
              </template>
              <template v-else>
                <p>${{ (selectedService?.price || 0).toFixed(2) }} x {{ bookingForm.amount_of_people || 1 }} people</p>
              </template>
            </div>

            <!-- Subtotal -->
            <div class="mt-4 flex justify-between text-sm">
              <span class="text-slate-600">Subtotal</span>
              <span class="font-medium text-slate-900">${{ receiptSubtotal.toFixed(2) }}</span>
            </div>

            <!-- Service Fee -->
            <div class="mt-2 flex justify-between text-sm">
              <span class="text-slate-600">Service Fee ({{ formatPercent(currentServiceFeePercent) }})</span>
              <span class="font-medium text-slate-900">${{ receiptServiceFee.toFixed(2) }}</span>
            </div>

            <div v-if="receiptPricingLoading" class="mt-3 rounded-xl bg-slate-50 px-3 py-2 text-sm text-slate-500">
              Refreshing live pricing for this service...
            </div>

            <div v-else-if="receiptPricingFallbackNotice" class="mt-3 rounded-xl bg-amber-50 px-3 py-2 text-sm text-amber-700">
              {{ receiptPricingFallbackNotice }}
            </div>

            <!-- Discount -->
            <div v-if="receiptDiscountAmount > 0" class="mt-2 flex justify-between text-sm">
              <span class="text-slate-600">Discount</span>
              <span class="font-medium text-emerald-600">-${{ receiptDiscountAmount.toFixed(2) }}</span>
            </div>

            <!-- Final Total -->
            <div class="mt-4 border-t border-slate-200 pt-4">
              <div class="flex justify-between">
                <p class="text-base font-semibold text-slate-900">Final Total</p>
                <p class="text-xl font-bold text-cyan-600">${{ receiptFinalTotal.toFixed(2) }}</p>
              </div>
            </div>

            <!-- Error message -->
            <div v-if="receiptError" class="mt-4 rounded-xl bg-red-50 p-3 text-sm text-red-600">
              {{ receiptError }}
            </div>
          </div>

          <!-- Footer -->
          <div class="flex justify-end gap-3 rounded-b-3xl border-t border-slate-100 bg-slate-50 px-6 py-4">
            <button
              type="button"
              @click="handleBackToForm"
              class="rounded-xl border border-slate-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
            >
              Back
            </button>
            <button
              type="button"
              @click="confirmBookingFromReceipt"
              :disabled="confirming"
              class="rounded-xl bg-cyan-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-cyan-700 disabled:opacity-60"
            >
              {{ confirming ? 'Confirming...' : 'Confirm Booking' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup>


import ReviewModal from '../components/ReviewModal.vue';
import ListingReviewsPanel from '../components/reviews/ListingReviewsPanel.vue';
import { ref, computed, onBeforeUnmount, reactive, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { bookingsAPI, listingsAPI, reviewsAPI, servicesAPI, availabilityAPI, pricingAPI } from '../services/api'
import { useAuthStore } from '../stores/auth'
import { useEmployeeStore } from '../stores/employee'
import { useToastStore } from '../stores/toast'
import HotelDetailSection from '../components/listings/detail-sections/HotelDetailSection.vue'
import RestaurantDetailSection from '../components/listings/detail-sections/RestaurantDetailSection.vue'
import TourDetailSection from '../components/listings/detail-sections/TourDetailSection.vue'
import ActivityDetailSection from '../components/listings/detail-sections/ActivityDetailSection.vue'
import ListingBookingServiceCarousel from '../components/listings/ListingBookingServiceCarousel.vue'

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const employeeStore = useEmployeeStore();
const toastStore = useToastStore();
const reviewsPanelRef = ref(null);

const listing = ref(null)
const loading = ref(true);
const showBooking = ref(false);
const bookingServices = ref([]);
const selectedServiceId = ref('');
const bookingServicesLoading = ref(false);
const bookingSubmitting = ref(false);
const bookingError = ref('');
const bookingAvailability = ref(null);
const bookingAvailableSlots = ref([]);
const bookingLoadingAvailability = ref(false);
const bookingAvailabilityError = ref('');
const bookingSelectedDate = ref('');
const currentImageIndex = ref(0);
const selectedServiceImageIndex = ref(0);
const brokenImages = ref(new Set());
let heroInterval = null;
const bookingForm = reactive({
  service_id: '',
  bookers_name: '',
  amount_of_people: 1,
  booking_from_time: '',
  booking_to_time: '',
  special_requests: '',
  selectedSlotId: '',
});

const showReceiptModal = ref(false);
const pendingBookingData = ref(null);
const confirming = ref(false);
const receiptError = ref('');
const receiptPricingLoading = ref(false);
const currentServiceFeePercent = ref(0.10);
const receiptPricingFallbackNotice = ref('');

const showReviewModal = ref(false);
const editingReview = ref(null);
let activeListingRequestToken = 0;
let activeBookingAvailabilityRequestKey = '';

const isLoggedIn = computed(() => authStore.isAuthenticated);
const currentUser = computed(() => authStore.user);
const userRole = computed(() => authStore.role);
const canWriteReview = computed(() => isLoggedIn.value);
const isEmployeeAssignedToCurrentListing = computed(() => {
  if (userRole.value !== 'employee' || !listing.value?.id) {
    return false;
  }

  return employeeStore.assignedListings.some(
    assignedListing => String(assignedListing.id) === String(listing.value.id),
  );
});

const canReply = computed(() => {
  if (userRole.value === 'business') {
    return true;
  }

  return isEmployeeAssignedToCurrentListing.value;
});
const canManageReply = computed(() => canReply.value);

const isOwner = (review) => {
  return currentUser.value && review.user_id === currentUser.value.id;
};

const openSubmitModal = () => {
  editingReview.value = null;
  showReviewModal.value = true;
};

const openEditModal = (review) => {
  editingReview.value = { ...review };
  showReviewModal.value = true;
};

const handleReviewSuccess = (message) => {
  showReviewModal.value = false;
  toastStore.show(message, 'success');
  refreshListingSummaryAndReviews();
};

const confirmDelete = async (review) => {
  if (confirm('Are you sure you want to delete this review?')) {
    try {
      await reviewsAPI.delete(review.id);
      toastStore.show('Review deleted', 'success');
      refreshListingSummaryAndReviews();
    } catch (err) {
      console.error('Failed to delete review', err);
      toastStore.show('Failed to delete review', 'error');
    }
  }
};

watch(
  [() => authStore.authResolved, currentUser, userRole],
  async ([authResolved, user, role]) => {
    if (!authResolved || !user) {
      employeeStore.reset();
      return;
    }

    if (role !== 'employee') {
      employeeStore.reset();
      return;
    }

    await employeeStore.fetchAssignments();
  },
  { immediate: true },
);

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
const isRestaurantType = computed(() => listing.value?.business_type_name === 'Restaurant')
const primaryCtaLabel = computed(() => (isRestaurantType.value ? 'Reserve table' : 'Book now'))
const modalSubmitLabel = computed(() => (isRestaurantType.value ? 'Confirm reservation' : 'Continue booking'))
const submitPendingLabel = computed(() => (isRestaurantType.value ? 'Reserving...' : 'Booking...'))
const modalDescription = computed(() => (
  isRestaurantType.value
    ? 'Review the selected dining option and complete your reservation details.'
    : 'Review the selected service and complete your booking details.'
))
const hotelCheckInDate = computed(() => bookingForm.booking_from_time ? bookingForm.booking_from_time.slice(0, 10) : '')

const selectedSlot = computed(() => {
  if (!bookingForm.selectedSlotId) return null
  return bookingAvailableSlots.value.find(s => String(s.slot_id) === String(bookingForm.selectedSlotId)) || null
})

const hotelCheckOutDate = computed(() => bookingForm.booking_to_time ? bookingForm.booking_to_time.slice(0, 10) : '')

const bookingDateValue = computed(() => {
  if (!isHotelType.value) return bookingSelectedDate.value
  return bookingForm.booking_from_time ? bookingForm.booking_from_time.slice(0, 10) : ''
})

const selectedSlotIdValue = computed(() => bookingForm.selectedSlotId || '')
const noSlotsForSelectedDate = computed(() => (
  !isHotelType.value
  && !!bookingDateValue.value
  && bookingAvailability.value !== null
  && !bookingLoadingAvailability.value
  && !bookingAvailabilityError.value
  && bookingAvailableSlots.value.length === 0
))
const canSubmitBooking = computed(() => {
  if (isHotelType.value) return true
  return !!bookingDateValue.value && !!selectedSlot.value
})

const selectedService = computed(() => {
  if (!selectedServiceId.value) return null
  return bookingServices.value.find((service) => String(service.service_id) === String(selectedServiceId.value)) || null
})

const selectedServiceImages = computed(() => (
  Array.isArray(selectedService.value?.image_urls)
    ? selectedService.value.image_urls.filter(Boolean)
    : []
))

const selectedServiceCurrentImage = computed(() => (
  selectedServiceImages.value[selectedServiceImageIndex.value]
    ?? selectedServiceImages.value[0]
    ?? null
))

const selectedServicePrice = computed(() => {
  const price = Number(selectedService.value?.price)
  return Number.isFinite(price) ? price.toFixed(2) : '0.00'
})

const displaySidebarPrice = computed(() => {
  const selectedPrice = Number(selectedService.value?.price)
  const fallbackPrice = Number(listing.value?.base_price)
  if (Number.isFinite(selectedPrice)) return selectedPrice.toFixed(2)
  if (Number.isFinite(fallbackPrice)) return fallbackPrice.toFixed(2)
  return '0.00'
})

const sidebarPriceSuffix = computed(() => {
  if (isRestaurantType.value) return '/ person'
  if (isHotelType.value) return '/ stay'
  return ''
})

const sidebarHelperText = computed(() => {
  if (bookingServicesLoading.value) return 'Loading active services for this listing.'
  if (bookingServices.value.length === 0) return 'No active services are available to book right now.'
  if (!selectedService.value) return 'Choose a service below to continue with the right booking details.'
  if (isRestaurantType.value) return 'This price is an average spend per guest.'
  return 'Your selected service will carry into the booking form with the right availability and details.'
})

const sidebarFootnote = computed(() => (
  isRestaurantType.value
    ? 'Reservation only. Payment happens at the restaurant.'
    : 'You won\'t be charged yet'
))

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

watch(
  selectedServiceImages,
  (nextImages) => {
    if (!nextImages.length) {
      selectedServiceImageIndex.value = 0
      return
    }
    if (selectedServiceImageIndex.value >= nextImages.length) {
      selectedServiceImageIndex.value = 0
    }
  },
  { immediate: true },
)

watch(selectedServiceId, () => {
  selectedServiceImageIndex.value = 0
})

function getBookingAvailabilityRequestKey() {
  return [
    showBooking.value ? 'open' : 'closed',
    selectedServiceId.value || '',
    bookingDateValue.value || '',
    bookingForm.amount_of_people || 1,
    isHotelType.value ? 'hotel' : 'timed',
  ].join(':')
}

function shouldFetchBookingAvailability() {
  return (
    showBooking.value
    && !!selectedServiceId.value
    && !!bookingDateValue.value
  )
}

function refreshBookingAvailability() {
  const requestKey = getBookingAvailabilityRequestKey()
  activeBookingAvailabilityRequestKey = requestKey

  if (!shouldFetchBookingAvailability()) {
    clearAvailabilityState()
    clearSelectedBookingSlot()
    return
  }

  fetchBookingAvailability()
}

function normalizeFractionalPercent(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return 0;
  if (numeric > 1) return numeric / 100;
  return Math.max(numeric, 0);
}

function formatPercent(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return '-';
  return `${(numeric * 100).toFixed(2).replace(/\.00$/, '')}%`;
}

function calculateCalendarNightCount(fromTime, toTime) {
  if (!fromTime || !toTime) return 1;
  const checkIn = new Date(fromTime);
  const checkOut = new Date(toTime);
  if (!(checkIn instanceof Date) || Number.isNaN(checkIn.getTime())) return 1;
  if (!(checkOut instanceof Date) || Number.isNaN(checkOut.getTime())) return 1;
  if (checkOut <= checkIn) return 1;

  const startDate = new Date(checkIn.getFullYear(), checkIn.getMonth(), checkIn.getDate());
  const endDate = new Date(checkOut.getFullYear(), checkOut.getMonth(), checkOut.getDate());
  const diffMs = endDate.getTime() - startDate.getTime();
  return Math.max(1, Math.round(diffMs / (1000 * 60 * 60 * 24)));
}

const receiptSubtotal = computed(() => {
  if (!selectedService.value) return 0;
  const price = Number(selectedService.value.price) || 0;
  const people = bookingForm.amount_of_people || 1;
  if (isHotelType.value) {
    const nights = calculateCalendarNightCount(
      bookingForm.booking_from_time,
      bookingForm.booking_to_time,
    );
    return price * nights;
  }
  return price * people;
});

// Helper to calculate hotel nights for receipt display
const hotelNightsForReceipt = computed(() => {
  return calculateCalendarNightCount(
    bookingForm.booking_from_time,
    bookingForm.booking_to_time,
  );
});

const receiptServiceFee = computed(() => receiptSubtotal.value * currentServiceFeePercent.value);

const receiptDiscountAmount = computed(() => {
  // For now, no discount for direct listing bookings
  return 0;
});

const receiptFinalTotal = computed(() => {
  return receiptSubtotal.value + receiptServiceFee.value - receiptDiscountAmount.value;
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

const showPreviousSelectedServiceImage = () => {
  if (!selectedServiceImages.value.length) return
  selectedServiceImageIndex.value =
    (selectedServiceImageIndex.value - 1 + selectedServiceImages.value.length) %
    selectedServiceImages.value.length
}

const showNextSelectedServiceImage = () => {
  if (!selectedServiceImages.value.length) return
  selectedServiceImageIndex.value =
    (selectedServiceImageIndex.value + 1) % selectedServiceImages.value.length
}

const goToSelectedServiceImage = (index) => {
  selectedServiceImageIndex.value = index
}

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

function clearAvailabilityState() {
  bookingAvailability.value = null;
  bookingAvailableSlots.value = [];
  bookingAvailabilityError.value = '';
  bookingLoadingAvailability.value = false;
}

function clearSelectedBookingSlot() {
  bookingForm.booking_from_time = '';
  bookingForm.booking_to_time = '';
  bookingForm.selectedSlotId = '';
}

function resetBookingForm() {
  bookingForm.service_id = selectedServiceId.value || '';
  bookingForm.bookers_name = getUserFullName();
  bookingForm.amount_of_people = 1;
  clearSelectedBookingSlot();
  bookingForm.special_requests = '';
  bookingSelectedDate.value = '';
  bookingError.value = '';
  clearAvailabilityState();
}

function applyServiceSelectionFallback() {
  if (bookingServices.value.length === 0) {
    selectedServiceId.value = '';
    bookingForm.service_id = '';
    return;
  }

  const stillValid = bookingServices.value.some(
    (service) => String(service.service_id) === String(selectedServiceId.value)
  );
  if (!stillValid) {
    selectedServiceId.value = bookingServices.value[0].service_id;
  }

  bookingForm.service_id = selectedServiceId.value;
}

function isCurrentListingRequest(listingId, requestToken) {
  return (
    requestToken === activeListingRequestToken
    && String(route.params.id) === String(listingId)
  );
}

function resetListingRouteState() {
  stopSlideshow();
  listing.value = null;
  bookingServices.value = [];
  bookingServicesLoading.value = false;
  selectedServiceId.value = '';
  currentImageIndex.value = 0;
  selectedServiceImageIndex.value = 0;
  brokenImages.value = new Set();
  showBooking.value = false;
  showReceiptModal.value = false;
  pendingBookingData.value = null;
  receiptError.value = '';
  bookingSubmitting.value = false;
  confirming.value = false;
  resetBookingForm();
}

async function fetchListingCore(listingId, { requestToken, showPageLoader = true } = {}) {
  if (showPageLoader && isCurrentListingRequest(listingId, requestToken)) {
    loading.value = true;
  }

  try {
    const response = await listingsAPI.getById(listingId);
    if (!isCurrentListingRequest(listingId, requestToken)) {
      return null;
    }

    listing.value = response.data;
    return response.data;
  } catch (err) {
    if (!isCurrentListingRequest(listingId, requestToken)) {
      return null;
    }

    listing.value = null;
    console.error('Failed to load listing', err);
    return null;
  } finally {
    if (showPageLoader && isCurrentListingRequest(listingId, requestToken)) {
      loading.value = false;
    }
  }
}

async function fetchBookingServices(listingId, { requestToken = activeListingRequestToken } = {}) {
  if (!listingId) {
    bookingServices.value = [];
    selectedServiceId.value = '';
    bookingServicesLoading.value = false;
    return;
  }

  bookingServicesLoading.value = true;
  bookingError.value = '';
  try {
    const response = await servicesAPI.getAll({ listing_id: listingId });
    if (!isCurrentListingRequest(listingId, requestToken)) {
      return [];
    }

    bookingServices.value = Array.isArray(response.data) ? response.data : [];
    applyServiceSelectionFallback();
    return bookingServices.value;
  } catch (err) {
    if (!isCurrentListingRequest(listingId, requestToken)) {
      return [];
    }

    console.error('Failed to load active services for listing detail', err);
    bookingServices.value = [];
    selectedServiceId.value = '';
    bookingError.value = 'Failed to load active services for this listing.';
    return [];
  } finally {
    if (isCurrentListingRequest(listingId, requestToken)) {
      bookingServicesLoading.value = false;
    }
  }
}

function loadListingDetail(listingId) {
  if (!listingId) {
    loading.value = false;
    listing.value = null;
    return;
  }

  activeListingRequestToken += 1;
  const requestToken = activeListingRequestToken;
  resetListingRouteState();

  fetchListingCore(listingId, { requestToken });
  fetchBookingServices(listingId, { requestToken });
}

function refreshListingSummaryAndReviews() {
  const listingId = route.params.id;
  const requestToken = activeListingRequestToken;

  if (!listingId) {
    return;
  }

  fetchListingCore(listingId, { requestToken, showPageLoader: false });
  reviewsPanelRef.value?.refreshReviews();
}

function handleSelectService(serviceId) {
  selectedServiceId.value = serviceId;
}

async function handleOpenBooking() {
  if (authStore.isAuthPending) {
    await authStore.startAuthResolution();
  }

  if (!authStore.isAuthenticated) {
    router.push({ name: 'Login', query: { redirect: route.fullPath } });
    return;
  }

  if (!bookingServices.value.length && !bookingServicesLoading.value) {
    await fetchBookingServices(route.params.id);
  }

  if (!selectedService.value) {
    bookingError.value = 'Please choose a service before continuing.';
    return;
  }

  resetBookingForm();
  showBooking.value = true;
}

function handleCloseBooking() {
  showBooking.value = false;
  bookingError.value = '';
  activeBookingAvailabilityRequestKey = getBookingAvailabilityRequestKey();
  clearAvailabilityState();
}

function updateHotelCheckIn(date) {
  bookingForm.booking_from_time = date ? `${date}T14:00:00` : '';
}

function updateHotelCheckOut(date) {
  bookingForm.booking_to_time = date ? `${date}T11:00:00` : '';
}

function buildLocalDateTime(dateStr, timeStr) {
  if (!dateStr || !timeStr) return ''
  // timeStr is "HH:MM" or "HH:MM:SS"
  const timeOnly = timeStr.length > 5 ? timeStr.slice(0, 5) : timeStr
  // Parse as local time by constructing YYYY-MM-DDTHH:MM explicitly as local
  // This avoids the browser interpreting "T09:00" as UTC
  const [year, month, day] = dateStr.split('-').map(Number)
  const [hour, minute] = timeOnly.split(':').map(Number)
  const d = new Date(year, month - 1, day, hour, minute, 0, 0)
  // Format as YYYY-MM-DDTHH:MM using local timezone
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function formatSlotTime(time) {
  if (!time) return ''
  // time is a string like "09:00:00" (Python time object serialized) or "2026-05-18T09:00:00"
  // Find the first ':' to locate the time portion
  const firstColon = time.indexOf(':')
  if (firstColon === -1) return ''
  // e.g. "09:00:00" → firstColon=2, extract slice(0,5) = "09:00"
  // e.g. "2026-05-18T09:00:00" → firstColon=11, extract slice(11,16) = "09:00"
  return time.slice(Math.max(0, firstColon - 2), firstColon + 3)
}

function selectBookingSlot(slotId) {
  bookingForm.selectedSlotId = slotId
  const slot = bookingAvailableSlots.value.find(s => String(s.slot_id) === String(slotId))
  if (!slot) return
  const date = bookingDateValue.value
  // slot.start_time / slot.end_time are Python time objects serialized as "HH:MM:SS" strings
  // e.g. "09:00:00" → extract HH:MM = "09:00"
  const start = slot.start_time ? String(slot.start_time).slice(0, 5) : ''
  const end = slot.end_time ? String(slot.end_time).slice(0, 5) : ''
  bookingForm.booking_from_time = date && start ? buildLocalDateTime(date, start) : bookingForm.booking_from_time
  bookingForm.booking_to_time = date && end ? buildLocalDateTime(date, end) : bookingForm.booking_to_time
}

function updateBookingDate(date) {
  bookingSelectedDate.value = date || ''
  clearSelectedBookingSlot()
  bookingAvailability.value = null
  bookingAvailableSlots.value = []
  bookingAvailabilityError.value = ''
}

async function fetchBookingAvailability() {
  const requestKey = getBookingAvailabilityRequestKey()
  activeBookingAvailabilityRequestKey = requestKey
  const serviceId = selectedServiceId.value
  const date = bookingDateValue.value
  const people = bookingForm.amount_of_people || 1
  if (!shouldFetchBookingAvailability()) {
    clearAvailabilityState()
    return
  }
  bookingLoadingAvailability.value = true
  bookingAvailabilityError.value = ''
  try {
    const response = await availabilityAPI.getServiceAvailability(serviceId, date, people)
    if (activeBookingAvailabilityRequestKey !== requestKey) {
      return
    }

    bookingAvailability.value = response.data
    bookingAvailableSlots.value = (response.data?.slots || []).filter(s => s.is_available)
    if (
      bookingForm.selectedSlotId
      && (!selectedSlot.value || selectedSlot.value.remaining_capacity < people)
    ) {
      clearSelectedBookingSlot()
    }
  } catch (err) {
    if (activeBookingAvailabilityRequestKey !== requestKey) {
      return
    }

    bookingAvailabilityError.value = 'Unable to load availability. Please try again.'
    bookingAvailableSlots.value = []
  } finally {
    if (activeBookingAvailabilityRequestKey === requestKey) {
      bookingLoadingAvailability.value = false
    }
  }
}

watch(
  [
    showBooking,
    selectedServiceId,
    bookingDateValue,
    () => bookingForm.amount_of_people,
  ],
  () => {
    refreshBookingAvailability()
  },
)

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
  if (!selectedServiceId.value) {
    bookingError.value = 'Please choose a service before continuing.';
    return false;
  }
  if (!bookingForm.bookers_name.trim()) {
    bookingError.value = "Booker's name is required.";
    return false;
  }
  if (!bookingDateValue.value) {
    bookingError.value = isHotelType.value
      ? 'Please choose both check-in and check-out dates.'
      : 'Please choose a booking date first.';
    return false;
  }
  if (isHotelType.value && bookingAvailability.value && bookingAvailability.value.is_open === false) {
    bookingError.value = 'This service is unavailable for the selected check-in date.';
    return false;
  }
  if (!isHotelType.value && bookingAvailabilityError.value) {
    bookingError.value = 'Availability could not be loaded. Please try another date.';
    return false;
  }
  if (!isHotelType.value && bookingAvailableSlots.value.length === 0) {
    bookingError.value = 'No time slots are available for the selected date.';
    return false;
  }
  if (!isHotelType.value && !selectedSlot.value) {
    bookingError.value = isRestaurantType.value
      ? 'Please choose a reservation time before continuing.'
      : 'Please choose a time slot before continuing.';
    return false;
  }
  if (!bookingForm.booking_from_time || !bookingForm.booking_to_time) {
    bookingError.value = isHotelType.value
      ? 'Please choose both check-in and check-out dates.'
      : 'Please choose a valid time slot before continuing.';
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

  pendingBookingData.value = {
    service_id: selectedServiceId.value,
    service_slot_id: selectedSlot.value?.slot_id ?? null,
    bookers_name: bookingForm.bookers_name.trim(),
    amount_of_people: bookingForm.amount_of_people || 1,
    booking_from_time: bookingForm.booking_from_time,
    booking_to_time: bookingForm.booking_to_time,
    special_requests: bookingForm.special_requests.trim() || null,
  };

  if (isRestaurantType.value) {
    bookingSubmitting.value = true;
    try {
      const response = await bookingsAPI.create(pendingBookingData.value);
      const createdBooking = response.data;
      const bookingId = createdBooking.booking_id || createdBooking.id;
      const isApprovedReservation = createdBooking.status === 'approved';
      toastStore.show(
        isApprovedReservation ? 'Reservation confirmed.' : 'Reservation created successfully.',
        'success',
      );
      pendingBookingData.value = null;
      handleCloseBooking();
      router.push(`/bookings/${bookingId}`);
    } catch (err) {
      bookingError.value = err.response?.data?.detail || 'Failed to create reservation. Please try again.';
      toastStore.show('Failed to create reservation.', 'error');
    } finally {
      bookingSubmitting.value = false;
    }
    return;
  }

  receiptError.value = '';
  receiptPricingFallbackNotice.value = '';
  receiptPricingLoading.value = true;
  try {
    const response = await pricingAPI.getListingPrice(route.params.id, {
      service_id: selectedServiceId.value,
    });
    currentServiceFeePercent.value = normalizeFractionalPercent(
      response.data?.service_fee_percent ?? 0.10,
    );
  } catch {
    currentServiceFeePercent.value = 0.10;
    receiptPricingFallbackNotice.value = 'Live pricing could not be loaded, so this quote is using the default 10% service fee.'
  } finally {
    receiptPricingLoading.value = false;
  }
  showReceiptModal.value = true;
}

async function confirmBookingFromReceipt() {
  if (!pendingBookingData.value) {
    receiptError.value = 'No booking data. Please start again.';
    return;
  }

  confirming.value = true;
  receiptError.value = '';
  try {
    const response = await bookingsAPI.create(pendingBookingData.value);
    const createdBooking = response.data;
    const bookingId = createdBooking.booking_id || createdBooking.id;
    toastStore.show('Booking created successfully.', 'success');
    showReceiptModal.value = false;
    pendingBookingData.value = null;
    handleCloseBooking();
    router.push(`/bookings/${bookingId}`);
  } catch (err) {
    receiptError.value = err.response?.data?.detail || 'Failed to confirm booking. Please try again.';
    toastStore.show('Failed to create booking.', 'error');
  } finally {
    confirming.value = false;
  }
}

function handleBackToForm() {
  showReceiptModal.value = false;
  receiptError.value = '';
}

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

watch(
  () => route.params.id,
  (listingId) => {
    loadListingDetail(listingId);
  },
  { immediate: true },
)

onBeforeUnmount(() => {
  stopSlideshow();
});
</script>
