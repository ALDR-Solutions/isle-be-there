<template>
  <div class="flex items-center justify-center" :class="centered ? 'py-20' : ''">
    <svg
      class="animate-spin text-cyan-500"
      :class="sizeClass"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
    </svg>
    <span v-if="label" class="sr-only">{{ label }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  size: {
    type: String,
    default: 'md',
  },
  centered: {
    type: Boolean,
    default: true,
  },
  label: {
    type: String,
    default: 'Loading',
  },
})

const sizeClass = computed(() => {
  if (props.size === 'sm') return 'h-5 w-5'
  if (props.size === 'lg') return 'h-10 w-10'
  return 'h-8 w-8'
})
</script>
