<template>
  <div class="bg-slate-50 text-slate-900">
    <section
      class="relative overflow-hidden border-b border-slate-200 bg-slate-950"
      style="background-image: linear-gradient(rgba(2, 6, 23, 0.72), rgba(2, 6, 23, 0.82)), url('/images/beach-bkg.jpg'); background-size: cover; background-position: center;">
      <div class="mx-auto flex min-h-[320px] max-w-7xl flex-col justify-end px-4 pb-10 pt-24 sm:px-6 lg:px-8">
        <p class="text-xs font-semibold uppercase tracking-[0.3em] text-cyan-300">
          Itinerary builder
        </p>
        <h1 class="mt-4 max-w-3xl text-4xl font-bold leading-tight text-white sm:text-5xl">
          Shape your Caribbean trip one choice at a time
        </h1>
        <p class="mt-5 max-w-2xl text-base leading-7 text-slate-200">
          Pick your interests, dates, travelers, and trip style. We will turn those choices into a day-by-day preview.
        </p>
      </div>
    </section>

    <section class="px-4 py-10 sm:px-6 lg:px-8">
      <div v-if="!generatedItinerary" class="mx-auto max-w-7xl">
        <ItineraryWizardShell
          :title="activeStep.title"
          :description="activeStep.description"
          :current-step="currentStepIndex"
          :total-steps="steps.length"
          :can-go-back="currentStepIndex > 0"
          :next-label="nextLabel"
          :busy-label="activeStep.type === 'review' ? 'Generating...' : 'Working...'"
          :busy="isGenerating"
          :next-disabled="loadingInterests || isGenerating"
          :error="errorMessage"
          @back="goBack"
          @next="goNext">

          <!-- Categories Modal -->
          <transition :name="slideDirection" mode="out-in">
            <div :key="activeStep.key">
              <div v-if="activeStep.type === 'categories'">
                <div v-if="loadingInterests" class="flex min-h-[280px] items-center justify-center">
                  <div class="text-center">
                    <div class="inline-block h-9 w-9 animate-spin rounded-full border-4 border-slate-200 border-t-cyan-500"></div>
                    <p class="mt-4 text-sm font-medium text-slate-500">Loading categories...</p>
                  </div>
                </div>

                <div
                  v-else-if="categoryNames.length === 0"
                  class="rounded-3xl border border-slate-200 bg-slate-50 px-6 py-12 text-center text-slate-500">
                  No interest categories are available right now.
                </div>

                <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  <button
                    v-for="category in categoryNames"
                    :key="category"
                    type="button"
                    class="group flex min-h-32 flex-col justify-between rounded-3xl border p-5 text-left shadow-sm transition hover:-translate-y-0.5"
                    :class="isCategorySelected(category)
                      ? 'border-cyan-400 bg-cyan-50 text-cyan-900 shadow-cyan-100'
                      : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300'"
                    @click="toggleCategory(category)">
                    <span class="flex items-start justify-between gap-4">
                      <span class="text-lg font-bold capitalize">{{ category }}</span>
                      <span
                        class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full border"
                        :class="isCategorySelected(category) ? 'border-cyan-500 bg-cyan-500 text-white' : 'border-slate-300 text-transparent'">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M16.704 5.29a1 1 0 010 1.42l-7.25 7.25a1 1 0 01-1.42 0l-3.25-3.25a1 1 0 111.42-1.42l2.54 2.55 6.54-6.55a1 1 0 011.42 0z" clip-rule="evenodd" />
                        </svg>
                      </span>
                    </span>
                    <span class="mt-8 text-sm font-medium text-slate-500">
                      {{ groupedInterests[category]?.length || 0 }}
                      {{ groupedInterests[category]?.length === 1 ? 'interest' : 'interests' }}
                    </span>
                  </button>
                </div>
              </div>
              
              <!-- Interest Modal -->
              <div v-else-if="activeStep.type === 'interests'">
                <div class="mb-6 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
                  <div>
                    <p class="text-sm font-semibold text-slate-500">
                      {{ selectedInterestIds.length }}
                      {{ selectedInterestIds.length === 1 ? 'interest' : 'interests' }} selected
                    </p>
                    <div class="mt-3 flex flex-wrap gap-2">
                      <span
                        v-for="category in selectedCategories"
                        :key="category"
                        class="rounded-full bg-cyan-50 px-3 py-1 text-xs font-semibold capitalize text-cyan-700">
                        {{ category }}
                      </span>
                    </div>
                  </div>
                  <p class="text-sm font-medium text-slate-500">
                    Interest set {{ activeStep.pageIndex + 1 }} of {{ interestPages.length }}
                  </p>
                </div>

                <div class="grid gap-3 sm:grid-cols-2">
                  <label
                    v-for="interest in activeInterestPage"
                    :key="interest.id"
                    class="cursor-pointer">
                    <input v-model="selectedInterestIds" type="checkbox" :value="interest.id" class="peer sr-only" />
                    <span
                      class="flex min-h-20 items-center justify-between gap-4 rounded-2xl border border-slate-200 bg-white px-5 py-4 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-cyan-300 hover:bg-cyan-50 peer-checked:border-cyan-500 peer-checked:bg-cyan-50 peer-checked:text-cyan-800">
                      <span>
                        <span class="block text-base">{{ interest.name }}</span>
                        <span class="mt-1 block text-xs font-medium capitalize text-slate-400">{{ interest.category }}</span>
                      </span>
                      <span
                        class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full border"
                        :class="isInterestSelected(interest.id) ? 'border-cyan-500 bg-cyan-500 text-white' : 'border-slate-300 text-transparent'">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M16.704 5.29a1 1 0 010 1.42l-7.25 7.25a1 1 0 01-1.42 0l-3.25-3.25a1 1 0 111.42-1.42l2.54 2.55 6.54-6.55a1 1 0 011.42 0z" clip-rule="evenodd" />
                        </svg>
                      </span>
                    </span>
                  </label>
                </div>
              </div>
              
              <!-- Detination Modal -->
              <div v-else-if="activeStep.type === 'destination'" class="grid gap-5 md:grid-cols-2">
                <label class="block">
                  <span class="text-sm font-semibold text-slate-700">Country</span>
                  <select
                    v-model="country"
                    class="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100">
                    <option value="">Select a country</option>
                    <option
                      v-for="option in countryOptions"
                      :key="option.name"
                      :value="option.name">
                      {{ option.name }}
                    </option>
                  </select>
                </label>

                <label class="block">
                  <span class="text-sm font-semibold text-slate-700">City</span>
                  <select
                    v-model="city"
                    :disabled="!country"
                    class="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-400">
                    <option value="">Select a city</option>
                    <option
                      v-for="option in cityOptions"
                      :key="option"
                      :value="option">
                      {{ option }}
                    </option>
                  </select>
                </label>

                <div class="rounded-3xl border border-slate-200 bg-white p-5 md:col-span-2">
                  <p class="text-sm font-semibold text-slate-900">
                    Destination
                  </p>
                  <p class="mt-1 text-sm text-slate-500">
                    <template v-if="country && city">
                      Your itinerary will focus on {{ city }}, {{ country }}.
                    </template>
                    <template v-else>
                      Choose a country first, then pick a city.
                    </template>
                  </p>
                </div>
              </div>

              <!-- Dates Modal -->
              <div v-else-if="activeStep.type === 'dates'" class="grid gap-5 md:grid-cols-2">
                <label class="block">
                  <span class="text-sm font-semibold text-slate-700">Start date</span>
                  <input
                    v-model="startDate"
                    type="date"
                    :min="today"
                    class="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100"
                  />
                </label>

                <label class="block">
                  <span class="text-sm font-semibold text-slate-700">End date</span>
                  <input
                    v-model="endDate"
                    type="date"
                    :min="startDate || today"
                    class="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100"
                  />
                </label>

                <div class="rounded-3xl border border-slate-200 bg-white p-5 md:col-span-2">
                  <p class="text-sm font-semibold text-slate-900">
                    Trip length
                  </p>
                  <p class="mt-1 text-sm text-slate-500">
                    {{ tripLengthLabel }}
                  </p>
                </div>
              </div>

              <!-- Traveller Types Modal -->
              <div v-else-if="activeStep.type === 'travelers'" class="grid gap-5 sm:grid-cols-2">
                <div class="rounded-3xl border border-slate-200 bg-white p-5">
                  <div class="flex items-center justify-between gap-4">
                    <div>
                      <p class="font-bold text-slate-900">Adults</p>
                      <p class="mt-1 text-sm text-slate-500">Ages 13 and up</p>
                    </div>
                    <div class="flex items-center gap-3">
                      <button
                        type="button"
                        class="flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 bg-white text-xl font-semibold text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40"
                        :disabled="adults <= 1"
                        @click="adults -= 1">
                        -
                      </button>
                      <span class="w-8 text-center text-lg font-bold text-slate-950">{{ adults }}</span>
                      <button
                        type="button"
                        class="flex h-10 w-10 items-center justify-center rounded-full bg-slate-950 text-xl font-semibold text-white transition hover:bg-slate-800"
                        @click="adults += 1">
                        +
                      </button>
                    </div>
                  </div>
                </div>

                <div class="rounded-3xl border border-slate-200 bg-white p-5">
                  <div class="flex items-center justify-between gap-4">
                    <div>
                      <p class="font-bold text-slate-900">Children</p>
                      <p class="mt-1 text-sm text-slate-500">Ages 12 and under</p>
                    </div>
                    <div class="flex items-center gap-3">
                      <button
                        type="button"
                        class="flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 bg-white text-xl font-semibold text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40"
                        :disabled="children <= 0"
                        @click="children -= 1">
                        -
                      </button>
                      <span class="w-8 text-center text-lg font-bold text-slate-950">{{ children }}</span>
                      <button
                        type="button"
                        class="flex h-10 w-10 items-center justify-center rounded-full bg-slate-950 text-xl font-semibold text-white transition hover:bg-slate-800"
                        @click="children += 1">
                        +
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Budget Level (Simple, Premium) and Trip Pace (Relaxed, Balanced )Modal -->
              <div v-else-if="activeStep.type === 'style'" class="grid gap-8 lg:grid-cols-2">
                <div>
                  <p class="mb-3 text-sm font-semibold text-slate-700">Budget level</p>
                  <div class="grid gap-3">
                    <label v-for="option in budgetOptions" :key="option.value" class="cursor-pointer">
                      <input v-model="budgetLevel" type="radio" :value="option.value" class="peer sr-only" />
                      <span class="block rounded-2xl border border-slate-200 bg-white p-5 transition hover:border-cyan-300 peer-checked:border-cyan-500 peer-checked:bg-cyan-50">
                        <span class="block font-bold text-slate-900">{{ option.label }}</span>
                        <span class="mt-1 block text-sm leading-6 text-slate-500">{{ option.description }}</span>
                      </span>
                    </label>
                  </div>
                </div>

                <div>
                  <p class="mb-3 text-sm font-semibold text-slate-700">Trip pace</p>
                  <div class="grid gap-3">
                    <label v-for="option in paceOptions" :key="option.value" class="cursor-pointer">
                      <input v-model="pace" type="radio" :value="option.value" class="peer sr-only" />
                      <span class="block rounded-2xl border border-slate-200 bg-white p-5 transition hover:border-cyan-300 peer-checked:border-cyan-500 peer-checked:bg-cyan-50">
                        <span class="block font-bold text-slate-900">{{ option.label }}</span>
                        <span class="mt-1 block text-sm leading-6 text-slate-500">{{ option.description }}</span>
                      </span>
                    </label>
                  </div>
                </div>
              </div>

              <!-- Review Modal (To see a preview of your decisions) -->
              <div v-else-if="activeStep.type === 'review'" class="grid gap-5 lg:grid-cols-2">
                <div class="rounded-3xl border border-slate-200 bg-white p-5">
                  <p class="text-sm font-semibold uppercase tracking-[0.18em] text-cyan-600">Selections</p>
                  <div class="mt-5 space-y-4 text-sm">
                    <div>
                      <p class="font-semibold text-slate-900">Categories</p>
                      <p class="mt-1 capitalize text-slate-500">{{ selectedCategories.join(', ') }}</p>
                    </div>
                    <div>
                      <p class="font-semibold text-slate-900">Interests</p>
                      <p class="mt-1 text-slate-500">{{ selectedInterestNames.join(', ') }}</p>
                    </div>
                    <div>
                      <p class="font-semibold text-slate-900">Destination</p>
                      <p class="mt-1 text-slate-500">{{ city }}, {{ country }}</p>
                    </div>
                    <div>
                      <p class="font-semibold text-slate-900">Dates</p>
                      <p class="mt-1 text-slate-500">{{ startDate }} to {{ endDate }}</p>
                    </div>
                  </div>
                </div>

                <div class="rounded-3xl border border-slate-200 bg-white p-5">
                  <p class="text-sm font-semibold uppercase tracking-[0.18em] text-cyan-600">Travel style</p>
                  <div class="mt-5 grid gap-3 sm:grid-cols-2">
                    <div class="rounded-2xl bg-slate-50 p-4">
                      <p class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">Travelers</p>
                      <p class="mt-2 font-bold text-slate-900">{{ adults }} adult{{ adults === 1 ? '' : 's' }}, {{ children }} child{{ children === 1 ? '' : 'ren' }}</p>
                    </div>
                    <div class="rounded-2xl bg-slate-50 p-4">
                      <p class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">Budget</p>
                      <p class="mt-2 font-bold capitalize text-slate-900">{{ budgetLevel }}</p>
                    </div>
                    <div class="rounded-2xl bg-slate-50 p-4 sm:col-span-2">
                      <p class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">Pace</p>
                      <p class="mt-2 font-bold capitalize text-slate-900">{{ pace }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </transition>
        </ItineraryWizardShell>
      </div>

      
      <div v-else class="mx-auto max-w-7xl">
        <div class="mb-8 flex flex-col justify-between gap-5 lg:flex-row lg:items-end">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.3em] text-cyan-600">Generated itinerary</p>
            <h2 class="mt-3 text-3xl font-bold text-slate-950 sm:text-4xl">
              Your {{ generatedItinerary.trip_days }} day trip preview
            </h2>
            <p class="mt-3 max-w-2xl text-sm leading-6 text-slate-500">
              Estimated total: ${{ generatedItinerary.total_estimated_cost.toFixed(2) }}.
              This preview is using the frontend mock planner.
            </p>
          </div>

          <div class="flex flex-col gap-3 sm:flex-row">
            <button
              type="button"
              class="rounded-2xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
              @click="generatedItinerary = null">
              Adjust answers
            </button>
            <button
              type="button"
              class="rounded-2xl border border-cyan-200 bg-cyan-50 px-5 py-3 text-sm font-semibold text-cyan-800 transition hover:bg-cyan-100"
              @click="handleProtectedItineraryAction('edit')">
              Edit itinerary
            </button>
            <button
              type="button"
              class="rounded-2xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
              @click="handleProtectedItineraryAction('save')">
              Save itinerary
            </button>
          </div>
        </div>

        <div class="grid gap-6">
          <article
            v-for="(day, dayIndex) in generatedItinerary.days"
            :key="day.date"
            class="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
            <div class="border-b border-slate-200 bg-slate-50 px-5 py-4 sm:px-6">
              <div class="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
                <div>
                  <p class="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-600">Day {{ dayIndex + 1 }}</p>
                  <h3 class="mt-1 text-xl font-bold text-slate-950">{{ formatDisplayDate(day.date) }}</h3>
                </div>
                <p class="text-sm font-semibold text-slate-500">
                  ${{ day.total_estimated_cost.toFixed(2) }} estimated · {{ day.total_duration_hours }} hours
                </p>
              </div>
            </div>

            <div class="divide-y divide-slate-100">
              <div
                v-for="stop in day.stops"
                :key="stop.listing_id"
                class="grid gap-4 px-5 py-5 sm:grid-cols-[140px_1fr_auto] sm:px-6">
                <div>
                  <p class="text-sm font-bold text-slate-950">{{ stop.start_time }} - {{ stop.end_time }}</p>
                  <p class="mt-1 text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">{{ stop.business_type_name }}</p>
                </div>

                <div>
                  <h4 class="font-bold text-slate-950">{{ stop.title }}</h4>
                  <p class="mt-1 text-sm font-medium text-slate-500">
                    {{ stop.address?.city }}, {{ stop.address?.country }}
                  </p>
                  <p class="mt-2 text-sm leading-6 text-slate-500">{{ stop.description }}</p>
                  <div class="mt-3 flex flex-wrap gap-2">
                    <span
                      v-for="tag in stop.reason_tags"
                      :key="tag"
                      class="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-500">
                      {{ tag }}
                    </span>
                  </div>
                </div>

                <p class="text-sm font-bold text-slate-950 sm:text-right">${{ stop.estimated_cost.toFixed(2) }}</p>
              </div>
            </div>
          </article>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import ItineraryWizardShell from '../components/itinerary/ItineraryWizardShell.vue'
