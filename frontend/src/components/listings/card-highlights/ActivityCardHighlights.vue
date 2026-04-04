<template>
  <div class="mb-4 flex flex-wrap items-center gap-2">
    <span v-if="details.difficulty_level" class="rounded-full px-2.5 py-0.5 text-xs font-medium" :class="difficultyClass">
      {{ details.difficulty_level }}
    </span>

    <span v-if="details.is_indoor != null" class="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600">
      {{ details.is_indoor ? 'Indoor' : 'Outdoor' }}
    </span>

    <span v-if="details.estimated_duration" class="rounded-full bg-violet-50 px-2.5 py-0.5 text-xs font-medium text-violet-700">
      {{ details.estimated_duration }} {{ details.estimated_duration === 1 ? 'hr' : 'hrs' }}
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  details: {
    type: Object,
    default: () => ({}),
  },
})

const difficultyClass = computed(() => {
  switch (props.details.difficulty_level?.toLowerCase()) {
    case 'beginner':     return 'bg-emerald-50 text-emerald-700'
    case 'intermediate': return 'bg-amber-50 text-amber-700'
    case 'expert':       return 'bg-red-50 text-red-600'
    default:             return 'bg-slate-100 text-slate-600'
  }
})
</script>
