<template>
  <div class="space-y-5 rounded-2xl border border-slate-200 bg-slate-50 p-6">
    <p class="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-600">Tour Details</p>
    <div class="grid grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-semibold text-slate-700 mb-1.5">Duration (hours)</label>
        <input
          :value="modelValue.duration ?? ''"
          @input="update('duration', $event.target.value ? Number($event.target.value) : null)"
          type="number" min="0" step="0.5" placeholder="e.g. 3"
          class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400"
        />
      </div>
      <div>
        <label class="block text-sm font-semibold text-slate-700 mb-1.5">Max Capacity</label>
        <input
          :value="modelValue.max_capacity ?? ''"
          @input="update('max_capacity', $event.target.value ? Number($event.target.value) : null)"
          type="number" min="0" placeholder="e.g. 20"
          class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400"
        />
      </div>
    </div>
    <div>
      <label class="block text-sm font-semibold text-slate-700 mb-1.5">Available Slots</label>
      <input
        :value="modelValue.available_slots ?? ''"
        @input="update('available_slots', $event.target.value ? Number($event.target.value) : null)"
        type="number" min="0" placeholder="e.g. 8"
        class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400"
      />
    </div>

    <div>
      <label class="block text-sm font-semibold text-slate-700 mb-2">Available Days</label>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="day in days"
          :key="day"
          type="button"
          @click="toggleDay(day)"
          class="rounded-2xl border px-3 py-1.5 text-xs font-semibold transition"
          :class="selectedDays.includes(day)
            ? 'border-cyan-400 bg-cyan-50 text-cyan-700'
            : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'"
        >{{ day }}</button>
      </div>
    </div>

    <div>
      <label class="block text-sm font-semibold text-slate-700 mb-1.5">Schedule Notes</label>
      <input
        :value="modelValue.service_availability ?? ''"
        @input="update('service_availability', $event.target.value || null)"
        type="text" placeholder="e.g. Departures at 9am and 2pm"
        class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: Object, default: () => ({}) },
})
const emit = defineEmits(['update:modelValue'])

function update(key, value) {
  emit('update:modelValue', { ...props.modelValue, [key]: value })
}

const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

const selectedDays = computed(() => props.modelValue.available_days ?? [])

function toggleDay(day) {
  const current = [...selectedDays.value]
  const idx = current.indexOf(day)
  if (idx === -1) current.push(day)
  else current.splice(idx, 1)
  update('available_days', current)
}
</script>
