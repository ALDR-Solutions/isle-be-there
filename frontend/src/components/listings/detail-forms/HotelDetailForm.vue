<template>
  <div class="space-y-5 rounded-2xl border border-slate-200 bg-slate-50 p-6">
    <p class="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-600">Hotel Details</p>

    <div>
      <label class="block text-sm font-semibold text-slate-700 mb-2">Star Rating</label>
      <div class="flex items-center gap-1">
        <button
          v-for="i in 5"
          :key="i"
          type="button"
          @click="update('star_level', i)"
          class="transition hover:scale-110">
          <svg
            class="h-7 w-7"
            :class="i <= (modelValue.star_level ?? 0) ? 'text-amber-400' : 'text-slate-200'"
            fill="currentColor"
            viewBox="0 0 20 20">
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
        </button>
        <span v-if="modelValue.star_level" class="ml-2 text-sm text-slate-500">{{ modelValue.star_level }}-star</span>
      </div>
    </div>

    <div class="grid grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-semibold text-slate-700 mb-1.5">Total Rooms</label>
        <input
          :value="modelValue.total_rooms ?? ''"
          @input="update('total_rooms', $event.target.value ? Number($event.target.value) : null)"
          type="number" min="0" placeholder="e.g. 50"
          class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400"
        />
      </div>
      <div>
        <label class="block text-sm font-semibold text-slate-700 mb-1.5">Available Rooms</label>
        <input
          :value="modelValue.available_rooms ?? ''"
          @input="update('available_rooms', $event.target.value ? Number($event.target.value) : null)"
          type="number" min="0" placeholder="e.g. 12"
          class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400"
        />
      </div>
    </div>
    <div>
      <label class="block text-sm font-semibold text-slate-700 mb-1.5">Free Cancellation Until (hours before check-in)</label>
      <input
        :value="modelValue.cancellation_until_hours ?? ''"
        @input="update('cancellation_until_hours', $event.target.value ? Number($event.target.value) : null)"
        type="number" min="0" placeholder="e.g. 24"
        class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400"
      />
    </div>
    <div class="flex items-center justify-between">
      <label class="text-sm font-semibold text-slate-700">Deposit Required</label>
      <button
        type="button"
        @click="update('deposit_required', !modelValue.deposit_required)"
        class="relative inline-flex h-6 w-11 items-center rounded-full transition"
        :class="modelValue.deposit_required ? 'bg-cyan-400' : 'bg-slate-200'">
        <span
          class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition"
          :class="modelValue.deposit_required ? 'translate-x-6' : 'translate-x-1'"
        />
      </button>
    </div>
    <div>
      <label class="block text-sm font-semibold text-slate-700 mb-1.5">Amenities</label>
      <div class="flex gap-2">
        <input
          v-model="amenityInput"
          @keydown.enter.prevent="addAmenity"
          type="text" placeholder="e.g. WiFi, Pool, Gym — press Enter to add"
          class="flex-1 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400"
        />
        <button
          type="button"
          @click="addAmenity"
          class="rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
        >Add</button>
      </div>
      <div v-if="modelValue.hotel_amenities?.length" class="mt-3 flex flex-wrap gap-2">
        <span
          v-for="(amenity, i) in modelValue.hotel_amenities"
          :key="amenity"
          class="flex items-center gap-1.5 rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
          {{ amenity }}
          <button type="button" @click="removeAmenity(i)" class="text-slate-400 hover:text-slate-700">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  modelValue: { type: Object, default: () => ({}) },
})
const emit = defineEmits(['update:modelValue'])

function update(key, value) {
  emit('update:modelValue', { ...props.modelValue, [key]: value })
}

const amenityInput = ref('')

function addAmenity() {
  const val = amenityInput.value.trim()
  if (!val) return
  const existing = props.modelValue.hotel_amenities ?? []
  if (!existing.includes(val)) {
    update('hotel_amenities', [...existing, val])
  }
  amenityInput.value = ''
}

function removeAmenity(index) {
  const updated = [...(props.modelValue.hotel_amenities ?? [])]
  updated.splice(index, 1)
  update('hotel_amenities', updated)
}
</script>
