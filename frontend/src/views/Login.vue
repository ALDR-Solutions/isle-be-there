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

          <div>
            <div class="mb-2 flex items-center justify-between">
              <label for="password" class="block text-sm font-medium text-slate-700">
                Password
              </label>
              <span class="text-xs text-slate-400">Minimum 8 characters</span>
            </div>
            <div class="relative">
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                required
                autocomplete="current-password"
                placeholder="Enter your password"
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

          <div
            v-if="error"
            class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
          >
            {{ error }}
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <span v-if="loading">Signing in...</span>
            <span v-else>Sign in</span>
          </button>
        </form>

        <p class="mt-6 text-center text-sm text-slate-500">
          Don’t have an account?
          <router-link to="/register" class="font-semibold text-cyan-600 hover:text-cyan-500">
            Create one
          </router-link>
        </p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useToastStore } from '../stores/toast'

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const toastStore = useToastStore();

const email = ref('');
const password = ref('');
const showPassword = ref(false);
const error = ref('');
const loading = ref(false);

const handleLogin = async () => {
  error.value = '';
  loading.value = true;

  const success = await authStore.login(email.value, password.value);

  if (success) {
    toastStore.show('Login Successful.', 'success');
    if (authStore.isBusiness) {
      router.push('/business');
    }else if (authStore.isAdmin){
      router.push('/admin');  
    } else {
      router.push(route.query.redirect || '/');
    }
  } else {
    error.value = authStore.error || 'Login failed';
    toastStore.show('Incorrect email or password', 'error')
  }

  loading.value = false;
};
</script>
