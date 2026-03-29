<template>
  <div class="rounded-3xl border border-slate-200 bg-white shadow-sm" :class="paddingClass">
    <slot />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  padding: {
    type: String,
    default: 'md',
  },
})

const paddingClass = computed(() => {
  if (props.padding === 'lg') return 'p-8'
  if (props.padding === 'sm') return 'p-4'
  return 'p-6'
})
</script>
