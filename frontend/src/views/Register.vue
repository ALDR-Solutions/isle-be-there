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
          Save favourites, manage bookings, and personalize your travel experience.
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
            <div>
              <label for="firstName" class="mb-1.5 block text-sm font-medium text-slate-700">
                First name
              </label>
              <input
                id="firstName"
                v-model="firstName"
                type="text"
                required
                autocomplete="given-name"
                placeholder="Lee"
                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100"
              />
            </div>

            <div>
              <label for="lastName" class="mb-1.5 block text-sm font-medium text-slate-700">
                Last name
              </label>
              <input
                id="lastName"
                v-model="lastName"
                type="text"
                required
                autocomplete="family-name"
                placeholder="Chong"
                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100"
              />
            </div>
          </div>

          <div class="grid gap-4 sm:grid-cols-2">
            <div>
              <label for="email" class="mb-1.5 block text-sm font-medium text-slate-700">
                Email
              </label>
              <input
                id="email"
                v-model="email"
                type="email"
                required
                autocomplete="email"
                placeholder="you@example.com"
                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100"
              />
            </div>

            <div>
              <label for="username" class="mb-1.5 block text-sm font-medium text-slate-700">
                Username
              </label>
              <input
                id="username"
                v-model="username"
                type="text"
                required
                autocomplete="username"
                placeholder="leechong"
                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100"
              />
            </div>
          </div>

          <div>
            <div class="mb-1.5 flex items-center justify-between">
              <label for="password" class="block text-sm font-medium text-slate-700">
                Password
              </label>
              <span class="text-xs text-slate-400">Choose a strong password</span>
            </div>
            <div class="relative">
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                required
                autocomplete="new-password"
                placeholder="Create a password"
                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 pr-11 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                tabindex="-1"
              >
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
            <div class="mb-1.5 flex items-center justify-between">
              <label for="confirmPassword" class="block text-sm font-medium text-slate-700">
                Confirm password
              </label>
            </div>
            <div class="relative">
              <input
                id="confirmPassword"
                v-model="confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                required
                autocomplete="new-password"
                placeholder="Repeat your password"
                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 pr-11 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100"
              />
              <button
                type="button"
                @click="showConfirmPassword = !showConfirmPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                tabindex="-1"
              >
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


          <label class="flex items-start gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
            <input
              v-model="isBusiness"
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

          <div
            v-if="error"
            class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
          >
            {{ error }}
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full rounded-xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <span v-if="loading">Creating account...</span>
            <span v-else>Create account</span>
          </button>
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
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useToastStore } from '../stores/toast';

const router = useRouter();
const authStore = useAuthStore();
const toastStore = useToastStore();

const firstName = ref('');
const lastName = ref('');
const email = ref('');
const username = ref('');
const password = ref('');
const confirmPassword = ref('');
const showPassword = ref(false);
const showConfirmPassword = ref(false);
const isBusiness = ref(false);
const error = ref('');
const loading = ref(false);

const handleRegister = async () => {
  error.value = '';
  loading.value = true;

  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match';
    loading.value = false;
    return;
  }


  const success = await authStore.register({
    email: email.value,
    password: password.value,
    username: username.value,
    first_name: firstName.value,
    last_name: lastName.value,
    is_business: isBusiness.value,
  });

  if (success) {
    toastStore.show('Account created successfully.', 'success')
    if (authStore.isBusiness) {
      router.push('/business');
    } else {
      router.push('/');
    }
  } else {
    error.value = authStore.error || 'Registration failed';
    toastStore.show(error.value, 'error')
  }

  loading.value = false;
};
</script>
