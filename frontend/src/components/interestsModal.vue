<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 px-4 backdrop-blur-sm"
    @click.self="$emit('close')"
  >
    <div class="relative flex max-h-[90vh] w-full max-w-4xl flex-col overflow-hidden rounded-[2rem] border border-white/10 bg-white shadow-2xl">
      <div class="absolute inset-x-0 top-0 h-32 bg-gradient-to-r from-cyan-100 via-white to-emerald-100"></div>

      <div class="relative flex items-start justify-between border-b border-slate-200 px-6 py-5 sm:px-8">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-600">
            Personalize
          </p>
          <h3 class="mt-2 text-2xl font-bold text-slate-900">
            Tell us your interests
          </h3>
          <p class="mt-2 text-sm text-slate-500">
            Select what you like so we can make your experience feel more relevant.
          </p>
        </div>

        <button
          @click="skip"
          class="rounded-xl p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="relative flex-1 overflow-y-auto px-6 py-6 sm:px-8">
        <div class="mb-6 flex items-center justify-between gap-4">
          <div>
            <p class="text-sm font-semibold text-slate-900">
              Category {{ currentStep + 1 }} of {{ categories.length || 1 }}
            </p>
            <p class="text-sm text-slate-500">
              {{ currentCategoryLabel }}
            </p>
          </div>

          <div class="min-w-[140px]">
            <div class="h-2 overflow-hidden rounded-full bg-slate-100">
              <div
                class="h-full rounded-full bg-slate-900 transition-all duration-300"
                :style="{ width: `${progressWidth}%` }"
              ></div>
            </div>
          </div>
        </div>

        <div v-if="loadingInterests" class="py-16 text-center text-slate-400">
          Loading interests...
        </div>

        <div v-else-if="categories.length === 0" class="rounded-3xl border border-slate-200 bg-slate-50 px-6 py-10 text-center text-slate-500">
          No interests available right now.
        </div>

        <div v-else>
          <div class="mb-6">
            <h4 class="text-lg font-bold text-slate-900">
              {{ categories[currentStep] }}
            </h4>
            <p class="mt-1 text-sm text-slate-500">
              Pick as many as you like.
            </p>
          </div>

          <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <label
              v-for="interest in categorized[categories[currentStep]]"
              :key="interest.id"
              class="cursor-pointer"
            >
              <input
                v-model="selected"
                type="checkbox"
                :value="interest.id"
                class="peer sr-only"
              />

              <div class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4 text-sm font-medium text-slate-700 transition hover:border-cyan-300 hover:bg-cyan-50 peer-checked:border-slate-900 peer-checked:bg-slate-900 peer-checked:text-white">
                <div class="flex items-center justify-between gap-3">
                  <span>{{ interest.name }}</span>
                  <span class="flex h-5 w-5 items-center justify-center rounded-full border border-current text-[10px] opacity-70">
                    ✓
                  </span>
                </div>
              </div>
            </label>
          </div>
        </div>
      </div>

      <div class="flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 bg-slate-50 px-6 py-4 sm:px-8">
        <button
          v-show="currentStep > 0"
          @click="currentStep--"
          class="rounded-2xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
        >
          Previous
        </button>

        <div v-show="currentStep === 0"></div>

        <div class="flex flex-wrap items-center gap-3">
          <button
            @click="skip"
            class="rounded-2xl px-5 py-3 text-sm font-semibold text-slate-500 transition hover:bg-slate-200 hover:text-slate-700"
          >
            Skip for now
          </button>

          <button
            @click="next"
            class="rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
          >
            {{ currentStep === categories.length - 1 ? 'Save Interests' : 'Next Category' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { interestsAPI } from '../services/api'

const emit = defineEmits(['close'])

const allInterests = ref([])
const selected = ref([])
const currentStep = ref(0)
const loadingInterests = ref(true)

onMounted(async () => {
  try {
    const res = await interestsAPI.getAll()
    allInterests.value = res.data
  } catch (e) {
    console.error('Failed to load interests', e)
  } finally {
    loadingInterests.value = false
  }
})

const categorized = computed(() => {
  const map = {}
  for (const i of allInterests.value) {
    const cat = i.category || 'Other'
    if (!map[cat]) map[cat] = []
    map[cat].push(i)
  }
  return map
})

const categories = computed(() => Object.keys(categorized.value))

const progressWidth = computed(() => {
  if (!categories.value.length) return 0
  return ((currentStep.value + 1) / categories.value.length) * 100
})

const currentCategoryLabel = computed(() => {
  if (!categories.value.length) return 'No categories available'
  return categories.value[currentStep.value]
})

async function next() {
  if (currentStep.value < categories.value.length - 1) {
    currentStep.value++
  } else {
    try {
      await interestsAPI.updateUserInterests(selected.value)
    } catch (e) {
      console.error('Failed to save interests', e)
    }
    emit('close')
  }
}

function skip() {
  emit('close')
}
</script>
