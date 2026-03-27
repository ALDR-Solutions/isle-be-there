<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 px-4 backdrop-blur-sm"
    @click.self="handleBackdropClick">

    <div class="relative flex max-h-[90vh] w-full max-w-4xl flex-col overflow-hidden rounded-[2rem] border border-white/10 bg-white shadow-2xl transition-all duration-300">
      <div class="absolute inset-x-0 top-0 h-32 bg-gradient-to-r from-cyan-100 via-white to-emerald-100 pointer-events-none"></div>

      <!-- Header -->
      <div class="relative flex items-start justify-between border-b border-slate-200 px-6 py-5 sm:px-8">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-600">
            {{ skipMode ? 'Skip personalization' : 'Personalize' }}
          </p>
          <h3 class="mt-2 text-2xl font-bold text-slate-900">
            {{ skipMode ? 'How would you like to continue?' : 'Tell us your interests' }}
          </h3>
          <p class="mt-2 text-sm text-slate-500">
            {{ skipMode
              ? 'You can always update your interests later from your profile.'
              : 'Select what you enjoy so we can tailor your recommended destinations.' }}
          </p>
        </div>

        <button
          @click="handleXClose"
          class="rounded-xl p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="relative flex-1 overflow-y-auto px-6 py-6 sm:px-8">

        <div v-if="skipMode" class="flex flex-col gap-4 py-2">
          <label class="cursor-pointer">
            <input v-model="skipOption" type="radio" value="remind" class="peer sr-only" />
            <div
              class="flex items-start gap-5 rounded-2xl border-2 border-slate-200 bg-slate-50 p-6 transition-all hover:border-slate-300 peer-checked:border-cyan-500 peer-checked:bg-cyan-50">
              <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-cyan-100 text-cyan-600">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p class="font-semibold text-slate-900">Remind me next time</p>
                <p class="mt-1 text-sm leading-6 text-slate-500">
                  This prompt will appear again. You can set your interests then.
                </p>
              </div>
              <div
                class="ml-auto mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full border-2 border-slate-300 transition peer-checked:border-cyan-500 peer-checked:bg-cyan-500">
                <svg v-if="skipOption === 'remind'" xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 text-white" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
          </label>

          <label class="cursor-pointer">
            <input v-model="skipOption" type="radio" value="never" class="peer sr-only" />
            <div
              class="flex items-start gap-5 rounded-2xl border-2 border-slate-200 bg-slate-50 p-6 transition-all hover:border-slate-300 peer-checked:border-slate-900 peer-checked:bg-slate-900/5">
              <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-600">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                </svg>
              </div>
              <div>
                <p class="font-semibold text-slate-900">Don't show me again</p>
                <p class="mt-1 text-sm leading-6 text-slate-500">
                  Skip personalization permanently. Your recommended destinations will be shown at random.
                </p>
              </div>
              <div
                class="ml-auto mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full border-2 border-slate-300 transition peer-checked:border-slate-900 peer-checked:bg-slate-900">
                <svg v-if="skipOption === 'never'" xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 text-white" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>
          </label>
        </div>
        <div v-else>
          <div class="mb-6 flex items-center justify-between gap-4">
            <p class="text-sm font-medium text-slate-500">
              Step <span class="font-bold text-slate-900">{{ currentStep + 1 }}</span> of {{ categories.length || 1 }}
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

          <div v-if="loadingInterests" class="py-16 text-center">
            <div class="inline-block h-8 w-8 animate-spin rounded-full border-4 border-slate-200 border-t-cyan-500"></div>
            <p class="mt-4 text-sm text-slate-400">Loading interests...</p>
          </div>

          <div
            v-else-if="categories.length === 0"
            class="rounded-3xl border border-slate-200 bg-slate-50 px-6 py-10 text-center text-slate-500">
            No interests available right now.
          </div>

          <transition v-else :name="slideDirection" mode="out-in">
            <div :key="currentStep">
              <div class="mb-6 rounded-2xl border border-cyan-100 bg-gradient-to-r from-cyan-50 to-emerald-50 px-5 py-4">
                <p class="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-600">Category {{ currentStep + 1 }}</p>
                <h4 class="mt-1 text-xl font-bold text-slate-900 capitalize">{{ categories[currentStep] }}</h4>
                <p class="mt-1 text-sm text-slate-500">Pick as many as you like — or skip this category.</p>
              </div>

              <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                <label
                  v-for="interest in categorized[categories[currentStep]]"
                  :key="interest.id"
                  class="cursor-pointer">
                  <input v-model="selected" type="checkbox" :value="interest.id" class="peer sr-only" />
                  <div
                    class="flex items-center justify-between gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-4 text-sm font-medium text-slate-700 shadow-sm transition hover:border-cyan-300 hover:bg-cyan-50 peer-checked:border-cyan-500 peer-checked:bg-cyan-50 peer-checked:text-cyan-700">
                    <span>{{ interest.name }}</span>
                    <span
                      class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full border border-current text-[10px] opacity-40 transition peer-checked:opacity-100"
                    >✓</span>
                  </div>
                </label>
              </div>

              <p v-if="selected.length > 0" class="mt-5 text-sm text-slate-500">
                <span class="font-semibold text-slate-900">{{ selected.length }}</span>
                {{ selected.length === 1 ? 'interest' : 'interests' }} selected across all categories.
              </p>
            </div>
          </transition>
        </div>
      </div>

      <div class="flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 bg-slate-50 px-6 py-4 sm:px-8">

        <template v-if="skipMode">
          <button
            @click="skipMode = false"
            class="rounded-2xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100">
            ← Back
          </button>
          <button
            @click="confirmSkip"
            :disabled="saving"
            class="rounded-2xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50">
            <span v-if="saving">Saving...</span>
            <span v-else>Confirm</span>
          </button>
        </template>

        <template v-else>
          <button
            v-show="currentStep > 0"
            @click="slideDirection = 'slide-right'; currentStep--"
            class="rounded-2xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100">
            Previous
          </button>
          <div v-show="currentStep === 0"></div>

          <div class="flex flex-wrap items-center gap-3">
            <button
              @click="skipMode = true"
              class="rounded-2xl px-5 py-3 text-sm font-semibold text-slate-500 transition hover:bg-slate-200 hover:text-slate-700">
              Skip for now
            </button>

            <button
              @click="next"
              :disabled="saving"
              class="rounded-2xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:opacity-50">
              <span v-if="saving">Saving...</span>
              <span v-else>{{ currentStep === categories.length - 1 ? 'Save Interests' : 'Next Category →' }}</span>
            </button>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { interestsAPI, profileAPI } from '../services/api'

