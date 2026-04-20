<template>
  <section class="mx-auto w-full max-w-5xl overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-xl shadow-slate-900/5">
    <div class="border-b border-slate-200 bg-slate-50 px-5 py-5 sm:px-8">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div class="min-w-0">
          <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-600">
            {{ eyebrow }}
          </p>
          <h1 class="mt-2 text-2xl font-bold text-slate-950 sm:text-3xl">
            {{ title }}
          </h1>
          <p v-if="description" class="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
            {{ description }}
          </p>
        </div>

        <div class="w-full shrink-0 lg:w-72">
          <div class="mb-2 flex items-center justify-between text-xs font-semibold text-slate-500">
            <span>Step {{ currentStep + 1 }} of {{ totalSteps }}</span>
            <span>{{ Math.round(progressWidth) }}%</span>
          </div>
          <div class="h-2 overflow-hidden rounded-full bg-slate-200">
            <div
              class="h-full rounded-full bg-cyan-500 transition-all duration-300"
              :style="{ width: `${progressWidth}%` }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <div class="min-h-[420px] px-5 py-6 sm:px-8 sm:py-8">
      <slot />
    </div>

    <div class="flex flex-col gap-3 border-t border-slate-200 bg-slate-50 px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-8">
      <p class="min-h-5 text-sm font-medium text-red-600">
        {{ error || '' }}
      </p>

      <div class="flex flex-col-reverse gap-3 sm:flex-row sm:items-center">
        <button
          type="button"
          :disabled="!canGoBack || busy"
          class="inline-flex items-center justify-center rounded-2xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40"
          @click="$emit('back')"
        >
          Back
        </button>

        <button
          type="button"
          :disabled="nextDisabled || busy"
          class="inline-flex items-center justify-center rounded-2xl bg-slate-950 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
          @click="$emit('next')"
        >
          <svg
            v-if="busy"
            class="mr-2 h-4 w-4 animate-spin"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
          </svg>
          {{ busy ? busyLabel : nextLabel }}
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  eyebrow: {
    type: String,
    default: 'Plan your trip',
  },
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    default: '',
  },
  currentStep: {
    type: Number,
    required: true,
  },
  totalSteps: {
    type: Number,
    required: true,
  },
  canGoBack: {
    type: Boolean,
    default: false,
  },
  nextDisabled: {
    type: Boolean,
    default: false,
  },
  nextLabel: {
    type: String,
    default: 'Next',
  },
  busyLabel: {
    type: String,
    default: 'Working...',
  },
  busy: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: '',
  },
})

defineEmits(['back', 'next'])

const progressWidth = computed(() => {
  if (!props.totalSteps) return 0
  return ((props.currentStep + 1) / props.totalSteps) * 100
})
</script>
