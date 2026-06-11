<template>
  <div class="min-h-screen bg-slate-50">
    <div class="border-b border-slate-200 bg-white">
      <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <p class="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-600">
          Admin Panel
        </p>
        <h1 class="mt-3 text-3xl font-bold text-slate-900 sm:text-4xl">
          Listing Moderation
        </h1>
        <p class="mt-3 max-w-2xl text-sm text-slate-500">
          Review listing submissions, inspect everything owners and employees entered, and
          moderate visibility from one place.
        </p>
      </div>
    </div>

    <div class="mx-auto max-w-7xl space-y-8 px-4 py-10 sm:px-6 lg:px-8">
      <div
        v-if="loading"
        class="rounded-3xl border border-slate-200 bg-white px-6 py-16 text-center shadow-sm">
        <svg
          class="mx-auto h-8 w-8 animate-spin text-cyan-500"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24">
          <circle
            class="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            stroke-width="4"/>
          <path
            class="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"/>
        </svg>
        <p class="mt-4 text-sm text-slate-500">Loading listing moderation data...</p>
      </div>

      <div
        v-else-if="loadError"
        class="rounded-3xl border border-red-200 bg-white px-6 py-8 text-center shadow-sm">
        <p class="text-sm font-semibold text-red-600">{{ loadError }}</p>
        <button
          @click="loadAdminData"
          class="mt-4 rounded-2xl bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800">
          Retry
        </button>
      </div>

      <template v-else>
        <div class="grid grid-cols-2 gap-4 lg:grid-cols-6">
          <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <p class="text-sm font-medium text-slate-500">Moderated Listings</p>
            <p class="mt-2 text-3xl font-bold text-slate-900">{{ stats.totalListings }}</p>
          </div>
          <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <p class="text-sm font-medium text-slate-500">Pending</p>
            <p class="mt-2 text-3xl font-bold text-amber-500">{{ stats.pendingListings }}</p>
          </div>
          <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <p class="text-sm font-medium text-slate-500">Active</p>
            <p class="mt-2 text-3xl font-bold text-emerald-500">{{ stats.activeListings }}</p>
          </div>
          <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <p class="text-sm font-medium text-slate-500">Suspended</p>
            <p class="mt-2 text-3xl font-bold text-orange-500">{{ stats.suspendedListings }}</p>
          </div>
          <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <p class="text-sm font-medium text-slate-500">Rejected</p>
            <p class="mt-2 text-3xl font-bold text-red-500">{{ stats.rejectedListings }}</p>
          </div>
          <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <p class="text-sm font-medium text-slate-500">Inactive</p>
            <p class="mt-2 text-3xl font-bold text-slate-500">{{ stats.inactiveListings }}</p>
          </div>
        </div>

        <div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div class="flex flex-1 flex-wrap gap-2">
            <button
              v-for="tab in filterTabs"
              :key="tab.value"
              @click="filterTab = tab.value"
              class="rounded-2xl px-5 py-2 text-sm font-semibold transition"
              :class="
                filterTab === tab.value
                  ? 'bg-cyan-500 text-slate-950 shadow-sm'
                  : 'border border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:text-slate-900'
              "
            >
              {{ tab.label }}
            </button>
          </div>

          <div class="w-full lg:w-72 lg:flex-none">
            <label for="admin-listing-search" class="sr-only">Search listings</label>
            <div class="relative">
              <input
                id="admin-listing-search"
                v-model="searchQuery"
                type="search"
                placeholder="Search listings"
                class="w-full rounded-2xl border border-slate-200 bg-white py-2.5 px-4 text-sm text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-cyan-400"
              />
            </div>
          </div>
        </div>

        <div
          v-if="filteredListings.length === 0"
          class="rounded-3xl border border-slate-200 bg-white px-6 py-20 text-center shadow-sm"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="mx-auto h-12 w-12 text-slate-300"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.5"
              d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
            />
          </svg>
          <p class="mt-4 text-base font-medium text-slate-500">No listings found.</p>
          <p class="mt-1 text-sm text-slate-400">
            No moderated listings match the current filters or search.
          </p>
        </div>

        <div v-else class="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3">
          <article
            v-for="listing in filteredListings"
            :key="listing.id"
            class="group overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-md"
          >
            <div class="relative h-52 overflow-hidden bg-slate-100">
              <img
                v-if="listing.image_urls?.length"
                :src="listing.image_urls[0]"
                :alt="listing.title"
                class="h-full w-full object-cover transition duration-500 group-hover:scale-105"/>
              <div v-else class="flex h-full w-full items-center justify-center text-slate-300">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-14 w-14"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="1.5"
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
              </div>

              <div class="absolute left-3 top-3">
                <span
                  class="rounded-xl px-3 py-1 text-xs font-semibold"
                  :class="statusBadgeClass(listing.status)">
                  {{ statusLabel(listing.status) }}
                </span>
              </div>

              <div class="absolute right-3 top-3">
                <span
                  class="rounded-xl bg-slate-900/75 px-3 py-1 text-xs font-semibold text-white backdrop-blur-sm"
                >
                  {{ listing.business_type_name || 'Listing' }}
                </span>
              </div>
            </div>

            <div class="space-y-4 p-6">
              <div>
                <h2 class="text-base font-bold leading-snug text-slate-900">{{ listing.title }}</h2>
                <p class="mt-1 flex items-center gap-1.5 text-sm text-slate-500">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-4 w-4 shrink-0 text-slate-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                    />
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                    />
                  </svg>
                  {{ formatLocation(listing.address) }}
                </p>
                <p class="mt-1 text-xs text-slate-400">
                  Submitted by
                  <span class="font-semibold text-slate-600">
                    {{ listing.business_name || 'Unknown business' }}
                  </span>
                  &middot; {{ formatDate(listing.created_at) }}
                </p>
              </div>

              <p class="line-clamp-3 text-sm leading-6 text-slate-500">
                {{ listing.description || 'No description provided.' }}
              </p>

              <div class="flex items-center justify-between border-t border-slate-100 pt-4">
                <div>
                  <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                    Base price
                  </p>
                  <p class="mt-1 text-lg font-bold text-slate-900">
                    {{ formatCurrency(listing.base_price) }}
                  </p>
                </div>
                <div class="text-right">
                  <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                    Reviews
                  </p>
                  <p class="mt-1 text-sm font-semibold text-slate-700">
                    {{ formatReviewSummary(listing) }}
                  </p>
                </div>
              </div>

              <div class="flex flex-wrap gap-2 border-t border-slate-100 pt-4">
                <button
                  @click="openDetailModal(listing.id)"
                  class="flex-1 rounded-2xl border border-slate-200 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50"
                >
                  View Details
                </button>
                <button
                  v-if="canActivateListing(listing)"
                  @click="openConfirmModal('activate', listing)"
                  :disabled="decisionSubmitting"
                  class="flex-1 rounded-2xl bg-emerald-500 py-2 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0"
                >
                  Activate
                </button>
                <button
                  v-if="canRejectListing(listing)"
                  @click="openConfirmModal('reject', listing)"
                  :disabled="decisionSubmitting"
                  class="flex-1 rounded-2xl border border-red-100 py-2 text-sm font-semibold text-red-500 transition hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-60">
                  Reject
                </button>
                <button
                  v-if="canSuspendListing(listing)"
                  @click="openConfirmModal('suspend', listing)"
                  :disabled="decisionSubmitting"
                  class="flex-1 rounded-2xl border border-orange-100 py-2 text-sm font-semibold text-orange-600 transition hover:bg-orange-50 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  Suspend
                </button>
              </div>
            </div>
          </article>
        </div>
      </template>
    </div>

    <div
      v-if="showDetailModal"
      class="fixed inset-0 z-50 flex items-center justify-center px-4"
      @click.self="closeDetailModal"
    >
      <div class="absolute inset-0 bg-slate-950/60 backdrop-blur-sm"></div>
      <div class="relative flex max-h-[92vh] w-full max-w-6xl flex-col overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-2xl">
        <div class="flex items-start justify-between gap-4 border-b border-slate-100 px-6 py-5 sm:px-8">
          <div class="min-w-0">
            <p class="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-600">
              Listing Review
            </p>
            <div class="mt-2 flex flex-wrap items-center gap-3">
              <span
                v-if="detailListing"
                class="rounded-xl px-3 py-1 text-xs font-semibold"
                :class="statusBadgeClass(detailListing.status)"
              >
                {{ statusLabel(detailListing.status) }}
              </span>
              <h2 class="truncate text-2xl font-bold text-slate-900">
                {{ detailListing?.title || 'Listing details' }}
              </h2>
            </div>
            <p class="mt-2 text-sm text-slate-500">
              Submitted by
              <span class="font-semibold text-slate-700">
                {{ detailListing?.business_name || 'Unknown business' }}
              </span>
            </p>
          </div>

          <div class="flex shrink-0 items-center gap-2">
            <button
              v-if="detailListing && canActivateListing(detailListing)"
              @click="openConfirmModal('activate', detailListing)"
              :disabled="decisionSubmitting"
              class="rounded-2xl bg-emerald-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Activate
            </button>
            <button
              v-if="detailListing && canRejectListing(detailListing)"
              @click="openConfirmModal('reject', detailListing)"
              :disabled="decisionSubmitting"
              class="rounded-2xl border border-red-100 px-4 py-2 text-sm font-semibold text-red-500 transition hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Reject
            </button>
            <button
              v-if="detailListing && canSuspendListing(detailListing)"
              @click="openConfirmModal('suspend', detailListing)"
              :disabled="decisionSubmitting"
              class="rounded-2xl border border-orange-100 px-4 py-2 text-sm font-semibold text-orange-600 transition hover:bg-orange-50 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Suspend
            </button>
            <button
              @click="closeDetailModal"
              class="flex h-10 w-10 items-center justify-center rounded-2xl border border-slate-200 text-slate-500 transition hover:bg-slate-50"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div class="overflow-y-auto px-6 py-6 sm:px-8">
          <div v-if="detailLoading" class="py-16 text-center">
            <svg
              class="mx-auto h-8 w-8 animate-spin text-cyan-500"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
              />
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
              />
            </svg>
            <p class="mt-4 text-sm text-slate-500">Loading full listing details...</p>
          </div>

          <div
            v-else-if="detailListingError && !detailListing"
            class="rounded-3xl border border-red-200 bg-red-50 px-6 py-8 text-center"
          >
            <p class="text-sm font-semibold text-red-600">{{ detailListingError }}</p>
          </div>

          <div v-else-if="detailListing" class="space-y-8">
            <div
              v-if="detailListingError"
              class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600"
            >
              {{ detailListingError }}
            </div>

            <div class="grid gap-8 lg:grid-cols-[1.4fr_1fr]">
              <div class="space-y-4">
                <div class="overflow-hidden rounded-3xl border border-slate-200 bg-slate-100">
                  <img
                    v-if="detailCurrentImage"
                    :src="detailCurrentImage"
                    :alt="detailListing.title"
                    class="h-80 w-full object-cover"
                  />
                  <div v-else class="flex h-80 items-center justify-center text-slate-300">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      class="h-16 w-16"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="1.5"
                        d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                      />
                    </svg>
                  </div>
                </div>

                <div v-if="detailImages.length > 1" class="flex flex-wrap gap-3">
                  <button
                    v-for="(image, index) in detailImages"
                    :key="`${image}-${index}`"
                    @click="detailImageIndex = index"
                    class="overflow-hidden rounded-2xl border-2 transition"
                    :class="detailImageIndex === index ? 'border-cyan-400' : 'border-transparent'">
                    <img :src="image" :alt="`${detailListing.title} ${index + 1}`" class="h-16 w-16 object-cover" />
                  </button>
                </div>
              </div>

              <div class="space-y-4">
                <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                  <p class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-400">
                    Listing Summary
                  </p>
                  <div class="mt-4 space-y-4">
                    <div class="grid grid-cols-2 gap-4">
                      <div>
                        <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                          Type
                        </p>
                        <p class="mt-1 text-sm font-semibold text-slate-800">
                          {{ detailListing.business_type_name || 'Unknown type' }}
                        </p>
                      </div>
                      <div>
                        <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                          Base Price
                        </p>
                        <p class="mt-1 text-sm font-semibold text-slate-800">
                          {{ formatCurrency(detailListing.base_price) }}
                        </p>
                      </div>
                      <div>
                        <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                          Created
                        </p>
                        <p class="mt-1 text-sm font-semibold text-slate-800">
                          {{ formatDateTime(detailListing.created_at) }}
                        </p>
                      </div>
                      <div>
                        <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                          Updated
                        </p>
                        <p class="mt-1 text-sm font-semibold text-slate-800">
                          {{ formatDateTime(detailListing.updated_at) }}
                        </p>
                      </div>
                    </div>

                    <div>
                      <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                        Reviews
                      </p>
                      <p class="mt-1 text-sm font-semibold text-slate-800">
                        {{ formatReviewSummary(detailListing) }}
                      </p>
                    </div>

                  </div>
                </div>

                <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                  <p class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-400">
                    Contact &amp; Location
                  </p>
                  <div class="mt-4 space-y-4">
                    <div>
                      <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                        Address
                      </p>
                      <p class="mt-1 text-sm text-slate-700">{{ formatFullAddress(detailListing.address) }}</p>
                    </div>
                    <div class="grid gap-4 sm:grid-cols-2">
                      <div>
                        <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                          Phone
                        </p>
                        <p class="mt-1 text-sm text-slate-700">{{ detailListing.phone_number || '-' }}</p>
                      </div>
                      <div>
                        <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                          Email
                        </p>
                        <p class="mt-1 text-sm text-slate-700">{{ detailListing.email_address || '-' }}</p>
                      </div>
                    </div>
                    <div>
                      <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                        Coordinates
                      </p>
                      <p class="mt-1 text-sm text-slate-700">{{ formatCoordinates(detailListing.location) }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-[0.25em] text-cyan-600">
                Description
              </p>
              <p class="mt-3 whitespace-pre-line text-sm leading-7 text-slate-600">
                {{ detailListing.description || 'No description provided.' }}
              </p>
            </section>

            <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <div class="flex items-center justify-between gap-3">
                <div>
                  <p class="text-xs font-semibold uppercase tracking-[0.25em] text-cyan-600">
                    Services
                  </p>
                  
                </div>
                <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                  {{ visibleServices.length }} {{ visibleServices.length === 1 ? 'service' : 'services' }}
                </span>
              </div>

              <div
                v-if="detailServicesError"
                class="mt-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600"
              >
                {{ detailServicesError }}
              </div>

              <div v-else-if="visibleServices.length === 0" class="mt-4 rounded-2xl bg-slate-50 px-6 py-10 text-center">
                <p class="text-sm font-medium text-slate-500">No services found for this listing.</p>
              </div>

              <div v-else class="mt-4 grid grid-cols-1 gap-4 xl:grid-cols-2">
                <article
                  v-for="service in visibleServices"
                  :key="service.service_id"
                  class="rounded-3xl border border-slate-200 bg-slate-50 p-5"
                >
                  <div class="flex items-start justify-between gap-3">
                    <div class="min-w-0">
                      <h3 class="truncate text-base font-bold text-slate-900">{{ service.name || 'Unnamed service' }}</h3>
                      <p v-if="service.description" class="mt-1 text-sm text-slate-500">
                        {{ service.description }}
                      </p>
                    </div>
                    <span
                      class="shrink-0 rounded-xl px-2.5 py-1 text-xs font-semibold"
                      :class="service.status === 'active' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-700'"
                    >
                      {{ service.status === 'active' ? 'Active' : 'Inactive' }}
                    </span>
                  </div>

                  <div class="mt-4 grid gap-4 sm:grid-cols-2">
                    <div>
                      <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                        Base Price
                      </p>
                      <p class="mt-1 text-sm font-semibold text-slate-800">
                        {{ formatCurrency(service.price) }}
                      </p>
                    </div>
                    <div>
                      <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                        Seasonal Price
                      </p>
                      <p class="mt-1 text-sm font-semibold text-slate-800">
                        {{ formatCurrency(service.season_price) }}
                      </p>
                    </div>
                    <div>
                      <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                        Capacity
                      </p>
                      <p class="mt-1 text-sm font-semibold text-slate-800">
                        {{ service.capacity ?? '-' }}
                      </p>
                    </div>
                    <div>
                      <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                        Created
                      </p>
                      <p class="mt-1 text-sm font-semibold text-slate-800">
                        {{ formatDateTime(service.created_at) }}
                      </p>
                    </div>
                  </div>

                  <div class="mt-4 space-y-4">
                    <div>
                      <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                        Availability
                      </p>
                      <div class="mt-2">
                        <StructuredDataViewer :value="service.availability" />
                      </div>
                    </div>

                    <div>
                      <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                        Type Data
                      </p>
                      <div class="mt-2">
                        <StructuredDataViewer :value="service.type_data" />
                      </div>
                    </div>
                  </div>
                </article>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>

    <div
      v-if="showConfirmModal"
      class="fixed inset-0 z-[60] flex items-center justify-center px-4"
      @click.self="!decisionSubmitting && (showConfirmModal = false)"
    >
      <div class="absolute inset-0 bg-slate-950/50 backdrop-blur-sm"></div>
      <div class="relative w-full max-w-md rounded-3xl border border-slate-200 bg-white p-8 shadow-2xl">
        <div class="flex items-start gap-4">
          <div
            class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl"
            :class="confirmConfig.iconBackgroundClass"
          >
            <svg
              v-if="confirmAction === 'activate'"
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6"
              :class="confirmConfig.iconClass"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <svg
              v-else-if="confirmAction === 'reject'"
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6"
              :class="confirmConfig.iconClass"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <svg
              v-else
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6"
              :class="confirmConfig.iconClass"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6" />
            </svg>
          </div>

          <div>
            <h3 class="text-lg font-bold text-slate-900">
              {{ confirmConfig.title }}
            </h3>
            <p class="mt-2 text-sm leading-6 text-slate-600">
              <span class="font-semibold text-slate-800">{{ confirmTargetLabel }}</span>
              will be marked as
              <span
                class="font-semibold"
                :class="confirmConfig.textClass"
              >
                {{ confirmConfig.nextStatus }}
              </span>
              and the listing card will update immediately.
            </p>
          </div>
        </div>

        <div class="mt-6 flex gap-3">
          <button
            @click="showConfirmModal = false"
            :disabled="decisionSubmitting"
            class="flex-1 rounded-2xl border border-slate-200 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60">
            Cancel
          </button>
          <button
            @click="confirmDecision"
            :disabled="decisionSubmitting"
            class="flex-1 rounded-2xl py-3 text-sm font-semibold text-white transition hover:-translate-y-0.5"
            :class="confirmConfig.buttonClass"
          >
            {{ decisionSubmitting ? 'Processing...' : confirmConfig.buttonLabel }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

import StructuredDataViewer from '../components/admin/StructuredDataViewer.vue'
import { listingsAPI, servicesAPI } from '../services/api'
import { useToastStore } from '../stores/toast'

const MODERATION_STATUSES = new Set(['pending', 'active', 'rejected', 'inactive', 'suspended'])
const CONFIRM_ACTION_CONFIG = {
  activate: {
    title: 'Activate Listing?',
    nextStatus: 'active',
    buttonLabel: 'Activate',
    successMessage: 'Listing activated.',
    textClass: 'text-emerald-600',
    iconClass: 'text-emerald-500',
    iconBackgroundClass: 'bg-emerald-50',
    buttonClass: 'bg-emerald-500 hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0',
  },
  reject: {
    title: 'Reject Listing?',
    nextStatus: 'rejected',
    buttonLabel: 'Reject',
    successMessage: 'Listing rejected.',
    textClass: 'text-red-600',
    iconClass: 'text-red-500',
    iconBackgroundClass: 'bg-red-50',
    buttonClass: 'bg-red-500 hover:bg-red-400 disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0',
  },
  suspend: {
    title: 'Suspend Listing?',
    nextStatus: 'suspended',
    buttonLabel: 'Suspend',
    successMessage: 'Listing suspended.',
    textClass: 'text-orange-600',
    iconClass: 'text-orange-500',
    iconBackgroundClass: 'bg-orange-50',
    buttonClass: 'bg-orange-500 hover:bg-orange-400 disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0',
  },
}

const toastStore = useToastStore()

const loading = ref(true)
const loadError = ref('')
const decisionSubmitting = ref(false)
const listings = ref([])
const filterTab = ref('all')
const searchQuery = ref('')

const showConfirmModal = ref(false)
const confirmAction = ref('')
const confirmTarget = ref(null)

const showDetailModal = ref(false)
const detailLoading = ref(false)
const detailListing = ref(null)
const detailListingError = ref('')
const detailServices = ref([])
const detailServicesError = ref('')
const detailImageIndex = ref(0)

const filterTabs = [
  { label: 'All', value: 'all' },
  { label: 'Pending', value: 'pending' },
  { label: 'Active', value: 'active' },
  { label: 'Suspended', value: 'suspended' },
  { label: 'Rejected', value: 'rejected' },
  { label: 'Inactive', value: 'inactive' },
]

const filteredListings = computed(() => {
  const normalizedQuery = normalizeSearchText(searchQuery.value)
  const statusFilteredListings =
    filterTab.value === 'all'
      ? listings.value
      : listings.value.filter((listing) => listing.status === filterTab.value)

  if (!normalizedQuery) return statusFilteredListings

  return statusFilteredListings.filter((listing) =>
    buildListingSearchHaystack(listing).includes(normalizedQuery),
  )
})

const stats = computed(() => ({
  totalListings: listings.value.length,
  pendingListings: listings.value.filter((listing) => listing.status === 'pending').length,
  activeListings: listings.value.filter((listing) => listing.status === 'active').length,
  suspendedListings: listings.value.filter((listing) => listing.status === 'suspended').length,
  rejectedListings: listings.value.filter((listing) => listing.status === 'rejected').length,
  inactiveListings: listings.value.filter((listing) => listing.status === 'inactive').length,
}))

const confirmTargetLabel = computed(() => confirmTarget.value?.title || 'this listing')
const confirmConfig = computed(
  () => CONFIRM_ACTION_CONFIG[confirmAction.value] ?? CONFIRM_ACTION_CONFIG.reject,
)

const detailImages = computed(() =>
  Array.isArray(detailListing.value?.image_urls)
    ? detailListing.value.image_urls.filter(Boolean)
    : [],
)

const detailCurrentImage = computed(
  () => detailImages.value[detailImageIndex.value] ?? detailImages.value[0] ?? null,
)

const visibleServices = computed(() =>
  detailServices.value.filter((service) => service?.status !== 'deleted'),
)

function normalizeListingStatus(listing) {
  const status = listing?.status === 'approved' ? 'active' : listing?.status
  return {
    ...listing,
    status,
  }
}

function isModerationVisibleStatus(status) {
  return MODERATION_STATUSES.has(status)
}

function statusLabel(status) {
  if (status === 'active') return 'Active'
  if (status === 'pending') return 'Pending'
  if (status === 'suspended') return 'Suspended'
  if (status === 'rejected') return 'Rejected'
  if (status === 'inactive') return 'Inactive'
  return status ?? 'Unknown'
}

function statusBadgeClass(status) {
  if (status === 'active') return 'bg-emerald-500 text-white'
  if (status === 'pending') return 'bg-amber-400 text-slate-900'
  if (status === 'suspended') return 'bg-orange-500 text-white'
  if (status === 'rejected') return 'bg-red-500 text-white'
  if (status === 'inactive') return 'bg-slate-500 text-white'
  return 'bg-slate-300 text-slate-900'
}

function canActivateListing(listing) {
  return ['pending', 'rejected', 'suspended'].includes(listing?.status)
}

function canRejectListing(listing) {
  return listing?.status === 'pending'
}

function canSuspendListing(listing) {
  return listing?.status === 'active' || listing?.status === 'inactive'
}

function formatDate(value) {
  if (!value) return 'Unknown date'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Unknown date'
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(date)
}

function formatDateTime(value) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '-'
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(date)
}

function formatCurrency(value) {
  const numericValue = Number(value)
  if (!Number.isFinite(numericValue)) return '-'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
  }).format(numericValue)
}

