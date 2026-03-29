<template>
  <teleport to="body">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-50 flex items-center justify-center px-4"
      @click.self="handleBackdrop"
    >
      <div class="absolute inset-0 bg-slate-950/55 backdrop-blur-sm"></div>
      <div
        ref="panelRef"
        class="relative w-full rounded-[1.75rem] border border-slate-200 bg-white shadow-2xl"
        :class="maxWidthClass"
        tabindex="-1"
      >
        <div class="flex items-start justify-between gap-4 border-b border-slate-200 px-6 py-5">
          <div>
            <p v-if="eyebrow" class="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-600">
              {{ eyebrow }}
            </p>
            <h3 class="mt-1 text-xl font-bold text-slate-900">{{ title }}</h3>
            <p v-if="description" class="mt-2 text-sm leading-6 text-slate-500">{{ description }}</p>
          </div>

          <button
            type="button"
            class="rounded-xl p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
            @click="emit('update:modelValue', false)"
            aria-label="Close dialog"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="max-h-[75vh] overflow-y-auto px-6 py-6">
          <slot />
        </div>

        <div v-if="$slots.footer" class="border-t border-slate-200 bg-slate-50 px-6 py-4">
          <slot name="footer" />
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    default: '',
  },
  eyebrow: {
    type: String,
    default: '',
  },
  maxWidth: {
    type: String,
    default: 'md',
  },
  closeOnBackdrop: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['update:modelValue'])
const panelRef = ref(null)

const maxWidthClass = computed(() => {
  if (props.maxWidth === 'lg') return 'max-w-4xl'
  if (props.maxWidth === 'xl') return 'max-w-5xl'
  return 'max-w-md'
})

function handleBackdrop() {
  if (props.closeOnBackdrop) {
    emit('update:modelValue', false)
  }
}

function handleKeydown(event) {
  if (event.key === 'Escape' && props.modelValue) {
    emit('update:modelValue', false)
  }
}

watch(
  () => props.modelValue,
  async (isOpen) => {
    if (typeof document !== 'undefined') {
      document.body.style.overflow = isOpen ? 'hidden' : ''
    }

    if (isOpen) {
      await nextTick()
      panelRef.value?.focus()
    }
  },
  { immediate: true }
)

if (typeof window !== 'undefined') {
  window.addEventListener('keydown', handleKeydown)
}

onBeforeUnmount(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('keydown', handleKeydown)
  }

  if (typeof document !== 'undefined') {
    document.body.style.overflow = ''
  }
})
</script>
