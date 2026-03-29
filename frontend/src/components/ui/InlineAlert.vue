<template>
  <div
    class="rounded-2xl border px-4 py-3 text-sm"
    :class="toneClass"
    role="alert"
  >
    <slot>{{ message }}</slot>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  message: {
    type: String,
    default: '',
  },
  tone: {
    type: String,
    default: 'error',
  },
})

const toneClass = computed(() => {
  if (props.tone === 'success') return 'border-emerald-200 bg-emerald-50 text-emerald-800'
  if (props.tone === 'info') return 'border-cyan-200 bg-cyan-50 text-cyan-800'
  return 'border-red-200 bg-red-50 text-red-700'
})
</script>
