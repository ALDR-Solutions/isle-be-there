<template>
  <div class="space-y-5 rounded-2xl border border-slate-200 bg-slate-50 p-6">
    <p class="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-600">Restaurant Details</p>
    <div>
      <label class="block text-sm font-semibold text-slate-700 mb-3">Service Options</label>
      <div class="space-y-3">
        <div v-for="option in serviceOptions" :key="option.key" class="flex items-center justify-between">
          <span class="text-sm text-slate-700">{{ option.label }}</span>
          <button
            type="button"
            @click="update(option.key, !modelValue[option.key])"
            class="relative inline-flex h-6 w-11 items-center rounded-full transition"
            :class="modelValue[option.key] ? 'bg-cyan-400' : 'bg-slate-200'">
            <span
              class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition"
              :class="modelValue[option.key] ? 'translate-x-6' : 'translate-x-1'"
            />
          </button>
        </div>
      </div>
    </div>
    <div class="flex items-center justify-between">
      <label class="text-sm font-semibold text-slate-700">Table Seating Available</label>
      <button
        type="button"
        @click="update('table_seating', !modelValue.table_seating)"
        class="relative inline-flex h-6 w-11 items-center rounded-full transition"
        :class="modelValue.table_seating ? 'bg-cyan-400' : 'bg-slate-200'">
        <span
          class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition"
          :class="modelValue.table_seating ? 'translate-x-6' : 'translate-x-1'"
        />
      </button>
    </div>
    <div>
      <label class="block text-sm font-semibold text-slate-700 mb-1.5">Opening Hours</label>
      <input
        :value="modelValue.service_availability ?? ''"
        @input="update('service_availability', $event.target.value || null)"
        type="text" placeholder="e.g. Mon–Fri 11am–10pm, Sat–Sun 10am–11pm"
        class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-cyan-400"
      />
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: { type: Object, default: () => ({}) },
})
const emit = defineEmits(['update:modelValue'])

function update(key, value) {
  emit('update:modelValue', { ...props.modelValue, [key]: value })
}

const serviceOptions = [
  { key: 'has_dining',   label: 'Dine-in' },
  { key: 'has_take_out', label: 'Takeout' },
  { key: 'has_delivery', label: 'Delivery' },
]
</script>
