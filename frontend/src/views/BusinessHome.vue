<template>
  <div class="bg-slate-50 min-h-screen">

    <div class="bg-white border-b border-slate-200">
      <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div class="flex flex-col gap-6 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p class="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-600">
              Business Dashboard
            </p>
            <h1 class="mt-3 text-3xl font-bold text-slate-900 sm:text-4xl">
              Manage Your Listings
            </h1>
          </div>
          <button
            @click="openCreateModal"
            class="inline-flex items-center gap-2 rounded-2xl bg-cyan-400 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:-translate-y-0.5 hover:bg-cyan-300 shrink-0"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
            </svg>
            Add Listing
          </button>
        </div>
      </div>
    </div>

    <div class="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8 space-y-8">

      <div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <p class="text-sm font-medium text-slate-500">Total Listings</p>
          <p class="mt-2 text-3xl font-bold text-slate-900">{{ stats.total }}</p>
        </div>
        <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <p class="text-sm font-medium text-slate-500">Active</p>
          <p class="mt-2 text-3xl font-bold text-cyan-600">{{ stats.active }}</p>
        </div>
        <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <p class="text-sm font-medium text-slate-500">Pending Approval</p>
          <p class="mt-2 text-3xl font-bold text-amber-500">{{ stats.pending }}</p>
        </div>
        <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <p class="text-sm font-medium text-slate-500">Archived</p>
          <p class="mt-2 text-3xl font-bold text-slate-400">{{ stats.archived }}</p>
        </div>
      </div>

      <div class="flex flex-wrap gap-2">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          @click="activeTab = tab.value"
          class="rounded-2xl px-5 py-2.5 text-sm font-semibold transition"
          :class="activeTab === tab.value
            ? 'bg-slate-900 text-white shadow-sm'
            : 'border border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:text-slate-900'"
        >
          {{ tab.label }}
        </button>
      </div>

      <div v-if="filteredListings.length === 0"
        class="rounded-3xl border border-slate-200 bg-white px-6 py-20 text-center shadow-sm"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
        <p class="mt-4 text-base font-medium text-slate-500">No listings found.</p>
        <p class="mt-1 text-sm text-slate-400">
          {{ activeTab === 'all' ? 'Click "Add Listing" to create your first listing.' : 'No listings with this status yet.' }}
        </p>
      </div>

      <div v-else class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="listing in filteredListings"
          :key="listing.id"
          class="group overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-md"
          :class="{ 'opacity-60': listing.status === 'archived' }"
        >
          <!-- Image -->
          <div class="relative h-48 bg-slate-100 overflow-hidden">
            <img
              v-if="listing.images && listing.images.length > 0"
              :src="listing.images[0]"
              :alt="listing.name"
              class="h-full w-full object-cover transition duration-500 group-hover:scale-105"
            />
            <div v-else class="flex h-full w-full items-center justify-center text-slate-300">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-14 w-14" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div class="absolute top-3 left-3">
              <span
                class="rounded-xl px-3 py-1 text-xs font-semibold"
                :class="statusBadgeClass(listing.status)"
              >
                {{ statusLabel(listing.status) }}
              </span>
            </div>
            <div class="absolute top-3 right-3">
              <span class="rounded-xl bg-slate-900/70 px-3 py-1 text-xs font-semibold text-white backdrop-blur-sm">
                {{ listing.category }}
              </span>
            </div>
          </div>

          <div class="p-6">
            <h3 class="text-base font-bold text-slate-900 leading-snug">{{ listing.name }}</h3>
            <p class="mt-1 flex items-center gap-1 text-sm text-slate-500">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 shrink-0 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              {{ listing.city }}, {{ listing.country }}
            </p>
            <p class="mt-2 text-sm text-slate-500 line-clamp-2">{{ listing.description }}</p>

            <div class="mt-4 flex items-center justify-between">
              <div>
                <span class="text-lg font-bold text-slate-900">${{ listing.cost }}</span>
                <span class="text-sm text-slate-400"> / night</span>
              </div>
            </div>

            <div class="mt-4 flex gap-2 border-t border-slate-100 pt-4">
              <button
                v-if="listing.status !== 'archived'"
                @click="openEditModal(listing)"
                class="flex-1 rounded-2xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50"
              >
                Edit
              </button>
              <button
                v-if="listing.status !== 'archived'"
                @click="openArchiveModal(listing)"
                class="flex-1 rounded-2xl border border-red-100 px-4 py-2 text-sm font-semibold text-red-500 transition hover:bg-red-50"
              >
                Archive
              </button>
              <span v-if="listing.status === 'archived'" class="flex-1 text-center text-sm text-slate-400 py-2">
                Listing archived
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div
      v-if="showFormModal"
      class="fixed inset-0 z-50 flex items-center justify-center px-4"
      @click.self="closeFormModal"
    >
      <div class="absolute inset-0 bg-slate-950/50 backdrop-blur-sm"></div>
      <div class="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-3xl border border-slate-200 bg-white shadow-2xl">

        <div class="sticky top-0 z-10 flex items-center justify-between border-b border-slate-100 bg-white px-8 py-6">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-600">
              {{ isEditing ? 'Edit Listing' : 'New Listing' }}
            </p>
            <h2 class="mt-1 text-xl font-bold text-slate-900">
              {{ isEditing ? 'Update your listing details' : 'Create a new listing' }}
            </h2>
          </div>
          <button
            @click="closeFormModal"
            class="flex h-9 w-9 items-center justify-center rounded-2xl border border-slate-200 text-slate-500 transition hover:bg-slate-50"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="submitForm" class="px-8 py-6 space-y-5">

          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">
              Listing Name <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.name"
              type="text"
              placeholder="e.g. Sunset Bay Resort"
              class="w-full rounded-2xl border px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition"
              :class="formErrors.name ? 'border-red-300 bg-red-50 focus:border-red-400' : 'border-slate-200 bg-white focus:border-cyan-400'"
            />
            <p v-if="formErrors.name" class="mt-1.5 text-xs text-red-500">{{ formErrors.name }}</p>
          </div>

          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">
              Category <span class="text-red-500">*</span>
            </label>
            <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <button
                v-for="cat in categories"
                :key="cat.value"
                type="button"
                @click="form.category = cat.value; form.hotelSubcategory = ''"
                class="flex flex-col items-center gap-2 rounded-2xl border py-3.5 text-xs font-semibold transition"
                :class="form.category === cat.value
                  ? 'border-cyan-400 bg-cyan-50 text-cyan-700'
                  : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'"
              >
                <span class="text-xl">{{ cat.icon }}</span>
                {{ cat.label }}
              </button>
            </div>
            <p v-if="formErrors.category" class="mt-1.5 text-xs text-red-500">{{ formErrors.category }}</p>
          </div>

          <div v-if="form.category === 'Hotel'">
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">
              Hotel Type <span class="text-red-500">*</span>
            </label>
            <select
              v-model="form.hotelSubcategory"
              class="w-full rounded-2xl border px-4 py-3 text-sm text-slate-900 outline-none transition"
              :class="formErrors.hotelSubcategory ? 'border-red-300 bg-red-50 focus:border-red-400' : 'border-slate-200 bg-white focus:border-cyan-400'"
            >
              <option value="" disabled>Select hotel type</option>
              <option value="Luxury">Luxury</option>
              <option value="Economy">Economy</option>
              <option value="Romantic">Romantic</option>
              <option value="Boutique">Boutique</option>
              <option value="Budget">Budget</option>
            </select>
            <p v-if="formErrors.hotelSubcategory" class="mt-1.5 text-xs text-red-500">{{ formErrors.hotelSubcategory }}</p>
          </div>

          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">
              Description <span class="text-red-500">*</span>
            </label>
            <textarea
              v-model="form.description"
              rows="3"
              placeholder="Describe what makes this listing special..."
              class="w-full rounded-2xl border px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition resize-none"
              :class="formErrors.description ? 'border-red-300 bg-red-50 focus:border-red-400' : 'border-slate-200 bg-white focus:border-cyan-400'"
            ></textarea>
            <p v-if="formErrors.description" class="mt-1.5 text-xs text-red-500">{{ formErrors.description }}</p>
          </div>

          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">
              Cost (USD) <span class="text-red-500">*</span>
            </label>
            <div class="relative">
              <span class="absolute left-4 top-1/2 -translate-y-1/2 text-sm font-semibold text-slate-400">$</span>
              <input
                v-model="form.cost"
                type="number"
                min="0"
                step="0.01"
                placeholder="0.00"
                class="w-full rounded-2xl border pl-8 pr-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition"
                :class="formErrors.cost ? 'border-red-300 bg-red-50 focus:border-red-400' : 'border-slate-200 bg-white focus:border-cyan-400'"
              />
            </div>
            <p v-if="formErrors.cost" class="mt-1.5 text-xs text-red-500">{{ formErrors.cost }}</p>
          </div>

          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1.5">
                City <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.city"
                type="text"
                placeholder="e.g. Bridgetown"
                class="w-full rounded-2xl border px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition"
                :class="formErrors.city ? 'border-red-300 bg-red-50 focus:border-red-400' : 'border-slate-200 bg-white focus:border-cyan-400'"
              />
              <p v-if="formErrors.city" class="mt-1.5 text-xs text-red-500">{{ formErrors.city }}</p>
            </div>
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1.5">
                Country / Island <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.country"
                type="text"
                placeholder="e.g. Barbados"
                class="w-full rounded-2xl border px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition"
                :class="formErrors.country ? 'border-red-300 bg-red-50 focus:border-red-400' : 'border-slate-200 bg-white focus:border-cyan-400'"
              />
              <p v-if="formErrors.country" class="mt-1.5 text-xs text-red-500">{{ formErrors.country }}</p>
            </div>
          </div>

          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">
              Policies
            </label>
            <textarea
              v-model="form.policies"
              rows="2"
              placeholder="e.g. No smoking, check-in after 3pm, pets allowed..."
              class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400 resize-none"
            ></textarea>
          </div>

          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">
              Image URLs
            </label>
            <div class="space-y-2">
              <div
                v-for="(url, index) in form.images"
                :key="index"
                class="flex gap-2"
              >
                <input
                  v-model="form.images[index]"
                  type="url"
                  :placeholder="`Image URL ${index + 1}`"
                  class="flex-1 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400"
                />
                <button
                  type="button"
                  @click="removeImage(index)"
                  class="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl border border-red-100 text-red-400 transition hover:bg-red-50"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            <button
              type="button"
              @click="addImage"
              class="mt-2 flex items-center gap-1.5 text-sm font-semibold text-cyan-600 transition hover:text-cyan-500"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
              </svg>
              Add Image URL
            </button>
          </div>

          <div class="rounded-2xl border border-amber-100 bg-amber-50 px-5 py-4">
            <div class="flex items-start gap-3">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 shrink-0 text-amber-500 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p class="text-sm text-amber-700">
                <span class="font-semibold">Requires approval.</span>
                {{ isEditing ? 'Edits will be reviewed before the listing updates publicly.' : 'New listings are marked as Pending Approval until reviewed by a moderator.' }}
              </p>
            </div>
          </div>

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
              class="flex-1 rounded-2xl bg-slate-900 py-3 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-slate-800"
            >
              {{ isEditing ? 'Save Changes' : 'Create Listing' }}
            </button>
          </div>

        </form>
      </div>
    </div>

    <div
      v-if="showArchiveModal"
      class="fixed inset-0 z-50 flex items-center justify-center px-4"
      @click.self="showArchiveModal = false"
    >
      <div class="absolute inset-0 bg-slate-950/50 backdrop-blur-sm"></div>
      <div class="relative w-full max-w-md rounded-3xl border border-slate-200 bg-white p-8 shadow-2xl">
        <div class="flex items-start gap-4">
          <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-red-50">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8l1 12a2 2 0 002 2h8a2 2 0 002-2L19 8M10 12v4M14 12v4" />
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-bold text-slate-900">Archive Listing?</h3>
            <p class="mt-2 text-sm leading-6 text-slate-600">
              <span class="font-semibold text-slate-800">{{ listingToArchive?.name }}</span> will be
              hidden from visitors. You can contact support to restore it later.
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
            class="flex-1 rounded-2xl bg-red-500 py-3 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-red-400"
          >
            Archive
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Replace with API calls
const listing = ref([
    {
    id: 1,
    name: 'Sunset Bay Resort',
    category: 'Hotel',
    hotelSubcategory: 'Luxury',
    description: 'A stunning luxury resort perched above the turquoise bay with panoramic ocean views.',
    cost: 320,
    city: 'Bridgetown',
    country: 'Barbados',
    policies: 'No smoking. Check-in after 3pm. Complimentary breakfast included.',
    images: [],
    status: 'active',
    },
    {
        id: 2,
        name: 'Coral Reef Diving Tour',
        category: 'Tour',
        hotelSubcategory: '',
        description: 'Guided snorkelling and diving experience through the vibrant coral reefs of St. Lucia.',
        cost: 75,
        city: 'Castries',
        country: 'St. Lucia',
        policies: 'Must be able to swim. Minimum age 12.',
        images: [],
        status: 'pending',
    },
    {
        id: 3,
        name: 'Spice Garden Restaurant',
        category: 'Restaurant',
        hotelSubcategory: '',
        description: 'Farm-to-table dining featuring authentic Grenadian spices and fresh seafood.',
        cost: 40,
        city: 'St. George\'s',
        country: 'Grenada',
        policies: 'Reservations recommended. Smart casual dress code.',
        images: [],
        status: 'archived',
    },
])

