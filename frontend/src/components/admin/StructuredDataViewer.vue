<template>
  <div class="space-y-3">
    <template v-if="isScalar(value)">
      <p class="text-sm text-slate-700">{{ formatValue(value) }}</p>
    </template>

    <template v-else-if="isPrimitiveArray(value)">
      <div class="flex flex-wrap gap-2">
        <span
          v-for="(item, index) in value"
          :key="`${String(item)}-${index}`"
          class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
          {{ formatValue(item) }}
        </span>
      </div>
    </template>

    <template v-else-if="Array.isArray(value)">
      <div class="space-y-3">
        <div
          v-for="(item, index) in value"
          :key="index"
          class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
            Item {{ index + 1 }}
          </p>
          <div class="mt-3">
            <StructuredDataViewer :value="item" />
          </div>
        </div>
      </div>
    </template>

    <template v-else-if="isObject(value)">
      <div v-if="objectEntries.length" class="space-y-3">
        <div
          v-for="[key, nestedValue] in objectEntries"
          :key="key"
          class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
            {{ formatKey(key) }}
          </p>
          <div class="mt-3">
            <template v-if="isScalar(nestedValue)">
              <p class="text-sm text-slate-700">{{ formatValue(nestedValue) }}</p>
            </template>
            <template v-else>
              <StructuredDataViewer :value="nestedValue" />
            </template>
          </div>
        </div>
      </div>
      <p v-else class="text-sm text-slate-400">No data provided.</p>
    </template>

    <template v-else>
      <p class="text-sm text-slate-400">No data provided.</p>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'

defineOptions({
  name: 'StructuredDataViewer',
})

const props = defineProps({
  value: {
    type: [Object, Array, String, Number, Boolean],
    default: null,
  },
})

const objectEntries = computed(() => {
  if (!isObject(props.value)) return []
  return Object.entries(props.value).filter(([, nestedValue]) => nestedValue !== undefined)
})

function isScalar(value) {
  return (
    value === null ||
    value === undefined ||
    typeof value === 'string' ||
    typeof value === 'number' ||
    typeof value === 'boolean'
  )
}

function isObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
}

function isPrimitiveArray(value) {
  return Array.isArray(value) && value.every((item) => isScalar(item))
}

function formatKey(value) {
  return String(value)
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

function formatValue(value) {
  if (value === null || value === undefined || value === '') return '-'
  if (typeof value === 'boolean') return value ? 'Yes' : 'No'
  return String(value)
}
</script>