import { interestsAPI } from '../services/api'
import { generateItinerary } from '../services/itinerary'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'

const router = useRouter()
const authStore = useAuthStore()
const toastStore = useToastStore()

const allInterests = ref([])
const loadingInterests = ref(true)
const currentStepIndex = ref(0)
const selectedCategories = ref([])
const selectedInterestIds = ref([])

const country = ref('')
const city = ref('')
const startDate = ref('')
const endDate = ref('')
const adults = ref(2)
const children = ref(0)
const budgetLevel = ref('medium')
const pace = ref('balanced')
const generatedItinerary = ref(null)
const isGenerating = ref(false)
const errorMessage = ref('')
const slideDirection = ref('slide-left')

const countryOptions = [
  {
    name: 'Barbados',
    cities: ['Bridgetown', 'Holetown', 'Oistins', 'Speightstown'],
  },
  {
    name: 'Jamaica',
    cities: ['Kingston', 'Montego Bay', 'Negril', 'Ocho Rios'],
  },
  {
    name: 'Trinidad and Tobago',
    cities: ['Port of Spain', 'San Fernando', 'Scarborough'],
  },
  {
    name: 'Guyana',
    cities: ['Georgetown', 'Linden', 'New Amsterdam'],
  },
]


const budgetOptions = [
  { value: 'low', label: 'Simple', description: 'Prioritize lower-cost stops and lighter spending.' },
  { value: 'medium', label: 'Balanced', description: 'Mix affordable picks with standout experiences.' },
  { value: 'high', label: 'Premium', description: 'Leave room for higher-end stays, dining, and tours.' },
]

