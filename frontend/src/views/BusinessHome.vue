<template>
  <div class="bg-slate-50 min-h-screen">
    <div
      v-if="businessStore.loading"
      class="flex min-h-screen items-center justify-center"
    >
      <svg
        class="h-8 w-8 animate-spin text-cyan-500"
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
    </div>

    <div
      v-else-if="businessStore.listings.length === 0"
      class="flex min-h-screen flex-col items-center justify-center px-4 text-center"
    >
      <div
        class="flex h-16 w-16 items-center justify-center rounded-3xl bg-slate-100"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-8 w-8 text-slate-400"
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
      </div>
      <h2 class="mt-6 text-2xl font-bold text-slate-900">No listings yet</h2>
      <p class="mt-2 max-w-sm text-sm text-slate-500">
        Add your first listing to start managing your property on Isle Be There.
      </p>
      <button
        @click="openCreateModal"
        class="mt-8 inline-flex items-center gap-2 rounded-2xl bg-cyan-400 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:-translate-y-0.5 hover:bg-cyan-300"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-4 w-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2.5"
            d="M12 4v16m8-8H4"
          />
        </svg>
        Add your first listing
      </button>
    </div>

    <template v-else>
      <div class="bg-white border-b border-slate-200">
        <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <p
            class="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-600"
          >
            {{ businessStore.business?.business_name || "Your Business" }}
          </p>
          <div
            class="mt-2 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
          >
            <div class="flex flex-wrap items-center gap-3">
              <span
                class="rounded-xl px-3 py-1 text-xs font-semibold"
                :class="statusBadgeClass(businessStore.activeListing?.status)"
              >
                {{ statusLabel(businessStore.activeListing?.status) }}
              </span>
              <h1 class="text-2xl font-bold text-slate-900 sm:text-3xl">
                {{ businessStore.activeListing?.title }}
              </h1>
            </div>
            <div class="flex shrink-0 gap-2">
              <button
                v-if="businessStore.activeListing?.status !== 'inactive'"
                @click="openEditModal(businessStore.activeListing)"
                class="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50"
              >
                Edit Listing
              </button>
              <button
                v-if="businessStore.activeListing?.status !== 'inactive'"
                @click="openArchiveModal(businessStore.activeListing)"
                class="inline-flex items-center gap-2 rounded-2xl border border-red-100 px-5 py-2.5 text-sm font-semibold text-red-500 transition hover:bg-red-50"
              >
                Archive
              </button>
              <button
                v-if="businessStore.activeListing?.status === 'inactive'"
                @click="unarchiveListing(businessStore.activeListing)"
                class="inline-flex items-center gap-2 rounded-2xl border border-emerald-100 px-5 py-2.5 text-sm font-semibold text-emerald-600 transition hover:bg-emerald-50"
              >
                Restore Listing
              </button>
            </div>
          </div>
          <p
            v-if="businessStore.activeListing?.address"
            class="mt-2 flex items-center gap-1.5 text-sm text-slate-500"
          >
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
                d="M17.657 16.657L13.414 20.9a2 2 0 01-2.828 0l-4.243-4.243a8 8 0 1111.314 0z"
              />
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
              />
            </svg>
            {{
              [
                businessStore.activeListing?.address?.city,
                businessStore.activeListing?.address?.country,
              ]
                .filter(Boolean)
                .join(", ")
            }}
          </p>
        </div>
      </div>

      <div class="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8 space-y-8">
        <div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <div
            class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <p class="text-sm font-medium text-slate-500">Total Services</p>
            <p class="mt-2 text-3xl font-bold text-slate-900">
              {{ services.length }}
            </p>
          </div>
          <div
            class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <p class="text-sm font-medium text-slate-500">Active Services</p>
            <p class="mt-2 text-3xl font-bold text-cyan-600">
              {{ services.filter((s) => s.status === "active").length }}
            </p>
          </div>
          <div
            class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <p class="text-sm font-medium text-slate-500">Reviews</p>
            <p class="mt-2 text-3xl font-bold text-slate-900">
              {{ businessStore.activeListing?.review_count ?? 0 }}
            </p>
          </div>
          <div
            class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <p class="text-sm font-medium text-slate-500">Avg Rating</p>
            <p class="mt-2 text-3xl font-bold text-amber-500">
              {{
                businessStore.activeListing?.avg_rating
                  ? businessStore.activeListing.avg_rating.toFixed(1)
                  : "—"
              }}
            </p>
          </div>
        </div>

        <ListingServicesSection
          :listing="businessStore.activeListing"
          @services-changed="handleServicesChanged"
        />

        <div>
          <div class="mb-6 flex items-center justify-between">
            <div>
              <p
                class="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-600"
              >
                Listing
              </p>
              <h2 class="mt-1 text-xl font-bold text-slate-900">Team</h2>
            </div>
            <router-link
              to="/business/employees"
              class="inline-flex items-center gap-2 rounded-2xl border border-slate-200 px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
            >
              Manage Employees
            </router-link>
          </div>

          <div
            v-if="listingEmployees.length === 0"
            class="rounded-3xl border-2 border-dashed border-slate-200 bg-white px-6 py-20 text-center"
          >
            <div
              class="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-7 w-7 text-slate-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.5"
                  d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
            </div>
            <p class="mt-4 text-base font-semibold text-slate-700">
              No employees assigned
            </p>
            <p class="mt-1.5 text-sm text-slate-400">
              Assign employees to this listing from the Employees page.
            </p>
          </div>

          <div
            v-else
            class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
          >
            <div
              v-for="emp in listingEmployees"
              :key="emp.id"
              class="flex items-center gap-4 rounded-3xl border border-slate-200 bg-white p-5 shadow-sm"
            >
              <div
                class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-cyan-500 text-base font-bold text-white"
              >
                {{
                  (emp.first_name || emp.email || "?").charAt(0).toUpperCase()
                }}
              </div>
              <div class="min-w-0 flex-1">
                <p class="truncate text-sm font-semibold text-slate-900">
                  {{ emp.first_name }} {{ emp.last_name }}
                </p>
                <p class="truncate text-xs text-slate-500">{{ emp.email }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
    <div
      v-if="showFormModal"
      class="fixed inset-0 z-50 flex items-center justify-center px-4"
      @click.self="closeFormModal"
    >
      <div class="absolute inset-0 bg-slate-950/50 backdrop-blur-sm"></div>
      <div
        class="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-3xl border border-slate-200 bg-white shadow-2xl no-scrollbar"
      >
        <div
          class="sticky top-0 z-10 flex items-center justify-between border-b border-slate-100 bg-white px-8 py-6"
        >
          <div>
            <p
              class="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-600"
            >
              {{ isEditing ? "Edit Listing" : "New Listing" }}
            </p>
            <h2 class="mt-1 text-xl font-bold text-slate-900">
              {{
                isEditing
                  ? "Update your listing details"
                  : "Create a new listing"
              }}
            </h2>
          </div>
          <button
            @click="closeFormModal"
            class="flex h-9 w-9 items-center justify-center rounded-2xl border border-slate-200 text-slate-500 transition hover:bg-slate-50"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <form @submit.prevent="submitForm" class="px-8 py-6 space-y-5">
          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5"
              >Listing Title <span class="text-red-500">*</span></label
            >
            <input
              v-model="form.title"
              type="text"
              placeholder="e.g. Sunset Bay Resort"
              class="w-full rounded-2xl border px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition"
              :class="
                formErrors.title
                  ? 'border-red-300 bg-red-50 focus:border-red-400'
                  : 'border-slate-200 bg-white focus:border-cyan-400'
              "
            />
            <p v-if="formErrors.title" class="mt-1.5 text-xs text-red-500">
              {{ formErrors.title }}
            </p>
          </div>

          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5"
              >Business Type <span class="text-red-500">*</span></label
            >
            <div v-if="!isEditing">
              <div
                v-if="businessTypes.length"
                class="grid grid-cols-2 gap-3 sm:grid-cols-4"
              >
                <button
                  v-for="type in businessTypes"
                  :key="type.id"
                  type="button"
                  @click="form.business_type = type.id"
                  class="flex flex-col items-center gap-2 rounded-2xl border py-3.5 text-xs font-semibold transition"
                  :class="
                    form.business_type === type.id
                      ? 'border-cyan-400 bg-cyan-50 text-cyan-700'
                      : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'
                  "
                >
                  {{ type.name }}
                </button>
              </div>
              <p v-else class="text-sm text-slate-400">Loading types...</p>
              <p
                v-if="formErrors.business_type"
                class="mt-1.5 text-xs text-red-500"
              >
                {{ formErrors.business_type }}
              </p>
            </div>
            <div v-else class="flex items-center gap-2">
              <span
                class="rounded-2xl border border-cyan-400 bg-cyan-50 px-4 py-2 text-xs font-semibold text-cyan-700"
              >
                {{ selectedTypeName ?? "Unknown type" }}
              </span>
              <span class="text-xs text-slate-400"
                >Type cannot be changed after creation.</span
              >
            </div>
          </div>

          <component
            v-if="detailFormComponent"
            :is="detailFormComponent"
            v-model="form.details"
          />

          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5"
              >Description <span class="text-red-500">*</span></label
            >
            <textarea
              v-model="form.description"
              rows="3"
              placeholder="Describe what makes this listing special..."
              class="w-full rounded-2xl border px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition resize-none"
              :class="
                formErrors.description
                  ? 'border-red-300 bg-red-50 focus:border-red-400'
                  : 'border-slate-200 bg-white focus:border-cyan-400'
              "
            ></textarea>
            <p
              v-if="formErrors.description"
              class="mt-1.5 text-xs text-red-500"
            >
              {{ formErrors.description }}
            </p>
          </div>

          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5"
              >Base Price (USD) <span class="text-red-500">*</span></label
            >
            <div class="relative">
              <span
                class="absolute left-4 top-1/2 -translate-y-1/2 text-sm font-semibold text-slate-400"
                >$</span
              >
              <input
                v-model="form.base_price"
                type="number"
                min="0"
                step="0.01"
                placeholder="0.00"
                class="w-full rounded-2xl border pl-8 pr-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition"
                :class="
                  formErrors.base_price
                    ? 'border-red-300 bg-red-50 focus:border-red-400'
                    : 'border-slate-200 bg-white focus:border-cyan-400'
                "
              />
            </div>
            <p v-if="formErrors.base_price" class="mt-1.5 text-xs text-red-500">
              {{ formErrors.base_price }}
            </p>
          </div>

          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">
              Street Address
              <span
                v-if="isEditing"
                class="ml-1.5 text-xs font-normal text-slate-400"
                >(locked after creation)</span
              >
            </label>
            <input
              v-model="form.street"
              type="text"
              placeholder="e.g. 12 Bay Street"
              :disabled="isEditing"
              class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
            />
          </div>

          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1.5"
                >City <span class="text-red-500">*</span></label
              >
              <input
                v-model="form.city"
                type="text"
                placeholder="e.g. Bridgetown"
                :disabled="isEditing"
                class="w-full rounded-2xl border px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition disabled:cursor-not-allowed disabled:opacity-50"
                :class="
                  formErrors.city
                    ? 'border-red-300 bg-red-50 focus:border-red-400'
                    : 'border-slate-200 bg-white focus:border-cyan-400'
                "
              />
              <p v-if="formErrors.city" class="mt-1.5 text-xs text-red-500">
                {{ formErrors.city }}
              </p>
            </div>
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1.5">
                {{ subdivisionLabel }}
              </label>
              <div class="relative">
                <select
                  v-model="form.state"
                  :disabled="isEditing || !showParishDropdown"
                  class="w-full appearance-none rounded-2xl border border-slate-200 bg-white px-4 py-3 pr-11 text-sm text-slate-900 outline-none transition focus:border-cyan-400 disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-400"
                >
                  <option value="">
                    {{
                      showParishDropdown
                        ? `Select ${subdivisionLabel.toLowerCase()}`
                        : "Choose a country first"
                    }}
                  </option>
                  <option
                    v-for="parish in availableParishes"
                    :key="parish"
                    :value="parish"
                  >
                    {{ parish }}
                  </option>
                </select>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="pointer-events-none absolute right-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1.5"
                >Postal Code</label
              >
              <input
                v-model="form.postal_code"
                type="text"
                placeholder="e.g. BB11000"
                :disabled="isEditing"
                class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
              />
            </div>
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1.5"
                >Country / Island <span class="text-red-500">*</span></label
              >
              <div class="relative">
                <select
                  v-model="form.country"
                  :disabled="isEditing"
                  class="w-full appearance-none rounded-2xl border px-4 py-3 pr-11 text-sm text-slate-900 outline-none transition disabled:cursor-not-allowed disabled:opacity-50"
                  :class="
                    formErrors.country
                      ? 'border-red-300 bg-red-50 focus:border-red-400'
                      : 'border-slate-200 bg-white focus:border-cyan-400'
                  "
                >
                  <option value="">Select country or island</option>
                  <option
                    v-for="country in CARIBBEAN_COUNTRIES"
                    :key="country"
                    :value="country"
                  >
                    {{ country }}
                  </option>
                </select>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="pointer-events-none absolute right-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </div>
              <p v-if="formErrors.country" class="mt-1.5 text-xs text-red-500">
                {{ formErrors.country }}
              </p>
            </div>
          </div>

          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1.5"
                >Phone Number</label
              >
              <input
                v-model="form.phone_number"
                type="tel"
                placeholder="e.g. +1 246 555 0100"
                class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400"
              />
            </div>
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1.5"
                >Email Address</label
              >
              <input
                v-model="form.email_address"
                type="email"
                placeholder="e.g. contact@resort.com"
                class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400"
              />
            </div>
          </div>

          <div class="rounded-3xl border border-slate-200 bg-slate-50 p-5">
            <div
              class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between"
            >
              <div>
                <p class="text-sm font-semibold text-slate-900">Map Location</p>
                <p class="mt-1 text-xs text-slate-500">
                  Search from the address, click the map, or drag the marker to
                  fine-tune the listing location.
                </p>
              </div>
              <button
                type="button"
                :disabled="geocodingLocation"
                @click="geocodeAddress"
                class="inline-flex items-center justify-center rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {{ geocodingLocation ? "Finding..." : "Use Address on Map" }}
              </button>
            </div>

            <div class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label
                  class="mb-1.5 block text-sm font-semibold text-slate-700"
                >
                  Latitude
                </label>
                <input
                  v-model="form.latitude"
                  type="number"
                  step="any"
                  placeholder="e.g. 13.0975"
                  class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400"
                  @change="syncMapToManualCoordinates"
                />
              </div>
              <div>
                <label
                  class="mb-1.5 block text-sm font-semibold text-slate-700"
                >
                  Longitude
                </label>
                <input
                  v-model="form.longitude"
                  type="number"
                  step="any"
                  placeholder="e.g. -59.6167"
                  class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400"
                  @change="syncMapToManualCoordinates"
                />
              </div>
            </div>

            <div
              ref="mapContainerRef"
              class="mt-4 h-72 overflow-hidden rounded-2xl border border-slate-200 bg-slate-200"
            ></div>
          </div>

          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5"
              >Images</label
            >
            <div
              class="relative flex flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-10 text-center transition cursor-pointer"
              :class="
                isDragging
                  ? 'border-cyan-400 bg-cyan-50'
                  : 'border-slate-200 bg-slate-50 hover:border-slate-300 hover:bg-white'
              "
              @dragover.prevent="isDragging = true"
              @dragleave.prevent="isDragging = false"
              @drop.prevent="onDrop"
              @click="fileInputRef.click()"
            >
              <input
                ref="fileInputRef"
                type="file"
                accept="image/*"
                multiple
                class="hidden"
                @change="onFileChange"
              />
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-10 w-10 text-slate-300 mb-3"
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
              <p class="text-sm font-semibold text-slate-600">
                Drag & drop images here
              </p>
              <p class="mt-1 text-xs text-slate-400">
                or click to browse files
              </p>
              <p
                v-if="uploadingCount > 0"
                class="mt-2 text-xs font-semibold text-cyan-600"
              >
                Uploading {{ uploadingCount }} file{{
                  uploadingCount > 1 ? "s" : ""
                }}...
              </p>
            </div>
            <p
              v-if="pendingImages.length > 0"
              class="mt-2 text-xs font-semibold text-cyan-600"
            >
              {{ pendingImages.length }} new image{{
                pendingImages.length > 1 ? "s" : ""
              }}
              ready to upload when you save.
            </p>
            <div
              v-if="displayImages.length"
              class="mt-3 grid grid-cols-3 gap-3 sm:grid-cols-4"
            >
              <div
                v-for="image in displayImages"
                :key="image.key"
                class="relative group aspect-square overflow-hidden rounded-2xl border border-slate-200 bg-slate-100"
              >
                <img
                  :src="image.url"
                  class="h-full w-full cursor-zoom-in object-cover"
                  @click="openImagePreview(image.key)"
                />
                <div
                  v-if="image.isPending"
                  class="absolute left-1.5 top-1.5 rounded-full bg-cyan-500/90 px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.18em] text-white"
                >
                  New
                </div>
                <button
                  type="button"
                  @click.stop="showRemoveConfirmation(image)"
                  class="absolute top-1.5 right-1.5 flex h-6 w-6 items-center justify-center rounded-full bg-slate-900/70 text-white opacity-0 transition group-hover:opacity-100"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-3 w-3"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2.5"
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <div
            class="rounded-2xl border border-amber-100 bg-amber-50 px-5 py-4"
          >
            <div class="flex items-start gap-3">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-5 w-5 shrink-0 text-amber-500 mt-0.5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <p class="text-sm text-amber-700">
                <span class="font-semibold">Requires approval.</span>
                {{
                  isEditing
                    ? "Edits will be reviewed before the listing updates publicly."
                    : "New listings are marked as Pending Approval until reviewed by a moderator."
                }}
              </p>
            </div>
          </div>

          <p v-if="formErrors.submit" class="text-sm text-red-500 text-center">
            {{ formErrors.submit }}
          </p>

          <div class="flex gap-3 pt-2">
            <button
              type="button"
              @click="closeFormModal"
              class="flex-1 rounded-2xl border border-slate-200 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="formSubmitting"
              class="flex-1 rounded-2xl bg-slate-900 py-3 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-slate-800 disabled:opacity-50"
            >
              {{
                formSubmitting
                  ? "Saving..."
                  : isEditing
                    ? "Save Changes"
                    : "Create Listing"
              }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div
      v-if="showImagePreviewModal && activePreviewImage"
      class="fixed inset-0 z-[60] flex items-center justify-center px-4"
      @click.self="closeImagePreview"
    >
      <div class="absolute inset-0 bg-slate-950/85 backdrop-blur-sm"></div>
      <div class="relative flex w-full max-w-5xl items-center justify-center">
        <button
          type="button"
          @click="closeImagePreview"
          class="absolute right-0 top-0 z-10 flex h-10 w-10 items-center justify-center rounded-full bg-slate-900/70 text-white transition hover:bg-slate-800"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>

        <button
          v-if="displayImages.length > 1"
          type="button"
          @click.stop="showPreviousImage"
          class="absolute left-0 z-10 flex h-11 w-11 items-center justify-center rounded-full bg-slate-900/70 text-white transition hover:bg-slate-800"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 19l-7-7 7-7"
            />
          </svg>
        </button>

        <img
          :src="activePreviewImage.url"
          class="max-h-[85vh] max-w-full rounded-3xl object-contain shadow-2xl"
        />

        <button
          v-if="displayImages.length > 1"
          type="button"
          @click.stop="showNextImage"
          class="absolute right-0 z-10 flex h-11 w-11 items-center justify-center rounded-full bg-slate-900/70 text-white transition hover:bg-slate-800"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 5l7 7-7 7"
            />
          </svg>
        </button>
      </div>
    </div>

    <div
      v-if="showRemoveImageConfirmation && imagePendingRemoval"
      class="fixed inset-0 z-[70] flex items-center justify-center px-4"
      @click.self="cancelRemoveImage"
    >
      <div class="absolute inset-0 bg-slate-950/60 backdrop-blur-sm"></div>
      <div
        class="relative w-full max-w-lg overflow-hidden rounded-3xl border border-slate-200 bg-white text-left shadow-2xl"
      >
        <div class="px-6 py-6 sm:px-7">
          <div class="sm:flex sm:items-start">
            <div
              class="mx-auto flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-red-500/10 sm:mx-0 sm:h-10 sm:w-10"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-6 w-6 text-red-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.5"
                  d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z"
                />
              </svg>
            </div>
            <div class="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left">
              <h3 class="text-base font-semibold text-slate-900">
                Remove image?
              </h3>
              <div class="mt-2 space-y-2">
                <p class="text-sm text-slate-600">
                  This image will be removed from the listing now.
                </p>
                <p class="text-sm text-slate-500">
                  If you save this edit, the image will be permanently deleted
                  from storage. If you cancel the edit instead, the image will
                  stay.
                </p>
              </div>
            </div>
          </div>
        </div>
        <div
          class="border-t border-slate-100 bg-slate-50 px-6 py-4 sm:flex sm:flex-row-reverse sm:px-7"
        >
          <button
            type="button"
            @click="confirmRemoveImage"
            class="inline-flex w-full justify-center rounded-2xl bg-red-500 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-red-400 sm:ml-3 sm:w-auto"
          >
            Remove Image
          </button>
          <button
            type="button"
            @click="cancelRemoveImage"
            class="mt-3 inline-flex w-full justify-center rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 sm:mt-0 sm:w-auto"
          >
            Keep Image
          </button>
        </div>
      </div>
    </div>

    <!-- Archive Modal -->
    <div
      v-if="showArchiveModal"
      class="fixed inset-0 z-50 flex items-center justify-center px-4"
      @click.self="showArchiveModal = false"
    >
      <div class="absolute inset-0 bg-slate-950/50 backdrop-blur-sm"></div>
      <div
        class="relative w-full max-w-md rounded-3xl border border-slate-200 bg-white p-8 shadow-2xl"
      >
        <div class="flex items-start gap-4">
          <div
            class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-red-50"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6 text-red-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8l1 12a2 2 0 002 2h8a2 2 0 002-2L19 8M10 12v4M14 12v4"
              />
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-bold text-slate-900">Archive Listing?</h3>
            <p class="mt-2 text-sm leading-6 text-slate-600">
              <span class="font-semibold text-slate-800">{{
                listingToArchive?.title
              }}</span>
              will be hidden from visitors. You can restore it at any time.
            </p>
          </div>
        </div>
        <div class="mt-6 flex gap-3">
          <button
            @click="showArchiveModal = false"
            class="flex-1 rounded-2xl border border-slate-200 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
          >
            Cancel
          </button>
          <button
            @click="confirmArchive"
            :disabled="archiveSubmitting"
            class="flex-1 rounded-2xl bg-red-500 py-3 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-red-400 disabled:opacity-50"
          >
            {{ archiveSubmitting ? "Archiving..." : "Archive" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  ref,
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  watch,
} from "vue";
import {
  businessesAPI,
  listingsAPI,
  uploadsAPI,
  employeesAPI,
} from "../services/api";
import { useToastStore } from "../stores/toast";
import { useBusinessStore } from "../stores/business";
import {
  CARIBBEAN_COUNTRIES,
  COUNTRY_DETAILS,
} from "../stores/caribbeanLocations";
import HotelDetailForm from "../components/listings/detail-forms/HotelDetailForm.vue";
import RestaurantDetailForm from "../components/listings/detail-forms/RestaurantDetailForm.vue";
import TourDetailForm from "../components/listings/detail-forms/TourDetailForm.vue";
import ActivityDetailForm from "../components/listings/detail-forms/ActivityDetailForm.vue";
import ListingServicesSection from "../components/services/ListingServicesSection.vue";

const toastStore = useToastStore();
const businessStore = useBusinessStore();
const businessTypes = ref([]);

onMounted(() => {
  fetchBusinessTypes();
});

watch(
  () => businessStore.showCreateModal,
  (val) => {
    if (val) {
      openCreateModal();
      businessStore.showCreateModal = false;
    }
  },
);

async function fetchBusinessTypes() {
  try {
    const response = await businessesAPI.getTypes();
    businessTypes.value = response.data;
  } catch (error) {
    console.error("Error fetching business types:", error);
  }
}

function statusLabel(status) {
  if (status === "active") return "Active";
  if (status === "pending") return "Pending Approval";
  if (status === "inactive") return "Archived";
  return status ?? "";
}

function statusBadgeClass(status) {
  if (status === "active") return "bg-emerald-500 text-white";
  if (status === "pending") return "bg-amber-400 text-slate-900";
  if (status === "inactive") return "bg-slate-500 text-white";
  return "bg-slate-300 text-slate-900";
}

const showFormModal = ref(false);
const showRemoveImageConfirmation = ref(false);
const isEditing = ref(false);
const editingId = ref(null);
const formSubmitting = ref(false);
const geocodingLocation = ref(false);

const blankForm = () => ({
  title: "",
  business_type: "",
  description: "",
  base_price: "",
  street: "",
  city: "",
  state: "",
  postal_code: "",
  country: "",
  phone_number: "",
  email_address: "",
  latitude: "",
  longitude: "",
  image_urls: [],
  details: {},
});

const form = ref(blankForm());
const formErrors = ref({});
const pendingImages = ref([]);
const imagePendingRemoval = ref(null);
const originalImageUrls = ref([]);
const originalListingPayload = ref(null);
const showImagePreviewModal = ref(false);
const previewImageIndex = ref(0);
const mapContainerRef = ref(null);
let pendingImageId = 0;
let leafletLoadPromise = null;
let leafletApi = null;
let listingMap = null;
let listingMarker = null;
const DEFAULT_MAP_CENTER = { lat: 13.1939, lng: -59.5432 };

const selectedTypeName = computed(
  () =>
    businessTypes.value.find((t) => t.id === form.value.business_type)?.name,
);
const displayImages = computed(() => [
  ...form.value.image_urls
    .filter((url) => url)
    .map((url, index) => ({
      key: `existing-${index}-${url}`,
      url,
      index,
      isPending: false,
    })),
  ...pendingImages.value.map((image) => ({
    key: `pending-${image.id}`,
    url: image.previewUrl,
    id: image.id,
    isPending: true,
  })),
]);
const activePreviewImage = computed(
  () => displayImages.value[previewImageIndex.value] ?? null,
);
const canGeocodeAddress = computed(() =>
  [form.value.street, form.value.city, form.value.country].some((value) =>
    String(value ?? "").trim(),
  ),
);

const availableParishes = computed(() => {
  const details = COUNTRY_DETAILS[form.value.country?.trim()];
  return details?.parishes ?? [];
});

const subdivisionLabel = computed(() => {
  const details = COUNTRY_DETAILS[form.value.country?.trim()];
  return details?.divisionLabel ?? "State / Parish";
});

const showParishDropdown = computed(() => availableParishes.value.length > 0);

// Watch country changes and autofill/clear dependent fields
watch(
  () => form.value.country,
  (newCountry, oldCountry) => {
    const trimmedNewCountry = String(newCountry ?? "").trim();
    const trimmedOldCountry = String(oldCountry ?? "").trim();

    if (trimmedNewCountry !== trimmedOldCountry && trimmedOldCountry) {
      form.value.state = "";
    }

    const newCountryDetails = COUNTRY_DETAILS[trimmedNewCountry];
    const oldCountryDetails = COUNTRY_DETAILS[trimmedOldCountry];
    const currentPostalCode = String(form.value.postal_code ?? "").trim();
    const shouldRefreshPostalCode =
      !currentPostalCode ||
      (oldCountryDetails?.postalPrefix &&
        currentPostalCode === oldCountryDetails.postalPrefix);

    if (trimmedNewCountry !== trimmedOldCountry && shouldRefreshPostalCode) {
      form.value.postal_code = newCountryDetails?.postalPrefix ?? "";
    }
  },
);

const detailFormComponent = computed(() => {
  switch (selectedTypeName.value) {
    case "Hotel":
      return HotelDetailForm;
    case "Restaurant":
      return RestaurantDetailForm;
    case "Tour Operator":
      return TourDetailForm;
    case "Activity Provider":
      return ActivityDetailForm;
    default:
      return null;
  }
});

watch(
  () => form.value.business_type,
  () => {
    if (!isEditing.value) form.value.details = {};
  },
);

function openCreateModal() {
  isEditing.value = false;
  editingId.value = null;
  clearPendingImages();
  closeImagePreview();
  destroyListingMap();
  originalImageUrls.value = [];
  originalListingPayload.value = null;
  form.value = blankForm();
  formErrors.value = {};
  showFormModal.value = true;
}

function openEditModal(item) {
  isEditing.value = true;
  editingId.value = item.id;
  clearPendingImages();
  closeImagePreview();
  destroyListingMap();
  originalImageUrls.value = item.image_urls?.length ? [...item.image_urls] : [];
  originalListingPayload.value = {
    title: item.title ?? "",
    business_type: item.business_type ?? "",
    description: item.description ?? "",
    base_price: Number(item.base_price ?? 0),
    address: {
      street: item.address?.street ?? null,
      city: item.address?.city ?? "",
      state: item.address?.state ?? null,
      postal_code: item.address?.postal_code ?? null,
      country: item.address?.country ?? "",
    },
    phone_number: item.phone_number ?? null,
    email_address: item.email_address ?? null,
    location: item.location
      ? {
          lat: item.location.lat,
          lng: item.location.lng,
        }
      : null,
    image_urls: item.image_urls?.length ? [...item.image_urls] : [],
    details: item.details ? { ...item.details } : null,
  };
  form.value = {
    title: item.title ?? "",
    business_type: item.business_type ?? "",
    description: item.description ?? "",
    base_price: item.base_price ?? "",
    street: item.address?.street ?? "",
    city: item.address?.city ?? "",
    state: item.address?.state ?? "",
    postal_code: item.address?.postal_code ?? "",
    country: item.address?.country ?? "",
    phone_number: item.phone_number ?? "",
    email_address: item.email_address ?? "",
    latitude: item.location?.lat ?? "",
    longitude: item.location?.lng ?? "",
    image_urls: item.image_urls?.length ? [...item.image_urls] : [],
    details: item.details ? { ...item.details } : {},
  };
  formErrors.value = {};
  showFormModal.value = true;
}

function closeFormModal() {
  clearPendingImages();
  closeImagePreview();
  cancelRemoveImage();
  destroyListingMap();
  originalImageUrls.value = [];
  originalListingPayload.value = null;
  showFormModal.value = false;
}

const fileInputRef = ref(null);
const isDragging = ref(false);
const uploadingCount = ref(0);

function clearPendingImages() {
  for (const image of pendingImages.value) {
    URL.revokeObjectURL(image.previewUrl);
  }
  pendingImages.value = [];
}

function stageFiles(files) {
  for (const file of files) {
    if (!file.type.startsWith("image/")) continue;
    pendingImageId += 1;
    pendingImages.value.push({
      id: pendingImageId,
      file,
      previewUrl: URL.createObjectURL(file),
    });
  }
}

async function uploadPendingImages() {
  const uploadedUrls = [];

  try {
    for (const image of pendingImages.value) {
      uploadingCount.value++;
      try {
        const formData = new FormData();
        formData.append("file", image.file);
        const res = await uploadsAPI.uploadImage(formData, {
          folder: "listings",
        });
        uploadedUrls.push(res.data.url);
      } finally {
        uploadingCount.value--;
      }
    }
  } catch (error) {
    error.uploadedUrls = uploadedUrls;
    throw error;
  }

  return uploadedUrls;
}

async function cleanupUploadedImages(urls) {
  if (!urls.length) return;

  try {
    await uploadsAPI.deleteImages(urls);
  } catch (error) {
    console.error("Failed to clean up uploaded images", error);
  }
}

function normalizeCoordinate(value) {
  const numericValue = Number.parseFloat(value);
  return Number.isFinite(numericValue) ? Number(numericValue.toFixed(6)) : null;
}

function getFormCoordinates() {
  const lat = normalizeCoordinate(form.value.latitude);
  const lng = normalizeCoordinate(form.value.longitude);
  if (lat === null || lng === null) return null;
  return { lat, lng };
}

function setFormCoordinates(lat, lng) {
  form.value.latitude = String(Number(lat).toFixed(6));
  form.value.longitude = String(Number(lng).toFixed(6));
}

function buildLocationPayload() {
  const coordinates = getFormCoordinates();
  if (!coordinates) return null;
  return coordinates;
}

function ensureLeafletCss() {
  if (document.getElementById("leaflet-css")) return;
  const stylesheet = document.createElement("link");
  stylesheet.id = "leaflet-css";
  stylesheet.rel = "stylesheet";
  stylesheet.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
  document.head.appendChild(stylesheet);
}

async function ensureLeaflet() {
  if (leafletApi) return leafletApi;
  if (window.L) {
    leafletApi = window.L;
    return leafletApi;
  }

  ensureLeafletCss();

  if (!leafletLoadPromise) {
    leafletLoadPromise = new Promise((resolve, reject) => {
      const existingScript = document.getElementById("leaflet-script");
      if (existingScript) {
        existingScript.addEventListener("load", () => resolve(window.L), {
          once: true,
        });
        existingScript.addEventListener("error", reject, { once: true });
        return;
      }

      const script = document.createElement("script");
      script.id = "leaflet-script";
      script.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
      script.async = true;
      script.onload = () => resolve(window.L);
      script.onerror = () => reject(new Error("Failed to load Leaflet"));
      document.body.appendChild(script);
    });
  }

  leafletApi = await leafletLoadPromise;
  return leafletApi;
}

function destroyListingMap() {
  if (listingMarker) {
    listingMarker.off("dragend");
    listingMarker = null;
  }
  if (listingMap) {
    listingMap.off();
    listingMap.remove();
    listingMap = null;
  }
}

function updateListingMarker({ centerMap = false } = {}) {
  if (!listingMap || !leafletApi) return;

  const coordinates = getFormCoordinates();
  const nextCenter = coordinates ?? DEFAULT_MAP_CENTER;

  if (coordinates) {
    if (!listingMarker) {
      listingMarker = leafletApi
        .marker([coordinates.lat, coordinates.lng], {
          draggable: true,
        })
        .addTo(listingMap);
      listingMarker.on("dragend", onMarkerDrag);
    } else {
      listingMarker.setLatLng([coordinates.lat, coordinates.lng]);
    }
  } else if (listingMarker) {
    listingMap.removeLayer(listingMarker);
    listingMarker.off("dragend", onMarkerDrag);
    listingMarker = null;
  }

  if (centerMap || !listingMap._loaded) {
    listingMap.setView([nextCenter.lat, nextCenter.lng], coordinates ? 14 : 9);
  }
}

async function initializeListingMap() {
  if (!showFormModal.value || !mapContainerRef.value) return;

  try {
    leafletApi = await ensureLeaflet();
  } catch (error) {
    toastStore.show("Failed to load the map.", "error");
    return;
  }

  if (!listingMap) {
    const coordinates = getFormCoordinates() ?? DEFAULT_MAP_CENTER;
    listingMap = leafletApi.map(mapContainerRef.value, {
      center: [coordinates.lat, coordinates.lng],
      zoom: getFormCoordinates() ? 14 : 9,
      zoomControl: true,
    });

    leafletApi
      .tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors",
      })
      .addTo(listingMap);

    listingMap.on("click", (event) => {
      setFormCoordinates(event.latlng.lat, event.latlng.lng);
      updateListingMarker({ centerMap: false });
    });
  }

  updateListingMarker({ centerMap: true });
  await nextTick();
  listingMap.invalidateSize();
}

async function geocodeAddress() {
  if (!canGeocodeAddress.value) {
    toastStore.show(
      "Add at least one address field before searching the map.",
      "error",
    );
    return;
  }

  const query = [form.value.street, form.value.city, form.value.country]
    .map((value) => String(value ?? "").trim())
    .filter(Boolean)
    .join(", ");

  geocodingLocation.value = true;
  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`,
      {
        headers: {
          "Accept-Language": "en",
        },
      },
    );

    if (!response.ok) {
      throw new Error("Geocoding failed");
    }

    const data = await response.json();
    if (!data[0]) {
      toastStore.show("No map result found for that address.", "error");
      return;
    }

    setFormCoordinates(data[0].lat, data[0].lon);
    await initializeListingMap();
    updateListingMarker({ centerMap: true });
  } catch (error) {
    toastStore.show("Failed to locate that address on the map.", "error");
  } finally {
    geocodingLocation.value = false;
  }
}

function onMarkerDrag(event) {
  const { lat, lng } = event.target.getLatLng();
  setFormCoordinates(lat, lng);
}

function syncMapToManualCoordinates() {
  if (!listingMap) return;
  const coordinates = getFormCoordinates();
  if (!coordinates) return;
  updateListingMarker({ centerMap: true });
}

async function deleteImagesOrThrow(urls) {
  if (!urls.length) return;
  await uploadsAPI.deleteImages(urls);
}

async function rollbackListingUpdate() {
  if (!editingId.value || !originalListingPayload.value) return;
  const rollbackResponse = await listingsAPI.update(
    editingId.value,
    originalListingPayload.value,
  );
  businessStore.updateListing(rollbackResponse.data);
}

function openImagePreview(imageKey) {
  const nextIndex = displayImages.value.findIndex(
    (image) => image.key === imageKey,
  );
  if (nextIndex === -1) return;
  previewImageIndex.value = nextIndex;
  showImagePreviewModal.value = true;
}

function closeImagePreview() {
  showImagePreviewModal.value = false;
  previewImageIndex.value = 0;
}

function showPreviousImage() {
  if (!displayImages.value.length) return;
  previewImageIndex.value =
    (previewImageIndex.value - 1 + displayImages.value.length) %
    displayImages.value.length;
}

function showNextImage() {
  if (!displayImages.value.length) return;
  previewImageIndex.value =
    (previewImageIndex.value + 1) % displayImages.value.length;
}

function onFileChange(e) {
  stageFiles(Array.from(e.target.files));
  e.target.value = "";
}

function onDrop(e) {
  isDragging.value = false;
  stageFiles(Array.from(e.dataTransfer.files));
}

function showRemoveConfirmation(image) {
  if (image.isPending) {
    removeImage(image);
  } else {
    imagePendingRemoval.value = image;
    showRemoveImageConfirmation.value = true;
  }
}

function cancelRemoveImage() {
  imagePendingRemoval.value = null;
  showRemoveImageConfirmation.value = false;
}

function confirmRemoveImage() {
  if (!imagePendingRemoval.value) return;
  removeImage(imagePendingRemoval.value);
  cancelRemoveImage();
}

function removeImage(image) {
  if (image.isPending) {
    const index = pendingImages.value.findIndex((item) => item.id === image.id);
    if (index === -1) return;
    const [removed] = pendingImages.value.splice(index, 1);
    URL.revokeObjectURL(removed.previewUrl);
    if (!displayImages.value.length) closeImagePreview();
    return;
  }

  form.value.image_urls.splice(image.index, 1);
  if (!displayImages.value.length) {
    closeImagePreview();
  } else if (previewImageIndex.value >= displayImages.value.length) {
    previewImageIndex.value = displayImages.value.length - 1;
  }
}

function validateForm() {
  const errors = {};
  if (!form.value.title.trim()) errors.title = "Listing title is required.";
  if (!form.value.business_type)
    errors.business_type = "Please select a business type.";
  if (!form.value.description.trim())
    errors.description = "Description is required.";
  if (!form.value.base_price || Number(form.value.base_price) <= 0)
    errors.base_price = "Please enter a valid price.";
  if (!form.value.city.trim()) errors.city = "City is required.";
  if (!form.value.country.trim())
    errors.country = "Country / Island is required.";
  formErrors.value = errors;
  return Object.keys(errors).length === 0;
}

async function submitForm() {
  if (!validateForm()) return;
  formSubmitting.value = true;
  let uploadedUrls = [];
  try {
    uploadedUrls = await uploadPendingImages();
    const payload = {
      title: form.value.title.trim(),
      business_type: form.value.business_type,
      description: form.value.description.trim(),
      base_price: Number(form.value.base_price),
      address: {
        street: form.value.street.trim() || null,
        city: form.value.city.trim(),
        state: form.value.state.trim() || null,
        postal_code: form.value.postal_code.trim() || null,
        country: form.value.country.trim(),
      },
      phone_number: form.value.phone_number.trim() || null,
      email_address: form.value.email_address.trim() || null,
      location: buildLocationPayload(),
      image_urls: [...form.value.image_urls, ...uploadedUrls],
      details: Object.keys(form.value.details).length
        ? form.value.details
        : null,
    };

    if (isEditing.value) {
      const removedOriginalUrls = originalImageUrls.value.filter(
        (url) => !payload.image_urls.includes(url),
      );
      const response = await listingsAPI.update(editingId.value, payload);
      try {
        await deleteImagesOrThrow(removedOriginalUrls);
      } catch (deleteError) {
        await rollbackListingUpdate();
        await cleanupUploadedImages(uploadedUrls);
        uploadedUrls = [];
        throw deleteError;
      }
      businessStore.updateListing(response.data);
      toastStore.show("Listing updated successfully.", "success");
    } else {
      const response = await listingsAPI.create(payload);
      businessStore.addListing(response.data);
      toastStore.show("Listing created successfully.", "success");
    }
    closeFormModal();
  } catch (e) {
    const urlsToCleanup = uploadedUrls.length
      ? uploadedUrls
      : (e.uploadedUrls ?? []);
    await cleanupUploadedImages(urlsToCleanup);
    formErrors.value.submit =
      e.response?.data?.detail || "Failed to save listing. Please try again.";
    toastStore.show("Failed to save listing.", "error");
  } finally {
    formSubmitting.value = false;
  }
}

// ── Services (local state until backend ready) ─────────────────────────────
const services = ref([]);

function handleServicesChanged(nextServices) {
  services.value = nextServices;
}

// ── Employees (read-only — managed from /business/employees) ──────────────
const listingEmployees = ref([]);

async function fetchListingEmployees(listingId) {
  if (!listingId) return;
  try {
    const res = await employeesAPI.getEmployeesForListing(listingId);
    listingEmployees.value = res.data ?? [];
  } catch (e) {
    listingEmployees.value = [];
  }
}

watch(
  () => businessStore.activeListingId,
  (id) => fetchListingEmployees(id),
  { immediate: true },
);

// ── Archive ────────────────────────────────────────────────────────────────
const showArchiveModal = ref(false);
const listingToArchive = ref(null);
const archiveSubmitting = ref(false);

function openArchiveModal(item) {
  listingToArchive.value = item;
  showArchiveModal.value = true;
}

async function confirmArchive() {
  if (!listingToArchive.value) return;
  archiveSubmitting.value = true;
  try {
    await listingsAPI.update(listingToArchive.value.id, { status: "inactive" });
    businessStore.updateListing({
      ...listingToArchive.value,
      status: "inactive",
    });
    const next = businessStore.listings.find(
      (l) => l.id !== listingToArchive.value.id && l.status !== "inactive",
    );
    if (next) businessStore.setActiveListing(next.id);
    showArchiveModal.value = false;
    listingToArchive.value = null;
    toastStore.show("Listing archived.", "success");
  } catch (e) {
    toastStore.show("Failed to archive listing.", "error");
  } finally {
    archiveSubmitting.value = false;
  }
}

async function unarchiveListing(item) {
  try {
    await listingsAPI.update(item.id, { status: "active" });
    businessStore.updateListing({ ...item, status: "active" });
    toastStore.show("Listing restored.", "success");
  } catch (e) {
    toastStore.show("Failed to restore listing.", "error");
  }
}

watch(showFormModal, async (isOpen) => {
  if (isOpen) {
    await nextTick();
    await initializeListingMap();
    return;
  }

  destroyListingMap();
});

watch([() => form.value.latitude, () => form.value.longitude], () => {
  if (!listingMap) return;
  updateListingMarker({ centerMap: false });
});

onBeforeUnmount(() => {
  destroyListingMap();
});
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

:deep(.leaflet-container) {
  z-index: 0;
  font: inherit;
}
</style>
