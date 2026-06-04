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

          <div v-if="reviews.length > 0" class="mt-4 flex gap-4">
            <select v-model="reviewFilters.rating" class="rounded-lg border border-slate-200 px-3 py-2 text-sm">
              <option :value="null">All Ratings</option>
              <option v-for="n in 5" :key="n" :value="n">{{ n }} star{{ n > 1 ? 's' : '' }}</option>
            </select>
            <select v-model="reviewFilters.mainLabel" class="rounded-lg border border-slate-200 px-3 py-2 text-sm">
              <option :value="null">All Categories</option>
              <option v-for="label in availableLabels" :key="label" :value="label">{{ label }}</option>
            </select>
          </div>

          <div
            v-if="reviews.length === 0"
            class="mt-6 rounded-3xl border border-slate-200 bg-white px-6 py-12 text-center shadow-sm">
            <p class="text-base font-medium text-slate-500">No reviews yet.</p>
            <p class="mt-1 text-sm text-slate-400">Be the first to share your experience.</p>
          </div>

          <div v-else class="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div
              v-for="review in filteredReviews"
              :key="review.id"
              class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
            >
              <div class="flex items-start justify-between gap-4">
                <div class="flex items-center gap-3">
                  <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-cyan-50 text-sm font-bold text-cyan-700">
                    {{ review.user_name?.charAt(0).toUpperCase() || 'G' }}
                  </div>
                  <div>
                    <p class="text-sm font-semibold text-slate-900">{{ review.user_name || 'Guest' }}</p>
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

              <div v-if="review.main_label && review.main_label !== '(none)'" class="mt-3">
                <span class="inline-flex items-center rounded-full bg-cyan-100 px-2.5 py-0.5 text-xs font-medium text-cyan-800">
                  {{ review.main_label }}
                </span>
              </div>

              <p v-if="review.comment" class="mt-3 text-sm leading-6 text-slate-600">
                {{ review.comment }}
              </p>

              <div v-if="review.business_reply" class="mt-4 rounded-lg bg-slate-50 p-4 border border-slate-100">
                <div class="flex items-center gap-2 mb-2">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-cyan-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  <span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Business Response</span>
                </div>
                <p class="text-sm text-slate-700">{{ review.business_reply.description }}</p>
                <p class="text-xs text-slate-400 mt-2">— {{ review.business_reply.user_name || 'Business' }}</p>
                <div v-if="isReplyOwner(review.business_reply)" class="mt-3 flex gap-3 border-t border-slate-200 pt-3">
                  <button @click="openEditReplyModal(review)" class="text-xs text-cyan-600 hover:text-cyan-700">Edit</button>
                  <button @click="confirmDeleteReply(review)" class="text-xs text-red-600 hover:text-red-700">Delete</button>
                </div>
              </div>

              <div v-else-if="canReply && !review.business_reply" class="mt-4">
                <button @click="openReplyModal(review)" class="text-sm text-cyan-600 hover:text-cyan-700">
                  Respond as Business
                </button>
              </div>

              <div v-if="isOwner(review)" class="mt-4 flex gap-3 border-t border-slate-100 pt-4">
                <button @click="openEditModal(review)" class="text-sm text-cyan-600 hover:text-cyan-700">Edit</button>
                <button @click="confirmDelete(review)" class="text-sm text-red-600 hover:text-red-700">Delete</button>
              </div>
            </div>
          </div>
        </div>

        <ReviewModal
          v-if="showReviewModal"
          :mode="editingReview ? 'edit' : 'submit'"
          :review="editingReview"
          :listing-id="listing.id"
          @close="showReviewModal = false"
          @success="handleReviewSuccess"
        />

        <BusinessReplyModal
          v-if="showReplyModal"
          :mode="editingReply ? 'edit' : 'submit'"
          :review-id="replyingToReview?.id"
          :reply="editingReply"
          @close="showReplyModal = false"
          @success="handleReplySuccess"
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
              <label v-if="bookingAvailableSlots.length > 0" class="block mt-3">
                <span class="text-sm font-semibold text-slate-700">
                  {{ isRestaurantType ? 'Choose a reservation time' : 'Choose a time slot' }}
                </span>
                <select
                  :value="selectedSlotIdValue"
                  class="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100"
                  @change="selectBookingSlot($event.target.value)"
                >
                  <option value="">-- Select a time slot --</option>
                  <option
                    v-for="slot in bookingAvailableSlots"
                    :key="slot.slot_id"
                    :value="String(slot.slot_id)"
                    :disabled="slot.remaining_capacity < (bookingForm.amount_of_people || 1)"
                  >
                    {{ formatSlotTime(slot.start_time) }} - {{ formatSlotTime(slot.end_time) }}
                    <span v-if="slot.remaining_capacity < (bookingForm.amount_of_people || 1)">
                      ({{ slot.remaining_capacity }} left - not enough for {{ bookingForm.amount_of_people || 1 }} people)
                    </span>
                    <span v-else>
                      ({{ slot.remaining_capacity }} spots left)
                    </span>
                  </option>
                </select>
              </label>

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
              <span class="text-slate-600">Service Fee</span>
              <span class="font-medium text-slate-900">${{ receiptServiceFee.toFixed(2) }}</span>
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
import { ref, computed, onMounted} from 'vue';
import {useRoute, useRouter} from 'vue-router';
import { listingsAPI, reviewsAPI, businessReplyAPI } from '../services/api';
import { useAuthStore } from '../stores/auth';
import { useToastStore } from '../stores/toast';
import ReviewModal from '../components/ReviewModal.vue';
import BusinessReplyModal from '../components/BusinessReplyModal.vue';
import { ref, computed, onMounted, onBeforeUnmount, reactive, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { bookingsAPI, listingsAPI, reviewsAPI, servicesAPI, availabilityAPI } from '../services/api'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'
import HotelDetailSection from '../components/listings/detail-sections/HotelDetailSection.vue'
import RestaurantDetailSection from '../components/listings/detail-sections/RestaurantDetailSection.vue'
import TourDetailSection from '../components/listings/detail-sections/TourDetailSection.vue'
import ActivityDetailSection from '../components/listings/detail-sections/ActivityDetailSection.vue'
import ListingBookingServiceCarousel from '../components/listings/ListingBookingServiceCarousel.vue'

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const toastStore = useToastStore();

const listing = ref(null)
const reviews = ref([]);
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
const brokenImages = ref(new Set());
let heroInterval = null;
const bookingForm = reactive({
  service_id: '',
  bookers_name: '',
  amount_of_people: 1,
  booking_from_time: '',
  booking_to_time: '',
  special_requests: '',
  _selectedSlotId: '',  // internal tracking for slot selection
});

const showReceiptModal = ref(false);
const pendingBookingData = ref(null);
const confirming = ref(false);
const receiptError = ref('');

const showReviewModal = ref(false);
const editingReview = ref(null);
const reviewFilters = ref({ rating: null, mainLabel: null });
const showReplyModal = ref(false);
const editingReply = ref(null);
const replyingToReview = ref(null);

const isLoggedIn = computed(() => authStore.isAuthenticated);
const currentUser = computed(() => authStore.user);
const userRole = computed(() => authStore.role);

const userReview = computed(() => {
  if (!currentUser.value) return null;
  return reviews.value.find(r => r.user_id === currentUser.value.id) || null;
});

const canWriteReview = computed(() => isLoggedIn.value && !userReview.value);

const canReply = computed(() => {
  const role = userRole.value;
  return (role === 'business' || role === 'employee');
});

const isOwner = (review) => {
  return currentUser.value && review.user_id === currentUser.value.id;
};

const isReplyOwner = (reply) => {
  if (!reply || !currentUser.value) return false;
  return reply.user_id === currentUser.value.id;
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
  fetchListings();
};

const confirmDelete = async (review) => {
  if (confirm('Are you sure you want to delete this review?')) {
    try {
      await reviewsAPI.delete(review.id);
      toastStore.show('Review deleted', 'success');
      fetchListings();
    } catch (err) {
      console.error('Failed to delete review', err);
      toastStore.show('Failed to delete review', 'error');
    }
  }
};

const handleWriteReviewClick = () => {
  if (!isLoggedIn.value) {
    toastStore.show('Sign in to write a review.', 'info');
    router.push({ name: 'Login', query: { redirect: route.fullPath } });
    return;
  }
  openSubmitModal();
};

const openReplyModal = (review) => {
  replyingToReview.value = review;
  editingReply.value = review.business_reply || null;
  showReplyModal.value = true;
};

const openEditReplyModal = (review) => {
  replyingToReview.value = review;
  editingReply.value = review.business_reply;
  showReplyModal.value = true;
};

const handleReplySuccess = (message) => {
  showReplyModal.value = false;
  toastStore.show(message, 'success');
  fetchListings();
};

const confirmDeleteReply = async (review) => {
  if (confirm('Are you sure you want to delete your response?')) {
    try {
      await businessReplyAPI.delete(review.id);
      toastStore.show('Response deleted', 'success');
      fetchListings();
    } catch (err) {
      console.error('Failed to delete reply:', err);
      toastStore.show('Failed to delete response', 'error');
    }
  }
};

const filteredReviews = computed(() => {
  let result = reviews.value;
  if (reviewFilters.value.rating) {
    result = result.filter(r => r.rating === reviewFilters.value.rating);
  }
  if (reviewFilters.value.mainLabel) {
    result = result.filter(r => r.main_label === reviewFilters.value.mainLabel);
  }
  return result;
});

const availableLabels = computed(() => {
  const labels = reviews.value.map(r => r.main_label).filter(Boolean);
  return [...new Set(labels)];
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
  if (!bookingForm._selectedSlotId) return null
  return bookingAvailableSlots.value.find(s => String(s.slot_id) === String(bookingForm._selectedSlotId)) || null
})

const hotelCheckOutDate = computed(() => bookingForm.booking_to_time ? bookingForm.booking_to_time.slice(0, 10) : '')

const bookingDateValue = computed(() => {
  if (!isHotelType.value) return bookingSelectedDate.value
  return bookingForm.booking_from_time ? bookingForm.booking_from_time.slice(0, 10) : ''
})

const selectedSlotIdValue = computed(() => bookingForm._selectedSlotId || '')
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

const SERVICE_FEE_PERCENT = 0.10;

const receiptSubtotal = computed(() => {
  if (!selectedService.value) return 0;
  const price = Number(selectedService.value.price) || 0;
  const people = bookingForm.amount_of_people || 1;
  if (isHotelType.value) {
    // Calculate number of nights for hotel booking
    const checkIn = bookingForm.booking_from_time ? new Date(bookingForm.booking_from_time) : null;
    const checkOut = bookingForm.booking_to_time ? new Date(bookingForm.booking_to_time) : null;
    let nights = 1;
    if (checkIn && checkOut && checkOut > checkIn) {
      const diffMs = checkOut.getTime() - checkIn.getTime();
      nights = Math.max(1, Math.round(diffMs / (1000 * 60 * 60 * 24)));
    }
    return price * nights;
  }
  return price * people;
});

// Helper to calculate hotel nights for receipt display
const hotelNightsForReceipt = computed(() => {
  const checkIn = bookingForm.booking_from_time ? new Date(bookingForm.booking_from_time) : null;
  const checkOut = bookingForm.booking_to_time ? new Date(bookingForm.booking_to_time) : null;
  if (checkIn && checkOut && checkOut > checkIn) {
    const diffMs = checkOut.getTime() - checkIn.getTime();
    return Math.max(1, Math.round(diffMs / (1000 * 60 * 60 * 24)));
  }
  return 1;
});

const receiptServiceFee = computed(() => receiptSubtotal.value * SERVICE_FEE_PERCENT);

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

function resetBookingForm() {
  bookingForm.service_id = selectedServiceId.value || '';
  bookingForm.bookers_name = getUserFullName();
  bookingForm.amount_of_people = 1;
  bookingForm.booking_from_time = '';
  bookingForm.booking_to_time = '';
  bookingForm.special_requests = '';
  bookingForm._selectedSlotId = '';
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

async function loadBookingServices() {
  if (!listing.value?.id) {
    bookingServices.value = [];
    selectedServiceId.value = '';
    return;
  }

  bookingServicesLoading.value = true;
  bookingError.value = '';
  try {
    const response = await servicesAPI.getAll({ listing_id: listing.value.id });
    bookingServices.value = Array.isArray(response.data) ? response.data : [];
    applyServiceSelectionFallback();
  } catch (err) {
    console.error('Failed to load active services for listing detail', err);
    bookingServices.value = [];
    selectedServiceId.value = '';
    bookingError.value = 'Failed to load active services for this listing.';
  } finally {
    bookingServicesLoading.value = false;
  }
}

function handleSelectService(serviceId) {
  selectedServiceId.value = serviceId;
}

async function handleOpenBooking() {
  await authStore.initialize();
  if (!authStore.isAuthenticated) {
    router.push({ name: 'Login', query: { redirect: route.fullPath } });
    return;
  }

  if (!bookingServices.value.length && !bookingServicesLoading.value) {
    await loadBookingServices();
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
  bookingForm._selectedSlotId = slotId
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
  bookingForm.booking_from_time = ''
  bookingForm.booking_to_time = ''
  bookingForm._selectedSlotId = ''
  bookingAvailability.value = null
  bookingAvailableSlots.value = []
  bookingAvailabilityError.value = ''
}

async function fetchBookingAvailability() {
  const serviceId = selectedServiceId.value
  const date = bookingDateValue.value
  const people = bookingForm.amount_of_people || 1
  if (!serviceId || !date || isHotelType.value) {
    clearAvailabilityState()
    return
  }
  bookingLoadingAvailability.value = true
  bookingAvailabilityError.value = ''
  try {
    const response = await availabilityAPI.getServiceAvailability(serviceId, date, people)
    bookingAvailability.value = response.data
    bookingAvailableSlots.value = (response.data?.slots || []).filter(s => s.is_available)
    if (
      bookingForm._selectedSlotId
      && (!selectedSlot.value || selectedSlot.value.remaining_capacity < people)
    ) {
      bookingForm._selectedSlotId = ''
      bookingForm.booking_from_time = ''
      bookingForm.booking_to_time = ''
    }
  } catch (err) {
    bookingAvailabilityError.value = 'Unable to load availability. Please try again.'
    bookingAvailableSlots.value = []
  } finally {
    bookingLoadingAvailability.value = false
  }
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
      toastStore.show('Reservation created successfully.', 'success');
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

const fetchListings = async () => {
  loading.value = true;
  try {
    const listingResponse = await listingsAPI.getById(route.params.id);
    listing.value = listingResponse.data;
    await loadBookingServices();

    try {
      const reviewResponse = await reviewsAPI.getAll({ listing_id: route.params.id });
      reviews.value = reviewResponse.data;
    } catch (reviewError) {
      reviews.value = [];
      console.error('Failed to load reviews', reviewError);
    }
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

onMounted(() => {
  fetchListings();
});

onBeforeUnmount(() => {
  stopSlideshow();
});
</script>
