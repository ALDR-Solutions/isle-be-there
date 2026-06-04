<template>
  <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-[0.25em] text-cyan-600">
          {{ headerEyebrow }}
        </p>
        <h2 class="mt-2 text-2xl font-bold text-slate-900">{{ headerTitle }}</h2>
        <p class="mt-2 text-sm leading-6 text-slate-500">
          {{ headerDescription }}
        </p>
      </div>

      <div v-if="services.length > 1" class="flex gap-2">
        <button
          type="button"
          class="flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 text-slate-600 transition hover:border-slate-300 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
          :disabled="loading"
          @click="scrollByCards(-1)"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <button
          type="button"
          class="flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 text-slate-600 transition hover:border-slate-300 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
          :disabled="loading"
          @click="scrollByCards(1)"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>

    <div v-if="loading" class="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      <div
        v-for="index in 3"
        :key="index"
        class="h-56 animate-pulse rounded-3xl border border-slate-200 bg-slate-50"
      ></div>
    </div>

    <div
      v-else-if="services.length === 0"
      class="mt-6 rounded-3xl border-2 border-dashed border-slate-200 bg-slate-50 px-6 py-12 text-center"
    >
      <p class="text-base font-semibold text-slate-800">No active services available</p>
      <p class="mt-2 text-sm text-slate-500">
        This listing can’t be booked yet because there are no active services to choose from.
      </p>
    </div>

    <div
      v-else
      ref="scrollContainerRef"
      class="no-scrollbar mt-6 flex snap-x snap-mandatory gap-4 overflow-x-auto pb-2"
    >
      <button
        v-for="service in services"
        :key="service.service_id"
        type="button"
        class="group min-w-[280px] flex-1 snap-start rounded-3xl border p-5 text-left transition md:min-w-[320px]"
        :class="selectedServiceId === service.service_id
          ? 'border-cyan-500 bg-cyan-50/70 shadow-sm shadow-cyan-100'
          : 'border-slate-200 bg-white hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-sm'"
        @click="$emit('select', service.service_id)"
      >
        <div v-if="service.image_urls?.length" class="mb-4 overflow-hidden rounded-2xl bg-slate-100">
          <img
            :src="service.image_urls[0]"
            :alt="service.name || 'Service image'"
            class="h-40 w-full object-cover transition duration-300 group-hover:scale-[1.02]"
          />
        </div>
        <div
          v-else
          class="mb-4 flex h-40 items-center justify-center rounded-2xl border border-dashed border-slate-200 bg-slate-50 text-slate-300"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>

        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="truncate text-lg font-bold text-slate-900">{{ service.name || 'Unnamed service' }}</p>
            <p v-if="summaryText(service)" class="mt-1 text-sm font-medium text-slate-600">
              {{ summaryText(service) }}
            </p>
          </div>

          <span
            class="rounded-full px-3 py-1 text-xs font-semibold"
            :class="selectedServiceId === service.service_id ? 'bg-cyan-600 text-white' : 'bg-slate-100 text-slate-600'"
          >
            {{ selectedServiceId === service.service_id ? 'Selected' : 'Select' }}
          </span>
        </div>

        <p v-if="service.description" class="mt-4 line-clamp-3 text-sm leading-6 text-slate-500">
          {{ service.description }}
        </p>
        <p v-else class="mt-4 text-sm leading-6 text-slate-400">
          Choose this option to continue with the right booking details.
        </p>

        <div v-if="availabilityText(service)" class="mt-4 rounded-2xl bg-slate-100 px-4 py-3 text-xs font-medium text-slate-500">
          {{ availabilityText(service) }}
        </div>

        <div class="mt-5 flex items-end justify-between gap-3">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
              {{ isRestaurant ? 'Average spend' : 'Price' }}
            </p>
            <p class="mt-1 text-2xl font-bold text-slate-900">
              {{ formatPrice(service.price) }}
            </p>
          </div>

          <div v-if="service.capacity != null" class="text-right text-xs font-medium text-slate-500">
            Capacity {{ service.capacity }}
          </div>
        </div>
      </button>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  services: {
    type: Array,
    default: () => [],
  },
  selectedServiceId: {
    type: [String, Number],
    default: '',
  },
  loading: {
    type: Boolean,
    default: false,
  },
  businessTypeName: {
    type: String,
    default: '',
  },
})

defineEmits(['select'])

const scrollContainerRef = ref(null)

const normalizedBusinessType = computed(() => (props.businessTypeName || '').toLowerCase())
const isRestaurant = computed(() => normalizedBusinessType.value === 'restaurant')

const headerEyebrow = computed(() => (isRestaurant.value ? 'Reservation Options' : 'Choose A Service'))
const headerTitle = computed(() => (isRestaurant.value ? 'Pick your dining experience' : 'Select the service you want'))
const headerDescription = computed(() => (
  isRestaurant.value
    ? 'Choose how you want to reserve, then continue with your party details and timing.'
    : 'Select a service first so we can show the exact booking details and availability for this listing.'
))

function scrollByCards(direction) {
  if (!scrollContainerRef.value) return
  scrollContainerRef.value.scrollBy({
    left: direction * 340,
    behavior: 'smooth',
  })
}

function formatPrice(value) {
  const numericValue = Number(value)
  return Number.isFinite(numericValue) ? `$${numericValue.toFixed(2)}` : '$0.00'
}

function availabilityText(service) {
  const availability = service?.availability
  if (!availability || typeof availability !== 'object') return ''

  const days = Array.isArray(availability.available_days) ? availability.available_days.filter(Boolean) : []
  const notes = typeof availability.notes === 'string' ? availability.notes.trim() : ''

  if (days.length && notes) return `${days.join(', ')} - ${notes}`
  return days.join(', ') || notes || ''
}

function summaryText(service) {
  const typeData = service?.type_data && typeof service.type_data === 'object' ? service.type_data : {}

  if (normalizedBusinessType.value === 'hotel') {
    const parts = []
    if (typeData.room_type) parts.push(typeData.room_type)
    if (Array.isArray(typeData.room_amenities) && typeData.room_amenities.length) {
      parts.push(typeData.room_amenities.slice(0, 2).join(', '))
    }
    return parts.join(' | ')
  }

  return ''
}
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
</style>
