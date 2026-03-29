<template>
  <span class="rounded-xl px-3 py-1 text-xs font-semibold" :class="toneClass">
    {{ label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: {
    type: String,
    required: true,
  },
  tone: {
    type: String,
    default: 'neutral',
  },
})

const toneClass = computed(() => {
  if (props.tone === 'success') return 'bg-emerald-500 text-white'
  if (props.tone === 'warning') return 'bg-amber-400 text-slate-900'
  if (props.tone === 'danger') return 'bg-red-500 text-white'
  if (props.tone === 'info') return 'bg-cyan-100 text-cyan-700'
  return 'bg-slate-200 text-slate-700'
})
</script>