const paceOptions = [
  { value: 'relaxed', label: 'Relaxed', description: 'Fewer stops with more open time between plans.' },
  { value: 'balanced', label: 'Balanced', description: 'A steady day with time for both plans and rest.' },
  { value: 'packed', label: 'Packed', description: 'More stops for travelers who want a fuller schedule.' },
]

const today = computed(() => toDateInputValue(new Date()))

const cityOptions = computed(() => {
  return countryOptions.find((item) => item.name === country.value)?.cities || []
})


onMounted(async () => {
  try {
    const response = await interestsAPI.getAll()
    allInterests.value = Array.isArray(response.data) ? response.data : []
  } catch (error) {
    console.error('Failed to load itinerary interests', error)
    toastStore.show('Failed to load trip interests.', 'error')
  } finally {
    loadingInterests.value = false
  }
})

const groupedInterests = computed(() => {
  return allInterests.value.reduce((groups, interest) => {
    const category = interest.category || 'Other'
    if (!groups[category]) groups[category] = []
    groups[category].push(interest)
    groups[category].sort((a, b) => a.name.localeCompare(b.name))
    return groups
  }, {})
})

const categoryNames = computed(() => Object.keys(groupedInterests.value).sort((a, b) => a.localeCompare(b)))

const filteredInterests = computed(() => {
  const selected = new Set(selectedCategories.value)
  return allInterests.value
    .filter((interest) => selected.has(interest.category || 'Other'))
    .sort((a, b) => {
      const categorySort = (a.category || 'Other').localeCompare(b.category || 'Other')
      if (categorySort !== 0) return categorySort
      return a.name.localeCompare(b.name)
    })
})