function formatLocation(address) {
  const location = [address?.city, address?.country].filter(Boolean).join(', ')
  return location || 'No location set'
}

function normalizeSearchText(value) {
  return String(value ?? '').trim().toLowerCase()
}

function buildListingSearchHaystack(listing) {
  return [
    listing?.title,
    listing?.business_name,
    listing?.business_type_name,
    formatLocation(listing?.address),
  ]
    .map((value) => normalizeSearchText(value))
    .filter(Boolean)
    .join(' ')
}

function formatFullAddress(address) {
  if (!address || typeof address !== 'object') return 'No address provided.'
  const parts = [
    address.street,
    address.city,
    address.state,
    address.postal_code,
    address.country,
  ].filter(Boolean)
  return parts.join(', ') || 'No address provided.'
}

function formatCoordinates(location) {
  const lat = Number(location?.lat)
  const lng = Number(location?.lng)
  if (!Number.isFinite(lat) || !Number.isFinite(lng)) return 'No coordinates provided.'
  return `${lat.toFixed(6)}, ${lng.toFixed(6)}`
}

function formatReviewSummary(listing) {
  if (!listing) return 'No reviews'
  if (listing.avg_rating == null && !listing.review_count) return 'No reviews'
  if (listing.avg_rating == null) return `${listing.review_count ?? 0} reviews`
  return `${Number(listing.avg_rating).toFixed(1)} rating - ${listing.review_count ?? 0} reviews`
}

