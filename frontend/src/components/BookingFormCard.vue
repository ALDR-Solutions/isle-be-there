<template>
  <div class="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
    <!-- Header -->
    <div class="border-b border-slate-100 bg-slate-50 px-5 py-4">
      <div class="flex items-start justify-between gap-4">
        <div class="min-w-0 flex-1">
          <h3 class="font-bold text-slate-950">{{ item.title }}</h3>
          <p class="mt-1 text-sm text-slate-500">{{ item.address?.city }}, {{ item.address?.country }}</p>
        </div>
        <div class="flex flex-col items-end gap-2">
          <span
            class="inline-flex rounded-full px-3 py-1 text-xs font-semibold capitalize"
            :class="businessTypeBadgeClass"
          >
            {{ item.business_type_name || item.item_type }}
          </span>
          <p class="text-sm font-bold text-slate-950">
            ${{ item.estimated_cost?.toFixed(2) || '0.00' }}
          </p>
        </div>
      </div>
    </div>

    <!-- Form -->
    <form class="grid gap-4 p-5" @submit.prevent>
      <!-- Booker's Name -->
      <label class="block">
        <span class="text-sm font-semibold text-slate-700">
          Service <span class="text-red-500">*</span>
        </span>
        <select
          :value="formData.service_id || ''"
          class="mt-2 w-full rounded-2xl border bg-white px-4 py-3 text-sm font-semibold text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100"
          :class="errors.service_id ? 'border-red-300' : 'border-slate-200'"
          :disabled="servicesLoading || services.length === 0"
          @change="updateField('service_id', $event.target.value || null)"
        >
          <option value="">
            {{ servicesLoading ? 'Loading services...' : services.length === 0 ? 'No active services available' : '-- Select a service --' }}
          </option>
          <option
            v-for="service in services"
            :key="service.service_id"
            :value="service.service_id"
          >
            {{ serviceOptionLabel(service) }}
          </option>
        </select>
        <p v-if="services.length > 1" class="mt-1 text-xs text-slate-500">
          Choose the exact service you want to book for this listing.
        </p>
        <p v-if="services.length === 0 && !servicesLoading" class="mt-1 text-xs text-amber-600">
          This listing has no active services available for booking right now.
        </p>
        <p v-if="errors.service_id" class="mt-1 text-xs text-red-500">{{ errors.service_id }}</p>
      </label>

      <!-- Booker's Name -->
      <label class="block">
        <span class="text-sm font-semibold text-slate-700">
          Booker's name <span class="text-red-500">*</span>
        </span>
        <input
          :value="formData.bookers_name"
          type="text"
          placeholder="Enter your full name"
          required
          class="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100"
          @input="updateField('bookers_name', $event.target.value)"
        />
        <p v-if="errors.bookers_name" class="mt-1 text-xs text-red-500">{{ errors.bookers_name }}</p>
      </label>

      <!-- Date -->
      <label class="block">
        <span class="text-sm font-semibold text-slate-700">Date</span>
        <input
          :value="dateValue"
          type="date"
          class="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100"
          @input="updateDateField($event.target.value)"
        />
      </label>

      <!-- Time Start / End -->
      <div class="grid grid-cols-2 gap-3">
        <label class="block">
          <span class="text-sm font-semibold text-slate-700">Time start</span>
          <input
            :value="timeStartValue"
            type="time"
            class="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100"
            @input="updateTimeStartField($event.target.value)"
          />
        </label>
        <label class="block">
          <span class="text-sm font-semibold text-slate-700">Time end</span>
          <input
            :value="timeEndValue"
            type="time"
            class="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100"
            @input="updateTimeEndField($event.target.value)"
          />
        </label>
      </div>

      <!-- Number of People -->
      <label class="block">
        <span class="text-sm font-semibold text-slate-700">Number of people</span>
        <input
          :value="formData.amount_of_people"
          type="number"
          min="1"
          class="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100"
          @input="updateField('amount_of_people', parseInt($event.target.value) || 1)"
        />
      </label>

      <!-- Special Requests -->
      <label class="block">
        <span class="text-sm font-semibold text-slate-700">Special requests <span class="text-slate-400">(optional)</span></span>
        <textarea
          :value="formData.special_requests"
          rows="3"
          placeholder="Any dietary requirements, accessibility needs, or special arrangements..."
          class="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100 resize-none"
          @input="updateField('special_requests', $event.target.value)"
        ></textarea>
      </label>
    </form>
  </div>
