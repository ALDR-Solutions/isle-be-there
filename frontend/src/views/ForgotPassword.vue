<template>
  <section class="grid overflow-hidden rounded-3xl border border-white/10 bg-white/10 shadow-2xl backdrop-blur-xl lg:grid-cols-2">
    <div class="hidden flex-col justify-between bg-gradient-to-br from-cyan-400 via-teal-300 to-emerald-300 p-10 text-slate-950 lg:flex">
      <div>
        <p class="text-sm font-semibold uppercase tracking-[0.3em] text-slate-800/70">
          Isle Be There
        </p>
        <h1 class="mt-6 max-w-md text-4xl font-bold leading-tight">
          Regain access without losing momentum.
        </h1>
        <p class="mt-4 max-w-md text-base text-slate-800/80">
          Enter your email and we'll send a reset link if an account exists for it.
        </p>
      </div>

      <div class="rounded-2xl border border-slate-900/10 bg-white/40 p-5">
        <p class="text-sm font-medium text-slate-900">
          For privacy, the response stays the same whether the email exists or not.
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
            Forgot your password?
          </h2>
          <p class="mt-2 text-sm text-slate-500">
            Enter your email and we'll send reset instructions.
          </p>
        </div>

        <form class="space-y-5" @submit.prevent="handleSubmit">
          <div>
            <label for="email" class="mb-2 block text-sm font-medium text-slate-700">
              Email
            </label>
            <input
              id="email"
              v-model="email"
              type="email"
              required
              autocomplete="email"
              placeholder="you@example.com"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100"
            />
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
            :disabled="loading"
            class="w-full rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <span v-if="loading">Sending reset link...</span>
            <span v-else>Send reset link</span>
          </button>
        </form>

        <div class="mt-6 flex flex-col gap-2 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between">
          <router-link to="/login" class="font-semibold text-cyan-600 hover:text-cyan-500">
            Back to sign in
          </router-link>
          <router-link to="/register" class="font-semibold text-slate-700 hover:text-slate-900">
            Create an account
          </router-link>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { authAPI } from '../services/api'
import { useToastStore } from '../stores/toast'

const toastStore = useToastStore()

const email = ref('')
const loading = ref(false)
const hasError = ref(false)
const message = ref('')

async function handleSubmit() {
  message.value = ''
  hasError.value = false
  loading.value = true

  try {
    const normalizedEmail = email.value.trim()
    const response = await authAPI.forgotPassword(normalizedEmail)
    email.value = normalizedEmail
    message.value = response.data?.detail || 'If an account exists for that email, a reset link has been sent.'
    toastStore.show(message.value, 'success')
  } catch (err) {
    hasError.value = true
    message.value = err.response?.data?.detail || 'Unable to send reset instructions.'
    toastStore.show(message.value, 'error')
  } finally {
    loading.value = false
  }
}
</script>