const interestPages = computed(() => {
  const pages = []
  const items = filteredInterests.value
  for (let index = 0; index < items.length; index += 5) {
    pages.push(items.slice(index, index + 5))
  }
  return pages.length ? pages : [[]]
})

const steps = computed(() => [
  {
    key: 'categories',
    type: 'categories',
    title: 'Choose your interest categories',
    description: 'Start broad. These categories decide which specific interests appear next.',
  },

  ...interestPages.value.map((_, pageIndex) => ({
    key: `interests-${pageIndex}`,
    type: 'interests',
    pageIndex,
    title: 'Choose specific interests',
    description: 'Pick the activities, food, places, and travel themes that should influence the itinerary.',
  })),
  {
    key: 'destination',
    type: 'destination',
    title: 'Choose your destination',
    description: 'Pick the country and city you want this itinerary to focus on.',
  },
  {
    key: 'dates',
    type: 'dates',
    title: 'Choose your dates',
    description: 'The itinerary preview will create one plan for each day in the date range.',
  },
  {
    key: 'travelers',
    type: 'travelers',
    title: 'Who is going?',
    description: 'Traveler counts are kept in the frontend payload so the backend can use them later.',
  },
  {
    key: 'style',
    type: 'style',
    title: 'Set the trip style',
    description: 'Budget and pace help shape how full and flexible each day should feel.',
  },
  {
    key: 'review',
    type: 'review',
    title: 'Review and generate',
    description: 'Confirm your choices before generating the itinerary preview.',
  },
])

