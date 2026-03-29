<template>
  <section class="grid overflow-hidden rounded-3xl border border-white/10 bg-white/10 shadow-2xl backdrop-blur-xl lg:grid-cols-[0.9fr_1.1fr]">
    <div class="hidden flex-col justify-between bg-gradient-to-br from-cyan-400 via-teal-300 to-emerald-300 p-8 text-slate-950 lg:flex">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-800/70">
          Isle Be There
        </p>
        <h1 class="mt-4 max-w-sm text-3xl font-bold leading-tight">
          Create an account and keep every trip in one place.
        </h1>
        <p class="mt-3 max-w-sm text-sm leading-6 text-slate-800/80">
          Save favorites, manage bookings, and personalize your travel experience.
        </p>
      </div>

      <div class="rounded-2xl border border-slate-900/10 bg-white/40 p-4">
        <p class="text-sm font-medium text-slate-900">
          Join as a traveler or use a business account to manage listings.
        </p>
      </div>
    </div>

    <div class="bg-white px-6 py-6 sm:px-8 lg:px-10">
      <div class="mx-auto w-full max-w-xl">
        <div class="mb-6">
          <p class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">
            Get started
          </p>
          <h2 class="mt-2 text-2xl font-bold text-slate-900">
            Create your account
          </h2>
          <p class="mt-1 text-sm text-slate-500">
            Fill in your details to join Isle Be There.
          </p>
        </div>

        <form class="space-y-4" @submit.prevent="handleRegister">
          <div class="grid gap-4 sm:grid-cols-2">
            <FormField label="First name" for-id="firstName" required :error="errors.first_name">
              <input
                id="firstName"
                v-model="values.first_name"
                type="text"
                required
                autocomplete="given-name"
                placeholder="Lee"
                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100"
              />
            </FormField>

            <FormField label="Last name" for-id="lastName" required :error="errors.last_name">
              <input
                id="lastName"
                v-model="values.last_name"
                type="text"
                required
                autocomplete="family-name"
                placeholder="Chong"
                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100"
              />
            </FormField>
          </div>

          <div class="grid gap-4 sm:grid-cols-2">
            <FormField label="Email" for-id="email" required :error="errors.email">
              <input
                id="email"
                v-model="values.email"
                type="email"
                required
                autocomplete="email"
                placeholder="you@example.com"
                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100"
              />
            </FormField>

            <FormField label="Username" for-id="username" required :error="errors.username">
              <input
                id="username"
                v-model="values.username"
                type="text"
                required
                autocomplete="username"
                placeholder="leechong"
                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100"
              />
            </FormField>
          </div>

          <FormField label="Password" for-id="password" required help-text="Choose a strong password" :error="errors.password">
            <div class="relative">
              <input
                id="password"
                v-model="values.password"
                :type="showPassword ? 'text' : 'password'"
                required
                autocomplete="new-password"
                placeholder="Create a password"
                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 pr-14 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100"
              />
              <button
                type="button"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-slate-400 hover:text-slate-600"
                tabindex="-1"
                @click="showPassword = !showPassword"
              >
                {{ showPassword ? 'Hide' : 'Show' }}
              </button>
            </div>
          </FormField>

          <FormField label="Confirm password" for-id="confirmPassword" required :error="errors.confirmPassword">
            <div class="relative">
              <input
                id="confirmPassword"
                v-model="values.confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                required
                autocomplete="new-password"
                placeholder="Repeat your password"
                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 pr-14 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100"
              />
              <button
                type="button"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-slate-400 hover:text-slate-600"
                tabindex="-1"
                @click="showConfirmPassword = !showConfirmPassword"
              >
                {{ showConfirmPassword ? 'Hide' : 'Show' }}
              </button>
            </div>
          </FormField>

          <label class="flex items-start gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
            <input
              v-model="values.is_business"
              type="checkbox"
              class="mt-0.5 h-4 w-4 rounded border-slate-300 text-cyan-600 focus:ring-cyan-500"
            />
            <span>
              <span class="block text-sm font-medium text-slate-800">Business account</span>
              <span class="block text-xs text-slate-500">
                Enable this if you want to manage listings as a business.
              </span>
            </span>
          </label>

          <InlineAlert v-if="submitError" :message="submitError" />

          <SubmitButton
            label="Create account"
            loading-label="Creating account..."
            :loading="isSubmitting"
            full-width
          />
        </form>

        <p class="mt-4 text-center text-sm text-slate-500">
          Already have an account?
          <router-link to="/login" class="font-semibold text-cyan-600 hover:text-cyan-500">
            Sign in
          </router-link>
        </p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import FormField from '@/components/ui/FormField.vue'
import InlineAlert from '@/components/ui/InlineAlert.vue'
import SubmitButton from '@/components/ui/SubmitButton.vue'
import { useForm } from '@/composables/useForm'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'

const router = useRouter()
const authStore = useAuthStore()
const toastStore = useToastStore()

const form = useForm({
  first_name: '',
  last_name: '',
  email: '',
  username: '',
  password: '',
  confirmPassword: '',
  is_business: false,
})
const { errors, isSubmitting, submitError, values } = form

const showPassword = ref(false)
const showConfirmPassword = ref(false)

function validate() {
  const errors = {}

  if (!form.values.value.first_name) errors.first_name = 'First name is required.'
  if (!form.values.value.last_name) errors.last_name = 'Last name is required.'
  if (!form.values.value.email) errors.email = 'Email is required.'
  if (!form.values.value.username) errors.username = 'Username is required.'
  if (!form.values.value.password) errors.password = 'Password is required.'

  if (form.values.value.password !== form.values.value.confirmPassword) {
    errors.confirmPassword = 'Passwords do not match.'
  }

  form.setErrors(errors)
  return Object.keys(errors).length === 0
}

async function handleRegister() {
  form.clearErrors()
  if (!validate()) return

  form.isSubmitting.value = true

  const success = await authStore.register({
    email: form.values.value.email,
    password: form.values.value.password,
    username: form.values.value.username,
    first_name: form.values.value.first_name,
    last_name: form.values.value.last_name,
    is_business: form.values.value.is_business,
  })

  if (success) {
    toastStore.show('Account created successfully.', 'success')
    router.push(authStore.isBusiness ? '/business' : '/')
  } else {
    form.submitError.value = authStore.error || 'Registration failed.'
    toastStore.show(form.submitError.value, 'error')
  }

  form.isSubmitting.value = false
}
</script>