function replaceListingInState(nextListing) {
  const normalized = normalizeListingStatus(nextListing)
  const index = listings.value.findIndex((item) => item.id === normalized.id)
  if (index !== -1) {
    listings.value[index] = normalized
  }
  if (detailListing.value?.id === normalized.id) {
    detailListing.value = {
      ...detailListing.value,
      ...normalized,
    }
  }
}

async function loadAdminData() {
  loading.value = true
  loadError.value = ''

  try {
    const response = await listingsAPI.getAll({ limit: 100 })
    const nextListings = Array.isArray(response.data) ? response.data : []
    listings.value = nextListings
      .map(normalizeListingStatus)
      .filter((listing) => isModerationVisibleStatus(listing.status))
  } catch (error) {
    loadError.value = 'Failed to load admin listing data.'
    toastStore.show('Failed to load admin listing data.', 'error')
  } finally {
    loading.value = false
  }
}

function openConfirmModal(action, listing) {
  if (decisionSubmitting.value) return
  confirmAction.value = action
  confirmTarget.value = listing
  showConfirmModal.value = true
}

async function confirmDecision() {
  if (!confirmTarget.value || decisionSubmitting.value) return
  decisionSubmitting.value = true

  try {
    const nextStatus = confirmConfig.value.nextStatus
    const response = await listingsAPI.moderate(confirmTarget.value.id, {
      status: nextStatus,
    })

    replaceListingInState(response.data)
    toastStore.show(confirmConfig.value.successMessage, 'success')

    showConfirmModal.value = false
    confirmTarget.value = null
  } catch (error) {
    toastStore.show(
      error.response?.data?.detail || 'Failed to update listing status.',
      'error',
    )
  } finally {
    decisionSubmitting.value = false
  }
}