const activeStep = computed(() => steps.value[currentStepIndex.value] || steps.value[0])
const activeInterestPage = computed(() => interestPages.value[activeStep.value?.pageIndex || 0] || [])

const nextLabel = computed(() => {
  if (activeStep.value.type === 'review') return 'Generate itinerary'
  return 'Next'
})

const selectedInterestNames = computed(() => {
  const selectedIds = new Set(selectedInterestIds.value.map(String))
  return allInterests.value
    .filter((interest) => selectedIds.has(String(interest.id)))
    .map((interest) => interest.name)
})

const tripLength = computed(() => {
  if (!startDate.value || !endDate.value || endDate.value < startDate.value) return 0
  const start = parseLocalDate(startDate.value)
  const end = parseLocalDate(endDate.value)
  return Math.max(1, Math.round((end.getTime() - start.getTime()) / 86400000) + 1)
})

const tripLengthLabel = computed(() => {
  if (!startDate.value || !endDate.value) return 'Choose both dates to preview the trip length.'
  if (endDate.value < startDate.value) return 'End date must be on or after the start date.'
  if (tripLength.value > 14) return 'Keep this first planner version to 14 days or fewer.'
  return `${tripLength.value} ${tripLength.value === 1 ? 'day' : 'days'}`
})

watch(selectedCategories, () => {
  const validIds = new Set(filteredInterests.value.map((interest) => String(interest.id)))
  selectedInterestIds.value = selectedInterestIds.value.filter((id) => validIds.has(String(id)))
})

