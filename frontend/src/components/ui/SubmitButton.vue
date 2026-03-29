<template>
  <button
    type="submit"
    class="rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
    :class="fullWidth ? 'w-full' : ''"
    :disabled="disabled || loading"
  >
    {{ loading ? loadingLabel : label }}
  </button>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    required: true,
  },
  loadingLabel: {
    type: String,
    default: 'Saving...',
  },
  loading: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  fullWidth: {
    type: Boolean,
    default: false,
  },
})
</script>