const emit = defineEmits(['close', 'interests-saved'])

const allInterests = ref([])
const selected = ref([])
const currentStep = ref(0)
const loadingInterests = ref(true)
const skipMode = ref(false)
const skipOption = ref('remind')
const saving = ref(false)

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

const slideDirection = ref('slide-left')

async function next() {
  if (currentStep.value < categories.value.length - 1) {
    slideDirection.value = 'slide-left'
    currentStep.value++
    return
  }
  saving.value = true
  try {
    if (selected.value.length > 0) {
      await interestsAPI.updateUserInterests(selected.value)
    }
    await profileAPI.setInterestsHandled()
    emit('interests-saved')
  } catch (e) {
    console.error('Failed to save interests', e)
  } finally {
    saving.value = false
  }
  emit('close')
}

async function confirmSkip() {
  saving.value = true
  try {
    if (skipOption.value === 'never') {
      await profileAPI.setInterestsHandled()
    }
  } catch (e) {
    console.error('Failed to update skip preference', e)
  } finally {
    saving.value = false
  }
  emit('close')
}

function handleXClose() {
  emit('close')
}

function handleBackdropClick() {
  emit('close')
}
</script>

<style scoped>
.slide-left-enter-active,
.slide-left-leave-active,
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.28s ease;
}

.slide-left-enter-from  { opacity: 0; transform: translateX(40px); }
.slide-left-leave-to    { opacity: 0; transform: translateX(-40px); }
.slide-right-enter-from { opacity: 0; transform: translateX(-40px); }
.slide-right-leave-to   { opacity: 0; transform: translateX(40px); }
</style>
