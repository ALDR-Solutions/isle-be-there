<template>
  <section class="grid overflow-hidden rounded-3xl border border-white/10 bg-white/10 shadow-2xl backdrop-blur-xl lg:grid-cols-[0.9fr_1.1fr]">

    <!-- Left panel -->
    <div class="hidden flex-col justify-between bg-gradient-to-br from-cyan-400 via-teal-300 to-emerald-300 p-8 text-slate-950 lg:flex">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-800/70">Isle Be There</p>
        <h1 class="mt-4 max-w-sm text-3xl font-bold leading-tight">
          <template v-if="step === 0">Welcome. How would you like to get started?</template>
          <template v-else-if="accountType === 'business' && step === 2">Add your first listing and start accepting bookings.</template>
          <template v-else-if="accountType === 'business'">List your property on Isle Be There.</template>
          <template v-else>Create an account and keep every trip in one place.</template>
        </h1>
        <p class="mt-3 max-w-sm text-sm leading-6 text-slate-800/80">
          <template v-if="accountType === 'business'">Manage listings, track bookings, and grow your island business.</template>
          <template v-else>Save favourites, manage bookings, and personalize your travel experience.</template>
        </p>
      </div>
      <div class="rounded-2xl border border-slate-900/10 bg-white/40 p-4">
        <p class="text-sm font-medium text-slate-900">
          <template v-if="accountType === 'business'">Business accounts can manage multiple listings from one dashboard.</template>
          <template v-else>Join as a traveler or use a business account to manage listings.</template>
        </p>
      </div>
    </div>

    <!-- Right panel -->
    <div class="bg-white px-6 py-6 sm:px-8 lg:px-10">
      <div class="mx-auto w-full max-w-xl">

        <!-- Step 0: Account type selection -->
        <div v-if="step === 0">
          <div class="mb-8">
            <p class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">Get started</p>
            <h2 class="mt-2 text-2xl font-bold text-slate-900">Create your account</h2>
            <p class="mt-1 text-sm text-slate-500">Choose how you'd like to use Isle Be There.</p>
          </div>

          <div class="grid gap-4 sm:grid-cols-2">
            <button
              @click="selectAccountType('traveler')"
              class="group flex flex-col items-start gap-3 rounded-2xl border-2 border-slate-200 bg-white p-6 text-left transition hover:border-cyan-400 hover:bg-cyan-50"
            >
              <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 transition group-hover:bg-cyan-100">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-slate-600 transition group-hover:text-cyan-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p class="text-base font-bold text-slate-900">Traveler</p>
                <p class="mt-1 text-sm text-slate-500">Explore stays, save favourites, and manage bookings.</p>
              </div>
            </button>

            <button
              @click="selectAccountType('business')"
              class="group flex flex-col items-start gap-3 rounded-2xl border-2 border-slate-200 bg-white p-6 text-left transition hover:border-cyan-400 hover:bg-cyan-50"
            >
              <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 transition group-hover:bg-cyan-100">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-slate-600 transition group-hover:text-cyan-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <div>
                <p class="text-base font-bold text-slate-900">Business Owner</p>
                <p class="mt-1 text-sm text-slate-500">List your property and manage bookings and services.</p>
              </div>
            </button>
          </div>

          <p class="mt-6 text-center text-sm text-slate-500">
            Already have an account?
            <router-link to="/login" class="font-semibold text-cyan-600 hover:text-cyan-500">Sign in</router-link>
          </p>
        </div>

        <!-- Step 1: Account details -->
        <div v-if="step === 1">
          <div class="mb-6 flex items-center gap-3">
            <button @click="step = 0" class="flex h-8 w-8 items-center justify-center rounded-xl border border-slate-200 text-slate-500 transition hover:bg-slate-50">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">
                {{ accountType === 'business' ? 'Step 1 of 2 · Business Account' : 'Get started' }}
              </p>
              <h2 class="mt-0.5 text-2xl font-bold text-slate-900">Create your account</h2>
            </div>
          </div>

          <form class="space-y-4" @submit.prevent="handleRegister">
            <div class="grid gap-4 sm:grid-cols-2">
              <div>
                <label for="firstName" class="mb-1.5 block text-sm font-medium text-slate-700">First name</label>
                <input id="firstName" v-model="firstName" type="text" required autocomplete="given-name" placeholder="Lee"
                  class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100" />
              </div>
              <div>
                <label for="lastName" class="mb-1.5 block text-sm font-medium text-slate-700">Last name</label>
                <input id="lastName" v-model="lastName" type="text" required autocomplete="family-name" placeholder="Chong"
                  class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100" />
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div>
                <label for="email" class="mb-1.5 block text-sm font-medium text-slate-700">Email</label>
                <input id="email" v-model="email" type="email" required autocomplete="email" placeholder="you@example.com"
                  class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100" />
              </div>
              <div>
                <label for="username" class="mb-1.5 block text-sm font-medium text-slate-700">Username</label>
                <input id="username" v-model="username" type="text" required autocomplete="username" placeholder="leechong"
                  class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100" />
              </div>
            </div>

            <div>
              <div class="mb-1.5 flex items-center justify-between">
                <label for="password" class="block text-sm font-medium text-slate-700">Password</label>
                <span class="text-xs text-slate-400">Choose a strong password</span>
              </div>
              <div class="relative">
                <input id="password" v-model="password" :type="showPassword ? 'text' : 'password'" required autocomplete="new-password" placeholder="Create a password"
                  class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 pr-11 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100" />
                <button type="button" @click="showPassword = !showPassword" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600" tabindex="-1">
                  <svg v-if="!showPassword" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                </button>
              </div>
            </div>

            <div>
              <label for="confirmPassword" class="mb-1.5 block text-sm font-medium text-slate-700">Confirm password</label>
              <div class="relative">
                <input id="confirmPassword" v-model="confirmPassword" :type="showConfirmPassword ? 'text' : 'password'" required autocomplete="new-password" placeholder="Repeat your password"
                  class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 pr-11 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100" />
                <button type="button" @click="showConfirmPassword = !showConfirmPassword" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600" tabindex="-1">
                  <svg v-if="!showConfirmPassword" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                </button>
              </div>
            </div>

            <div v-if="error" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {{ error }}
            </div>

            <button type="submit" :disabled="loading"
              class="w-full rounded-xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60">
              <span v-if="loading">Creating account...</span>
              <span v-else>{{ accountType === 'business' ? 'Continue' : 'Create account' }}</span>
            </button>
          </form>

          <p class="mt-4 text-center text-sm text-slate-500">
            Already have an account?
            <router-link to="/login" class="font-semibold text-cyan-600 hover:text-cyan-500">Sign in</router-link>
          </p>
        </div>

        <!-- Step 2: First listing (business only) -->
        <div v-if="step === 2">
          <div class="mb-6 flex items-center gap-3">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">Step 2 of 2 · Your First Listing</p>
              <h2 class="mt-0.5 text-2xl font-bold text-slate-900">Add your first listing</h2>
              <p class="mt-1 text-sm text-slate-500">You can update all details later from your dashboard.</p>
            </div>
          </div>

          <form class="space-y-4" @submit.prevent="handleCreateListing">
            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700">Listing name <span class="text-red-500">*</span></label>
              <input v-model="listingTitle" type="text" required placeholder="e.g. Beachfront Villa"
                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100" />
            </div>

            <div v-if="businessTypes.length">
              <label class="mb-1.5 block text-sm font-medium text-slate-700">Type <span class="text-red-500">*</span></label>
              <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
                <button
                  v-for="type in businessTypes" :key="type.id" type="button"
                  @click="listingType = type.id"
                  class="rounded-xl border py-2.5 text-xs font-semibold transition"
                  :class="listingType === type.id ? 'border-cyan-400 bg-cyan-50 text-cyan-700' : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'"
                >{{ type.name }}</button>
              </div>
            </div>

            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700">Description <span class="text-red-500">*</span></label>
              <textarea v-model="listingDescription" rows="3" required placeholder="Briefly describe your listing..."
                class="w-full resize-none rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100"></textarea>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div>
                <label class="mb-1.5 block text-sm font-medium text-slate-700">City <span class="text-red-500">*</span></label>
                <input v-model="listingCity" type="text" required placeholder="e.g. Bridgetown"
                  class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100" />
              </div>
              <div>
                <label class="mb-1.5 block text-sm font-medium text-slate-700">Country / Island <span class="text-red-500">*</span></label>
                <input v-model="listingCountry" type="text" required placeholder="e.g. Barbados"
                  class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100" />
              </div>
            </div>

            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700">Base price (USD) <span class="text-red-500">*</span></label>
              <div class="relative">
                <span class="absolute left-4 top-1/2 -translate-y-1/2 text-sm font-semibold text-slate-400">$</span>
                <input v-model="listingPrice" type="number" min="0" step="0.01" required placeholder="0.00"
                  class="w-full rounded-xl border border-slate-200 bg-slate-50 pl-8 pr-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100" />
              </div>
            </div>

            <div v-if="listingError" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {{ listingError }}
            </div>

            <div class="flex gap-3">
              <button type="button" @click="skipListing"
                class="flex-1 rounded-xl border border-slate-200 py-3 text-sm font-semibold text-slate-600 transition hover:bg-slate-50">
                Skip for now
              </button>
              <button type="submit" :disabled="listingLoading"
                class="flex-1 rounded-xl bg-slate-900 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60">
                <span v-if="listingLoading">Creating...</span>
                <span v-else>Create listing</span>
              </button>
            </div>
          </form>
        </div>

      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'
