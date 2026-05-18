<template>
  <section class="grid overflow-hidden rounded-3xl border border-white/10 bg-white/10 shadow-2xl backdrop-blur-xl lg:grid-cols-2">
    <div class="hidden flex-col justify-between bg-gradient-to-br from-amber-300 via-cyan-300 to-emerald-300 p-10 text-slate-950 lg:flex">
      <div>
        <p class="text-sm font-semibold uppercase tracking-[0.3em] text-slate-800/70">
          Isle Be There
        </p>
        <h1 class="mt-6 max-w-md text-4xl font-bold leading-tight">
          Choose a new password and get back to your trip plans.
        </h1>
        <p class="mt-4 max-w-md text-base text-slate-800/80">
          This page uses the secure token from your reset email to update your password.
        </p>
      </div>

      <div class="rounded-2xl border border-slate-900/10 bg-white/40 p-5">
        <p class="text-sm font-medium text-slate-900">
          Use a strong password you haven't used elsewhere.
        </p>
      </div>
    </div>

    <div class="bg-white px-6 py-8 sm:px-10 sm:py-12">
      <div class="mx-auto w-full max-w-md">
        <div class="mb-8">
          <p class="text-sm font-semibold uppercase tracking-[0.25em] text-slate-500">
            Password reset
          </p>
          <h2 class="mt-3 text-3xl font-bold text-slate-900">
            Reset your password
          </h2>
          <p class="mt-2 text-sm text-slate-500">
            Enter your new password below to finish resetting your account.
          </p>
        </div>

        <form class="space-y-5" @submit.prevent="handleSubmit">
          <div>
            <div class="mb-2 flex items-center justify-between">
              <label for="password" class="block text-sm font-medium text-slate-700">
                New password
              </label>
              <span class="text-xs text-slate-400">Minimum 8 characters</span>
            </div>
            <div class="relative">
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                required
                autocomplete="new-password"
                placeholder="Create a new password"
                class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 pr-12 text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                tabindex="-1"
              >
                <svg v-if="!showPassword" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
              </button>
            </div>
          </div>

          <div>
            <label for="confirmPassword" class="mb-2 block text-sm font-medium text-slate-700">
              Confirm new password
            </label>
            <div class="relative">
              <input
                id="confirmPassword"
                v-model="confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                required
                autocomplete="new-password"
                placeholder="Repeat your new password"
                class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 pr-12 text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100"
              />
              <button
                type="button"
                @click="showConfirmPassword = !showConfirmPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                tabindex="-1"
              >
                <svg v-if="!showConfirmPassword" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
              </button>
            </div>
          </div>

          <div
            v-if="message"
            class="rounded-2xl border px-4 py-3 text-sm"
            :class="hasError ? 'border-red-200 bg-red-50 text-red-700' : 'border-emerald-200 bg-emerald-50 text-emerald-700'"
          >
            {{ message }}
          </div>

          <button
            type="submit"
            :disabled="loading || !hasToken"
            class="w-full rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <span v-if="loading">Resetting password...</span>
            <span v-else>Reset password</span>
          </button>
        </form>

        <div class="mt-6 flex flex-col gap-2 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between">
          <router-link to="/login" class="font-semibold text-cyan-600 hover:text-cyan-500">
            Back to sign in
          </router-link>
          <router-link to="/forgot-password" class="font-semibold text-slate-700 hover:text-slate-900">
            Request a new link
          </router-link>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authAPI } from '../services/api'
import { useToastStore } from '../stores/toast'

const route = useRoute()
const router = useRouter()
const toastStore = useToastStore()

const token = ref('')
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const loading = ref(false)
const hasError = ref(false)
const message = ref('')

const hasToken = computed(() => !!token.value)

async function handleSubmit() {
  message.value = ''
  hasError.value = false

  if (!hasToken.value) {
    hasError.value = true
    message.value = 'Missing reset token.'
    return
  }

  if (password.value !== confirmPassword.value) {
    hasError.value = true
    message.value = 'Passwords do not match.'
    return
  }

  loading.value = true

  try {
    const response = await authAPI.confirmPasswordReset({
      token: token.value,
      password: password.value,
    })
    message.value = response.data?.detail || 'Password updated successfully.'
    toastStore.show(message.value, 'success')
    window.setTimeout(() => {
      router.push('/login')
    }, 1500)
  } catch (err) {
    hasError.value = true
    message.value = err.response?.data?.detail || 'Unable to reset password.'
    toastStore.show(message.value, 'error')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const queryToken = route.query.token
  if (typeof queryToken === 'string' && queryToken.trim()) {
    token.value = queryToken.trim()
  } else {
    hasError.value = true
    message.value = 'Missing reset token.'
  }
})
</script>
