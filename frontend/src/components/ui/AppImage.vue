<template>
  <div class="relative overflow-hidden bg-slate-200" :class="wrapperClass">
    <img
      v-if="resolvedSrc && !failed"
      :src="resolvedSrc"
      :alt="alt"
      class="h-full w-full object-cover"
      :class="imgClass"
      @error="failed = true"
    />

    <div v-else class="flex h-full w-full items-center justify-center text-slate-400">
      <slot name="fallback">
        <div class="text-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <p v-if="fallbackLabel" class="mt-2 text-xs font-medium">{{ fallbackLabel }}</p>
        </div>
      </slot>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  src: {
    type: String,
    default: '',
  },
  alt: {
    type: String,
    default: '',
  },
  wrapperClass: {
    type: String,
    default: '',
  },
  imgClass: {
    type: String,
    default: '',
  },
  fallbackLabel: {
    type: String,
    default: '',
  },
})

const failed = ref(false)
const resolvedSrc = computed(() => props.src || '')

watch(
  () => props.src,
  () => {
    failed.value = false
  }
)
</script>