watch(country, () => {
  city.value = ''
})


watch(steps, () => {
  if (currentStepIndex.value > steps.value.length - 1) {
    currentStepIndex.value = Math.max(0, steps.value.length - 1)
  }
})

function toggleCategory(category) {
  errorMessage.value = ''
  if (isCategorySelected(category)) {
    selectedCategories.value = selectedCategories.value.filter((item) => item !== category)
    return
  }
  selectedCategories.value = [...selectedCategories.value, category]
}

function isCategorySelected(category) {
  return selectedCategories.value.includes(category)
}

function isInterestSelected(interestId) {
  return selectedInterestIds.value.map(String).includes(String(interestId))
}

function goBack() {
  if (currentStepIndex.value === 0 || isGenerating.value) return
  slideDirection.value = 'slide-right'
  currentStepIndex.value -= 1
  errorMessage.value = ''
}

async function goNext() {
  const validation = getValidationMessage()
  if (validation) {
    errorMessage.value = validation
    return
  }

  errorMessage.value = ''

  if (activeStep.value.type === 'review') {
    await handleGenerate()
    return
  }

  slideDirection.value = 'slide-left'
  currentStepIndex.value += 1
}

async function handleGenerate() {
  isGenerating.value = true

  try {
    generatedItinerary.value = await generateItinerary(buildPayload())
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch (error) {
    console.error('Failed to generate itinerary', error)
    errorMessage.value = 'Could not generate an itinerary right now.'
  } finally {
    isGenerating.value = false
  }
}

function buildPayload() {
  return {
    start_date: startDate.value,
    end_date: endDate.value,
    city: city.value,
    country: country.value,
    interests: selectedInterestNames.value,
    preferred_business_types: selectedCategories.value,
    budget_level: budgetLevel.value,
    pace: pace.value,
    travelers: {
      adults: adults.value,
      children: children.value,
    },
  }
}

function getValidationMessage() {
  if (activeStep.value.type === 'categories') {
    if (loadingInterests.value) return 'Categories are still loading.'
    if (categoryNames.value.length === 0) return 'No categories are available right now.'
    if (selectedCategories.value.length === 0) return 'Choose at least one category.'
  }

  if (activeStep.value.type === 'interests') {
    if (selectedInterestIds.value.length === 0) return 'Choose at least one interest.'
  }

  if (activeStep.value.type === 'destination') {
    if (!country.value) return 'Choose a country.'
    if (!city.value) return 'Choose a city.'
  }


  if (activeStep.value.type === 'dates') {
    if (!startDate.value || !endDate.value) return 'Choose a start date and end date.'
    if (endDate.value < startDate.value) return 'End date must be on or after the start date.'
    if (tripLength.value > 14) return 'Choose a trip that is 14 days or fewer.'
  }

  if (activeStep.value.type === 'travelers') {
    if (adults.value < 1) return 'At least one adult is required.'
  }

  return ''
}

function handleProtectedItineraryAction(action) {
  if (!authStore.isAuthenticated) {
    toastStore.show(`Sign in to ${action} your itinerary.`, 'info')
    router.push({ name: 'Login', query: { redirect: '/itinerary' } })
    return
  }

  toastStore.show('Saving and editing itineraries will be available when the backend is ready.', 'info')
}

function formatDisplayDate(value) {
  return parseLocalDate(value).toLocaleDateString(undefined, {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  })
}

function parseLocalDate(value) {
  const [year, month, day] = value.split('-').map(Number)
  return new Date(year, month - 1, day)
}

function toDateInputValue(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}
</script>

<style scoped>
.slide-left-enter-active,
.slide-left-leave-active,
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.24s ease;
}

.slide-left-enter-from {
  opacity: 0;
  transform: translateX(28px);
}

.slide-left-leave-to {
  opacity: 0;
  transform: translateX(-28px);
}

.slide-right-enter-from {
  opacity: 0;
  transform: translateX(-28px);
}

.slide-right-leave-to {
  opacity: 0;
  transform: translateX(28px);
}
</style>
