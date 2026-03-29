<template>
  <section class="grid overflow-hidden rounded-3xl border border-white/10 bg-white/10 shadow-2xl backdrop-blur-xl lg:grid-cols-2">
    <div class="hidden flex-col justify-between bg-gradient-to-br from-cyan-400 via-teal-300 to-emerald-300 p-10 text-slate-950 lg:flex">
      <div>
        <p class="text-sm font-semibold uppercase tracking-[0.3em] text-slate-800/70">
          Isle Be There
        </p>
        <h1 class="mt-6 max-w-md text-4xl font-bold leading-tight">
          Plan easier, travel smarter, and keep every booking in one place.
        </h1>
        <p class="mt-4 max-w-md text-base text-slate-800/80">
          Sign in to explore listings, manage favorites, and pick up right where you left off.
        </p>
      </div>

      <div class="rounded-2xl border border-slate-900/10 bg-white/40 p-5">
        <p class="text-sm font-medium text-slate-900">
          One account for bookings, saved places, and your travel profile.
        </p>
      </div>
    </div>

    <div class="bg-white px-6 py-8 sm:px-10 sm:py-12">
      <div class="mx-auto w-full max-w-md">
        <div class="mb-8">
          <p class="text-sm font-semibold uppercase tracking-[0.25em] text-slate-500">
            Welcome back
          </p>
          <h2 class="mt-3 text-3xl font-bold text-slate-900">
            Sign in to your account
          </h2>
          <p class="mt-2 text-sm text-slate-500">
            Enter your details below to continue.
          </p>
        </div>

        <form class="space-y-5" @submit.prevent="handleLogin">
          <FormField label="Email" for-id="email" required :error="errors.email">
            <input
              id="email"
              v-model="values.email"
              type="email"
              required
              autocomplete="email"
              placeholder="you@example.com"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100"
            />
          </FormField>

          <FormField
            label="Password"
            for-id="password"
            required
            help-text="Minimum 8 characters"
            :error="errors.password"
          >
            <div class="relative">
              <input
                id="password"
                v-model="values.password"
                :type="showPassword ? 'text' : 'password'"
                required
                autocomplete="current-password"
                placeholder="Enter your password"
                class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 pr-12 text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100"
              />
              <button
                type="button"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                tabindex="-1"
                @click="showPassword = !showPassword"
              >
                {{ showPassword ? 'Hide' : 'Show' }}
              </button>
            </div>
          </FormField>

          <InlineAlert v-if="submitError" :message="submitError" />

          <SubmitButton
            label="Sign in"
            loading-label="Signing in..."
            :loading="isSubmitting"
            full-width
          />
        </form>

        <p class="mt-6 text-center text-sm text-slate-500">
          Don't have an account?
          <router-link to="/register" class="font-semibold text-cyan-600 hover:text-cyan-500">
            Create one
          </router-link>
        </p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import FormField from '@/components/ui/FormField.vue'
import InlineAlert from '@/components/ui/InlineAlert.vue'
import SubmitButton from '@/components/ui/SubmitButton.vue'
import { useForm } from '@/composables/useForm'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const toastStore = useToastStore()

const form = useForm({
  email: '',
  password: '',
})
const { errors, isSubmitting, submitError, values } = form

const showPassword = ref(false)

function validate() {
  const errors = {}

  if (!form.values.value.email) {
    errors.email = 'Email is required.'
  }

  if (!form.values.value.password) {
    errors.password = 'Password is required.'
  }

  form.setErrors(errors)
  return Object.keys(errors).length === 0
}

async function handleLogin() {
  form.clearErrors()
  if (!validate()) return

  form.isSubmitting.value = true

  const success = await authStore.login(form.values.value.email, form.values.value.password)

  if (success) {
    toastStore.show('Login successful.', 'success')

    if (authStore.isAdmin) {
      router.push('/admin')
    } else if (authStore.isBusiness) {
      router.push('/business')
    } else {
      router.push(route.query.redirect || '/')
    }
  } else {
    form.submitError.value = authStore.error || 'Incorrect email or password.'
    toastStore.show(form.submitError.value, 'error')
  }

  form.isSubmitting.value = false
}
</script>