import { listingsAPI, businessesAPI } from '../services/api'

const router = useRouter()
const authStore = useAuthStore()
const toastStore = useToastStore()

// Step state
const step = ref(0)
const accountType = ref(null) // 'traveler' | 'business'

// Step 1 fields
const firstName = ref('')
const lastName = ref('')
const email = ref('')
const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const error = ref('')
const loading = ref(false)

// Step 2 fields
const listingTitle = ref('')
const listingType = ref('')
const listingDescription = ref('')
const listingCity = ref('')
const listingCountry = ref('')
const listingPrice = ref('')
const listingError = ref('')
const listingLoading = ref(false)
const businessTypes = ref([])

function selectAccountType(type) {
  accountType.value = type
  step.value = 1
}

async function fetchBusinessTypes() {
  try {
    const response = await businessesAPI.getTypes()
    businessTypes.value = response.data
  } catch (e) {
    console.error('Failed to load business types', e)
  }
}

onMounted(() => {
  fetchBusinessTypes()
})

async function handleRegister() {
  error.value = ''
  loading.value = true

  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    loading.value = false
    return
  }

  const success = await authStore.register({
    email: email.value,
    password: password.value,
    username: username.value,
    first_name: firstName.value,
    last_name: lastName.value,
    user_type: accountType.value === 'business' ? 'business' : 'regular',
  })

  if (success) {
    toastStore.show('Account created successfully.', 'success')
    if (accountType.value === 'business') {
      step.value = 2
    } else {
      router.push('/')
    }
  } else {
    error.value = authStore.error || 'Registration failed'
    toastStore.show(error.value, 'error')
  }

  loading.value = false
}

async function handleCreateListing() {
  listingError.value = ''
  if (!listingTitle.value.trim()) { listingError.value = 'Listing name is required.'; return }
  if (!listingType.value) { listingError.value = 'Please select a listing type.'; return }
  if (!listingDescription.value.trim()) { listingError.value = 'Description is required.'; return }
  if (!listingCity.value.trim()) { listingError.value = 'City is required.'; return }
  if (!listingCountry.value.trim()) { listingError.value = 'Country is required.'; return }
  if (!listingPrice.value || Number(listingPrice.value) <= 0) { listingError.value = 'Please enter a valid price.'; return }

  listingLoading.value = true
  try {
    await listingsAPI.create({
      title: listingTitle.value.trim(),
      business_type: listingType.value,
      description: listingDescription.value.trim(),
      base_price: Number(listingPrice.value),
      address: { city: listingCity.value.trim(), country: listingCountry.value.trim() },
    })
    toastStore.show('Listing created! Welcome to your dashboard.', 'success')
    router.push('/business')
  } catch (e) {
    listingError.value = e.response?.data?.detail || 'Failed to create listing.'
    toastStore.show(listingError.value, 'error')
  } finally {
    listingLoading.value = false
  }
}

function skipListing() {
  router.push('/business')
}
</script>