async function openDetailModal(listingId) {
  showDetailModal.value = true
  detailLoading.value = true
  detailImageIndex.value = 0
  detailListingError.value = ''
  detailServicesError.value = ''
  detailServices.value = []

  const existingListing = listings.value.find((item) => item.id === listingId)
  detailListing.value = existingListing ? { ...existingListing } : null

  const [listingResult, servicesResult] = await Promise.allSettled([
    listingsAPI.getById(listingId),
    servicesAPI.getAll({ listing_id: listingId }),
  ])

  if (listingResult.status === 'fulfilled') {
    detailListing.value = normalizeListingStatus(listingResult.value.data)
    replaceListingInState(listingResult.value.data)
  } else {
    detailListingError.value =
      listingResult.reason?.response?.data?.detail || 'Failed to load listing details.'
  }

  if (servicesResult.status === 'fulfilled') {
    detailServices.value = Array.isArray(servicesResult.value.data) ? servicesResult.value.data : []
  } else {
    detailServicesError.value =
      servicesResult.reason?.response?.data?.detail || 'Failed to load listing services.'
  }

  detailLoading.value = false
}

function closeDetailModal() {
  showDetailModal.value = false
  detailImageIndex.value = 0
}

onMounted(() => {
  loadAdminData()
})
</script>
