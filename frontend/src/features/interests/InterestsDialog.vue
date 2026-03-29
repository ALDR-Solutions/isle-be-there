<template>
  <BaseDialog
    v-model="open"
    eyebrow="Personalize"
    title="Tell us your interests"
    description="Select what you enjoy so we can tailor your recommended destinations."
    max-width="lg"
    @update:modelValue="handleClose"
  >
    <div v-if="loading" class="py-8">
      <LoadingSpinner />
    </div>

    <div v-else-if="error">
      <InlineAlert :message="error.message" />
    </div>

    <div v-else-if="categories.length === 0">
      <PageStatus
        title="No interests available right now"
        description="You can still continue browsing listings."
        icon="[]"
      />
    </div>

    <div v-else>
      <div class="mb-6 flex items-center justify-between gap-4">
        <p class="text-sm font-medium text-slate-500">
          Step <span class="font-bold text-slate-900">{{ currentStep + 1 }}</span> of {{ categories.length }}
        </p>
        <div class="flex flex-1 items-center gap-2">
          <div class="h-2 flex-1 overflow-hidden rounded-full bg-slate-100">
            <div
              class="h-full rounded-full bg-gradient-to-r from-cyan-500 to-emerald-500 transition-all duration-500"
              :style="{ width: `${progressWidth}%` }"
            ></div>
          </div>
          <span class="text-xs font-semibold text-slate-400">{{ Math.round(progressWidth) }}%</span>
        </div>
      </div>

      <div class="mb-6 rounded-2xl border border-cyan-100 bg-gradient-to-r from-cyan-50 to-emerald-50 px-5 py-4">
        <p class="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-600">Category {{ currentStep + 1 }}</p>
        <h4 class="mt-1 text-xl font-bold text-slate-900 capitalize">{{ categories[currentStep] }}</h4>
        <p class="mt-1 text-sm text-slate-500">Pick as many as you like, or skip this category.</p>
      </div>

      <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <label
          v-for="interest in categorized[categories[currentStep]]"
          :key="interest.id"
          class="cursor-pointer"
        >
          <input v-model="selected" type="checkbox" :value="interest.id" class="peer sr-only" />
          <div
            class="flex items-center justify-between gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-4 text-sm font-medium text-slate-700 shadow-sm transition hover:border-cyan-300 hover:bg-cyan-50 peer-checked:border-cyan-500 peer-checked:bg-cyan-50 peer-checked:text-cyan-700"
          >
            <span>{{ interest.name }}</span>
            <span
              class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full border border-current text-[10px] opacity-40 transition peer-checked:opacity-100"
            >
              v
            </span>
          </div>
        </label>
      </div>

      <p v-if="selected.length > 0" class="mt-5 text-sm text-slate-500">
        <span class="font-semibold text-slate-900">{{ selected.length }}</span>
        {{ selected.length === 1 ? 'interest' : 'interests' }} selected across all categories.
      </p>
    </div>

    <template #footer>
      <div class="flex flex-wrap items-center justify-between gap-3">
        <button
          v-if="currentStep > 0"
          type="button"
          class="rounded-2xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
          @click="currentStep -= 1"
        >
          Previous
        </button>
        <div v-else></div>

        <div class="flex flex-wrap items-center gap-3">
          <button
            type="button"
            class="rounded-2xl px-5 py-3 text-sm font-semibold text-slate-500 transition hover:bg-slate-200 hover:text-slate-700"
            @click="handleSkip"
          >
            Skip for now
          </button>
          <button
            type="button"
            class="rounded-2xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:opacity-50"
            :disabled="saving"
            @click="handleNext"
          >
            {{ saving ? 'Saving...' : currentStep === categories.length - 1 ? 'Save Interests' : 'Next Category' }}
          </button>
        </div>
      </div>
    </template>
  </BaseDialog>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import BaseDialog from '@/components/ui/BaseDialog.vue'
import InlineAlert from '@/components/ui/InlineAlert.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import PageStatus from '@/components/ui/PageStatus.vue'
import { useAsyncData } from '@/composables/useAsyncData'
import { interestsService } from '@/services/interestsService'
import { profileService } from '@/services/profileService'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue', 'interests-saved'])

const open = ref(props.modelValue)
const currentStep = ref(0)
const selected = ref([])
const saving = ref(false)

const state = useAsyncData(({ signal }) => interestsService.getAll({ signal }), {
  initialData: [],
})
const { error, loading } = state

watch(
  () => props.modelValue,
  (value) => {
    open.value = value
  }
)

const categorized = computed(() => {
  const map = {}

  for (const interest of state.data.value || []) {
    const category = interest.category || 'Other'
    if (!map[category]) {
      map[category] = []
    }
    map[category].push(interest)
  }

  return map
})

const categories = computed(() => Object.keys(categorized.value))
const progressWidth = computed(() => {
  if (!categories.value.length) return 0
  return ((currentStep.value + 1) / categories.value.length) * 100
})

onMounted(() => {
  state.load().catch(() => {})
})

function handleClose(value = false) {
  open.value = value
  emit('update:modelValue', value)
}

async function handleNext() {
  if (currentStep.value < categories.value.length - 1) {
    currentStep.value += 1
    return
  }

  saving.value = true

  try {
    if (selected.value.length > 0) {
      await interestsService.updateUserInterests(selected.value)
    }

    await profileService.setInterestsHandled()
    emit('interests-saved')
    handleClose(false)
  } finally {
    saving.value = false
  }
}

async function handleSkip() {
  saving.value = true

  try {
    await profileService.setInterestsHandled()
    emit('interests-saved')
    handleClose(false)
  } finally {
    saving.value = false
  }
}
</script>
