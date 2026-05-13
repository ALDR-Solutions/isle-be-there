<template>
  <div class="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
    <!-- Header -->
    <div class="border-b border-slate-100 bg-slate-50 px-5 py-4">
      <div class="flex items-start justify-between gap-4">
        <div class="min-w-0 flex-1">
          <h3 class="font-bold text-slate-950">{{ item.title }}</h3>
          <p class="mt-1 text-sm text-slate-500">Hotel Stay</p>
          <p class="mt-1 text-sm text-slate-400">
            Check-in: {{ formattedCheckIn }} · Check-out: {{ formattedCheckOut }}
          </p>
        </div>
        <div class="flex flex-col items-end gap-2">
          <span class="inline-flex rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700">
            Hotel
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

      <!-- Check-in Date -->
      <label class="block">
        <span class="text-sm font-semibold text-slate-700">
          Check-in date <span class="text-red-500">*</span>
        </span>
        <input
          :value="checkInDateValue"
          type="date"
          class="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100"
          @input="updateCheckInDate($event.target.value)"
        />
        <p v-if="errors.check_in_date" class="mt-1 text-xs text-red-500">{{ errors.check_in_date }}</p>
      </label>

      <!-- Check-out Date -->
      <label class="block">
        <span class="text-sm font-semibold text-slate-700">
          Check-out date <span class="text-red-500">*</span>
        </span>
        <input
          :value="checkOutDateValue"
          type="date"
          class="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 focus:ring-cyan-100"
          @input="updateCheckOutDate($event.target.value)"
        />
        <p v-if="errors.check_out_date" class="mt-1 text-xs text-red-500">{{ errors.check_out_date }}</p>
      </label>

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
  }
})

const emit = defineEmits(['update:modelValue'])

const errors = reactive({
  bookers_name: '',
  check_in_date: '',
  check_out_date: ''
})

const formData = computed(() => props.modelValue)

// Format check-in date for display
const formattedCheckIn = computed(() => {
  if (!props.item.start_at) return 'Not set';
  const date = new Date(props.item.start_at);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
});

// Format check-out date for display
const formattedCheckOut = computed(() => {
  if (!props.item.end_at) return 'Not set';
  const date = new Date(props.item.end_at);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
});

// Extract date part from check-in datetime string
const checkInDateValue = computed(() => {
  const datetime = formData.value.booking_from_time
  if (!datetime) return ''
  return datetime.slice(0, 10) // YYYY-MM-DD
})

// Extract date part from check-out datetime string
const checkOutDateValue = computed(() => {
  const datetime = formData.value.booking_to_time
  if (!datetime) return ''
  return datetime.slice(0, 10) // YYYY-MM-DD
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

function updateCheckInDate(date) {
  // Always use 14:00 for hotel check-in time
  emit('update:modelValue', {
    ...formData.value,
    booking_from_time: date ? `${date}T14:00:00` : null
  })
}

function updateCheckOutDate(date) {
  // Always use 11:00 for hotel check-out time
  emit('update:modelValue', {
    ...formData.value,
    booking_to_time: date ? `${date}T11:00:00` : null
  })
}

// Validate the form
function validate() {
  errors.bookers_name = ''
  errors.check_in_date = ''
  errors.check_out_date = ''

  let isValid = true

  if (!formData.value.bookers_name || !formData.value.bookers_name.trim()) {
    errors.bookers_name = "Booker's name is required"
    isValid = false
  }

  if (!checkInDateValue.value) {
    errors.check_in_date = 'Check-in date is required'
    isValid = false
  }

  if (!checkOutDateValue.value) {
    errors.check_out_date = 'Check-out date is required'
    isValid = false
  }

  if (checkInDateValue.value && checkOutDateValue.value) {
    if (checkOutDateValue.value <= checkInDateValue.value) {
      errors.check_out_date = 'Check-out must be after check-in'
      isValid = false
    }
  }

  return isValid
}

// Expose validate method for parent components
defineExpose({
  validate
})
</script>