</template>

<script setup>
import { computed, reactive } from 'vue'

const props = defineProps({
  item: {
    type: Object,
    required: true
  },
  modelValue: {
    type: Object,
    required: true
  },
  services: {
    type: Array,
    default: () => []
  },
  servicesLoading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const errors = reactive({
  service_id: '',
  bookers_name: ''
})

const formData = computed(() => props.modelValue)

// Extract date part from datetime string
const dateValue = computed(() => {
  const datetime = formData.value.booking_from_time
  if (!datetime) return ''
  return datetime.slice(0, 10) // YYYY-MM-DD
})

// Extract time part from datetime string for start time
const timeStartValue = computed(() => {
  const datetime = formData.value.booking_from_time
  if (!datetime) return ''
  return datetime.slice(11, 16) // HH:MM
})

// Extract time part from datetime string for end time
const timeEndValue = computed(() => {
  const datetime = formData.value.booking_to_time
  if (!datetime) return ''
  return datetime.slice(11, 16) // HH:MM
})

// Business type badge classes
const businessTypeBadgeClass = computed(() => {
  const type = (props.item?.business_type_name || props.item?.item_type || '').toLowerCase()
  const classes = {
    hotel: 'bg-blue-100 text-blue-700',
    restaurant: 'bg-orange-100 text-orange-700',
    tour: 'bg-green-100 text-green-700',
    activity: 'bg-purple-100 text-purple-700'
  }
  return classes[type] || 'bg-slate-100 text-slate-600'
})

function updateField(field, value) {
  if (typeof value === 'object' && value !== null) {
    emit('update:modelValue', value)
  } else {
    emit('update:modelValue', {
      ...formData.value,
      [field]: value
    })
  }
}

function updateDateField(date) {
  // Update both booking_from_time and booking_to_time with new date
  const currentFromTime = timeStartValue.value || '09:00'
  const currentToTime = timeEndValue.value || '10:00'

  emit('update:modelValue', {
    ...formData.value,
    booking_from_time: date ? `${date}T${currentFromTime}:00` : null,
    booking_to_time: date ? `${date}T${currentToTime}:00` : null
  })
}

function updateTimeStartField(time) {
  const currentDate = dateValue.value
  emit('update:modelValue', {
    ...formData.value,
    booking_from_time: currentDate && time ? `${currentDate}T${time}:00` : null
  })
}

function updateTimeEndField(time) {
  const currentDate = dateValue.value
  emit('update:modelValue', {
    ...formData.value,
    booking_to_time: currentDate && time ? `${currentDate}T${time}:00` : null
  })
}

function serviceOptionLabel(service) {
  if (service?.price !== null && service?.price !== undefined) {
    const price = Number(service.price)
    if (Number.isFinite(price)) {
      return `${service.name} ($${price.toFixed(2)})`
    }
  }
  return service?.name || 'Unnamed service'
}

// Validate the form
function validate() {
  errors.service_id = ''
  errors.bookers_name = ''
  if (!formData.value.service_id) {
    errors.service_id = props.services.length === 0
      ? 'No active services are available for this listing.'
      : 'Please choose a service.'
  }
  if (!formData.value.bookers_name || !formData.value.bookers_name.trim()) {
    errors.bookers_name = "Booker's name is required"
  }
  return !errors.service_id && !errors.bookers_name
}

// Expose validate method for parent components
defineExpose({
  validate
})
</script>
