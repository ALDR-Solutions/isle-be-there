<template>
  <div
    class="pointer-events-none fixed right-4 top-4 z-[100] flex w-full max-w-sm flex-col gap-3"
    aria-live="polite"
    aria-atomic="true"
  >
    <transition-group name="toast">
      <div
        v-for="toast in toastStore.toasts"
        :key="toast.id"
        class="pointer-events-auto overflow-hidden rounded-2xl border shadow-xl backdrop-blur-md"
        :class="toastClasses(toast.type)"
      >
        <div class="flex items-start justify-between gap-3 px-4 py-4">
          <div>
            <p class="text-sm font-semibold">{{ toastTitle(toast.type) }}</p>
            <p class="mt-1 text-sm">{{ toast.message }}</p>
          </div>

          <button
            @click="toastStore.remove(toast.id)"
            class="rounded-lg p-1 opacity-70 transition hover:bg-black/5 hover:opacity-100"
          >
            Close
          </button>
        </div>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()

const toastClasses = (type) => {
  if (type === 'success') {
    return 'border-emerald-200 bg-emerald-50 text-emerald-900'
  }

  if (type === 'error') {
    return 'border-red-200 bg-red-50 text-red-900'
  }

  return 'border-slate-200 bg-white text-slate-900'
}

const toastTitle = (type) => {
  if (type === 'success') return 'Success'
  if (type === 'error') return 'Error'
  return 'Notice'
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.25s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