const tabs = [
    { label: 'All', value: 'all' },
    { label: 'Active', value: 'active' },
    { label: 'Pending Approval', value: 'pending' },
    { label: 'Archived', value:'archived'},
]
const activeTab = ref('all')

const filteredListings = computed(() => {
    if(activeTab.value === 'all') return listing.value
    return listing.value.filter(l => l.status === activeTab.value)
})

function statusLabel(status) {
    if (status === 'active') return 'Active'
    if (status === 'pending') return 'Pending Approval'
    if (status === 'archived') return 'Archived'
    return status
}

function statusBadgeClass(status) {
    if (status === 'active') return 'bg-emerald-500 text-white'
    if (status === 'pending') return 'bg-amber-400 text-slate-900'
    if (status === 'archived') return 'bg-slate-500 text-white'
    return 'bg-slate-300 text-slate-900'
}

const stats = computed(() => ({
  total: listing.value.length,
  active: listing.value.filter(l => l.status === 'active').length,
  pending: listing.value.filter(l => l.status === 'pending').length,
  archived: listing.value.filter(l => l.status === 'archived').length,
}))

const categories = [
    { label: 'Hotel', value: 'Hotel', icon: '🏨' },
    { label: 'Restaurant', value: 'Restaurant', icon: '🍽️' },
    { label: 'Tour', value: 'Tour', icon: '🗺️' },
    { label: 'Event / Activity', value: 'Event', icon: '🎉' },
]


const showFormModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)

const blankForm = () => ({
  name: '',
  category: '',
  hotelSubcategory: '',
  description: '',
  cost: '',
  city: '',
  country: '',
  policies: '',
  images: [''],
})

const form = ref(blankForm())
const formErrors = ref({})

function openCreateModal() {
    isEditing.value = false
    editingId.value = null
    form.value = blankForm()
    formErrors.value = {}
    showFormModal.value = true

}

function openEditModal(listing){
    isEditing.value = true
    editingId.value = listing.id
    form.value = {
        name: listing.name,
        category: listing.category,
        hotelSubcategory: listing.hotelSubcategory || '',
        description: listing.description,
        cost: listing.cost,
        city: listing.city,
        country: listing.country,
        policies: listing.policies,
        images: listing.images.length > 0 ? [...listing.images] : [''],
    }
    formErrors.value = {}
    showFormModal.value = true
}

function closeFormModal() {
    showFormModal.value = false
}

function addImage() {
    form.value.images.push('')
}

function removeImage(index) {
    form.value.images.splice(index, 1)
    if (form.value.images.length === 0) form.value.images.push('')
}

function validateForm() {
    const errors = {}

    if (!form.value.name.trim()) errors.name = 'Listing name is required.'
    if (!form.value.category) errors.category = 'Please select a category.'
    if (form.value.category === 'Hotel' && !form.value.hotelSubcategory)
        errors.hotelSubcategory = 'Please select a hotel type.'
    if (!form.value.description.trim()) errors.description = 'Description is required.'
    if (!form.value.cost || Number(form.value.cost) <= 0) errors.cost = 'Please enter a valid cost.'
    if (!form.value.city.trim()) errors.city = 'City is required.'
    if (!form.value.country.trim()) errors.country = 'Country / Island is required.'

    formErrors.value = errors
    return Object.keys(errors).length === 0
}   

