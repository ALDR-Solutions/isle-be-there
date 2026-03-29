<template>
  <div class="bg-white border-b border-slate-200">
    <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <div class="flex flex-col gap-6 sm:flex-row sm:items-end sm:justify-between">
        <div class="max-w-2xl">
          <p v-if="eyebrow" class="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-600">
            {{ eyebrow }}
          </p>
          <h1 class="mt-3 text-3xl font-bold text-slate-900 sm:text-4xl">
            {{ title }}
          </h1>
          <p v-if="description" class="mt-3 text-base leading-7 text-slate-600">
            {{ description }}
          </p>
        </div>

        <div v-if="$slots.actions" class="shrink-0">
          <slot name="actions" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  eyebrow: {
    type: String,
    default: '',
  },
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    default: '',
  },
})
</script>
