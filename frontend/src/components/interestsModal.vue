<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-2xl mx-4 max-h-[90vh] flex flex-col">
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b">
        <h3 class="text-lg font-semibold">Tell us your interests</h3>
        <button @click="skip" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">&times;</button>
      </div>

      <!-- Body -->
      <div class="px-6 py-4 overflow-y-auto flex-1">
        <p class="text-gray-600 mb-4">Select your interests to help us personalize your experience</p>

        <div v-if="loadingInterests" class="text-center py-4 text-gray-400">Loading...</div>
        <div v-else>
          <div v-for="(items, category) in categorized" :key="category" v-show="categories[currentStep] === category">
            <h4 class="font-semibold uppercase text-sm text-gray-700 mb-3">{{ category }}</h4>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-2">
              <label
                v-for="interest in items"
                :key="interest.id"
                class="cursor-pointer"
              >
                <input type="checkbox" :value="interest.id" v-model="selected" class="hidden peer" />
                <div class="border rounded-lg px-4 py-2 text-center text-sm font-medium transition
                  peer-checked:bg-teal-700 peer-checked:text-white peer-checked:border-teal-700
                  hover:border-teal-500">
                  {{ interest.name }}
                </div>
              </label>
            </div>
          </div>
        </div>

        <p class="text-center text-gray-400 text-sm mt-4">
          Category {{ currentStep + 1 }} of {{ categories.length }}
        </p>
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-between px-6 py-4 border-t">
        <button
          v-show="currentStep > 0"
          @click="currentStep--"
          class="px-4 py-2 border rounded-md text-gray-600 hover:bg-gray-50"
        >Previous</button>
        <div v-show="currentStep === 0"></div>

        <div class="flex gap-2">
          <button @click="skip" class="px-4 py-2 bg-gray-200 rounded-md hover:bg-gray-300">Skip</button>
          <button
            @click="next"
            class="px-4 py-2 bg-teal-700 text-white rounded-md hover:bg-teal-800"
          >
            {{ currentStep === categories.length - 1 ? 'Save' : 'Next' }}
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