function submitForm() {
    if (!validateForm()) return 

    const cleanImages = form.value.images.filter(url => url.trim() !== '')

    if (isEditing.value) {
        const index = listing.value.findIndex(l => l.id === editingId.value)
        if (index !== -1) {
            listing.value[index] = {
                ...listing.value[index],
                name: form.value.name.trim(),
                category: form.value.category,
                hotelSubcategory: form.value.hotelSubcategory,
                description: form.value.description.trim(),
                cost: Number(form.value.cost),
                city: form.value.city.trim(),
                country: form.value.country.trim(),
                policies: form.value.policies.trim(),
                images: cleanImages,
                status: 'pending', // edits go back to pending approval
            }
        }
    }else {
        listing.value.unshift({
            id: Date.now(),
            name: form.value.name.trim(),
            category: form.value.category,
            hotelSubcategory: form.value.hotelSubcategory,
            description: form.value.description.trim(),
            cost: Number(form.value.cost),
            city: form.value.city.trim(),
            country: form.value.country.trim(),
            policies: form.value.policies.trim(),
            images: cleanImages,
            status: 'pending', 
        })
    }  

    closeFormModal()
}

const showArchiveModal = ref(false)
const listingToArchive = ref(null)

function openArchiveModal(listing){
    listingToArchive.value = listing
    showArchiveModal.value = true
}

function confirmArchive() {
    if (!listingToArchive.value) return
    const index = listing.value.findIndex(l => l.id === listingToArchive.value.id)
    if (index !== -1) {
        listing.value[index] = {...listing.value[index], status: 'archived'}

    }
    showArchiveModal.value = false
    listingToArchive.value = null
}


</script>