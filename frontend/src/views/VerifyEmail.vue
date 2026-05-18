<template>
  <section class="grid overflow-hidden rounded-3xl border border-white/10 bg-white/10 shadow-2xl backdrop-blur-xl lg:grid-cols-[0.95fr_1.05fr]">
    <div class="hidden flex-col justify-between bg-gradient-to-br from-cyan-400 via-teal-300 to-emerald-300 p-10 text-slate-950 lg:flex">
      <div>
        <p class="text-sm font-semibold uppercase tracking-[0.3em] text-slate-800/70">
          Isle Be There
        </p>
        <h1 class="mt-6 max-w-md text-4xl font-bold leading-tight">
          Verifying your account so you can get back to planning.
        </h1>
        <p class="mt-4 max-w-md text-base text-slate-800/80">
          This page only handles the verification link from your email and will send you to sign in when it succeeds.
        </p>
      </div>

      <div class="rounded-2xl border border-slate-900/10 bg-white/40 p-5">
        <p class="text-sm font-medium text-slate-900">
          Use the newest verification email if you requested more than one link.
        </p>
      </div>
    </div>

    <div class="bg-white px-6 py-8 sm:px-10 sm:py-12">
      <div class="mx-auto w-full max-w-lg space-y-6">
        <div>
          <p class="text-sm font-semibold uppercase tracking-[0.25em] text-slate-500">
            Email verification
          </p>
          <h2 class="mt-3 text-3xl font-bold text-slate-900">
            {{ heading }}
          </h2>
          <p class="mt-2 text-sm leading-6 text-slate-500">
            {{ description }}
          </p>
        </div>

        <div class="rounded-3xl border px-5 py-5" :class="panelClasses">
          <div class="flex items-start gap-4">
            <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl" :class="badgeClasses">
              <svg v-if="status === 'loading'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <svg v-else-if="status === 'success'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M5 13l4 4L19 7" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 9v4m0 4h.01M5.07 19h13.86c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.73 3z" />
              </svg>
            </div>

            <div class="min-w-0">
              <p class="text-base font-semibold text-slate-900">{{ cardTitle }}</p>
              <p class="mt-1 text-sm leading-6 text-slate-600">{{ message }}</p>
              <p v-if="status === 'success'" class="mt-3 text-sm font-medium text-emerald-700">
                Redirecting to sign in...
              </p>
            </div>
          </div>

          <div class="mt-5 flex flex-col gap-3 sm:flex-row">
            <router-link
              to="/login"
              class="inline-flex items-center justify-center rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
            >
              Go to sign in
            </router-link>
          </div>
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

const status = ref('loading')
const message = ref('Verifying your email now.')

const token = computed(() => {
  const queryToken = route.query.token
  return typeof queryToken === 'string' ? queryToken.trim() : ''
})

const heading = computed(() => {
  if (status.value === 'loading') return 'Verifying your email'
  if (status.value === 'success') return 'Email verified'
  return 'Verification failed'
})

const description = computed(() => {
  if (status.value === 'loading') return 'Please wait while we confirm your verification token.'
  if (status.value === 'success') return 'Your account is ready. You will be redirected to sign in shortly.'
  return 'We could not complete verification with this link.'
})

const cardTitle = computed(() => {
  if (status.value === 'loading') return 'Checking verification token'
  if (status.value === 'success') return 'Verification complete'
  return 'Verification could not be completed'
})

const panelClasses = computed(() => {
  if (status.value === 'success') return 'border-emerald-200 bg-emerald-50/70'
  if (status.value === 'loading') return 'border-cyan-200 bg-cyan-50/80'
  return 'border-amber-200 bg-amber-50/80'
})

const badgeClasses = computed(() => {
  if (status.value === 'success') return 'bg-emerald-100 text-emerald-700'
  if (status.value === 'loading') return 'bg-cyan-100 text-cyan-700'
  return 'bg-amber-100 text-amber-700'
})

async function runVerification() {
  if (!token.value) {
    status.value = 'error'
    message.value = 'Missing verification token.'
    return
  }

  try {
    const response = await authAPI.verifyEmail(token.value)
    status.value = 'success'
    message.value = response.data?.detail || 'Email verified successfully.'
    toastStore.show(message.value, 'success')
    window.setTimeout(() => {
      router.push('/login')
    }, 1500)
  } catch (err) {
    status.value = 'error'
    message.value = err.response?.data?.detail || 'Verification failed.'
    toastStore.show(message.value, 'error')
  }
}

onMounted(() => {
  runVerification()
})
</script>
