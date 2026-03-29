<template>
  <div class="rounded-3xl border border-slate-200 bg-white px-6 py-16 text-center shadow-sm">
    <div class="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl" :class="iconContainerClass">
      <slot name="icon">
        <span class="text-2xl">{{ icon }}</span>
      </slot>
    </div>
    <h2 class="mt-5 text-lg font-bold text-slate-900">{{ title }}</h2>
    <p v-if="description" class="mt-2 mx-auto max-w-md text-sm leading-6 text-slate-500">
      {{ description }}
    </p>
    <div v-if="$slots.actions" class="mt-6">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    default: '',
  },
  tone: {
    type: String,
    default: 'neutral',
  },
  icon: {
    type: String,
    default: '*',
  },
})

const iconContainerClass = computed(() => {
  if (props.tone === 'error') return 'bg-red-50 text-red-500'
  if (props.tone === 'success') return 'bg-emerald-50 text-emerald-500'
  return 'bg-slate-100 text-slate-400'
})
</script>
