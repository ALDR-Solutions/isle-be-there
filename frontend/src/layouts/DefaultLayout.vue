<template>
  <div class="min-h-screen bg-slate-50 text-slate-900">
    <header class="sticky top-0 z-50 border-b border-slate-200/80 bg-white/85 backdrop-blur-xl">
      <div class="mx-auto flex h-20 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <router-link to="/" class="flex items-center gap-3">
          <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-slate-900 text-sm font-bold text-white shadow-lg shadow-slate-900/10">
            IBT
          </div>
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-600">
              Travel Platform
            </p>
            <p class="text-lg font-bold text-slate-900">
              Isle Be There
            </p>
          </div>
        </router-link>

        <nav class="hidden items-center gap-8 md:flex">
          <router-link to="/" class="text-sm font-medium text-slate-600 transition hover:text-slate-900">
            Home
          </router-link>
          <router-link to="/listings" class="text-sm font-medium text-slate-600 transition hover:text-slate-900">
            Listings
          </router-link>

          <template v-if="authStore.isAuthenticated">
            <router-link to="/bookings" class="text-sm font-medium text-slate-600 transition hover:text-slate-900">
              Bookings
            </router-link>
            <router-link to="/favorites" class="text-sm font-medium text-slate-600 transition hover:text-slate-900">
              Favorites
            </router-link>
            <router-link to="/profile" class="text-sm font-medium text-slate-600 transition hover:text-slate-900">
              Profile
            </router-link>
          </template>
        </nav>

        <div class="flex items-center gap-3">
          <template v-if="authStore.isAuthenticated">
            <div class="hidden rounded-2xl border border-slate-200 bg-slate-100 px-4 py-2 text-sm text-slate-600 lg:block">
              {{ authStore.user?.email }}
            </div>
            <button
              @click="handleLogout"
              class="rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800"
            >
              Logout
            </button>
          </template>

          <template v-else>
            <router-link
              to="/login"
              class="rounded-2xl px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
            >
              Login
            </router-link>
            <router-link
              to="/register"
              class="rounded-2xl bg-cyan-500 px-4 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400"
            >
              Sign Up
            </router-link>
          </template>
        </div>
      </div>
    </header>

    <main>
      <slot />
    </main>

    <footer class="relative mt-16 overflow-hidden border-t border-slate-200 bg-slate-950 text-slate-200">
      <div class="absolute inset-0">
        <div class="absolute left-0 top-0 h-56 w-56 rounded-full bg-cyan-500/10 blur-3xl"></div>
        <div class="absolute bottom-0 right-0 h-64 w-64 rounded-full bg-emerald-400/10 blur-3xl"></div>
      </div>

      <div class="relative mx-auto max-w-7xl px-4 py-14 sm:px-6 lg:px-8">
        <div class="grid gap-10 md:grid-cols-2 lg:grid-cols-4">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.3em] text-cyan-400">
              Isle Be There
            </p>
            <h2 class="mt-4 text-2xl font-bold text-white">
              Travel planning with a cleaner, calmer experience.
            </h2>
            <p class="mt-4 text-sm leading-6 text-slate-400">
              Discover stays, manage bookings, and keep your travel plans organized in one place.
            </p>
          </div>

          <div>
            <h3 class="text-sm font-semibold uppercase tracking-[0.2em] text-white">
              Explore
            </h3>
            <div class="mt-4 space-y-3 text-sm text-slate-400">
              <p>
                <router-link to="/" class="transition hover:text-white">Home</router-link>
              </p>
              <p>
                <router-link to="/listings" class="transition hover:text-white">Listings</router-link>
              </p>
              <p>
                <router-link to="/favorites" class="transition hover:text-white">Favorites</router-link>
              </p>
              <p>
                <router-link to="/bookings" class="transition hover:text-white">Bookings</router-link>
              </p>
            </div>
          </div>

          <div>
            <h3 class="text-sm font-semibold uppercase tracking-[0.2em] text-white">
              Contact
            </h3>
            <div class="mt-4 space-y-3 text-sm text-slate-400">
              <p>
                Email:
                <a href="mailto:hello@islebethere.com" class="transition hover:text-white">
                  hello@islebethere.com
                </a>
              </p>
              <p>
                Phone:
                <a href="tel:+6561234567" class="transition hover:text-white">
                  +65 6123 4567
                </a>
              </p>
              <p>
                Support:
                <a href="mailto:support@islebethere.com" class="transition hover:text-white">
                  support@islebethere.com
                </a>
              </p>
            </div>
          </div>

          <div>
            <h3 class="text-sm font-semibold uppercase tracking-[0.2em] text-white">
              Office
            </h3>
            <div class="mt-4 space-y-3 text-sm text-slate-400">
              <p>Isle Be There Pte. Ltd.</p>
              <p>123 Marina View</p>
              <p>Level 8, South Tower</p>
              <p>Singapore 018960</p>
            </div>
          </div>
        </div>

        <div class="mt-12 flex flex-col gap-4 border-t border-white/10 pt-6 text-sm text-slate-500 md:flex-row md:items-center md:justify-between">
          <p>&copy; {{ currentYear }} Isle Be There. All rights reserved.</p>
          <p>Built for smoother discovery, booking, and travel planning.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useToastStore } from '../stores/toast';

const router = useRouter();
const authStore = useAuthStore();
const toastStore = useToastStore();

const currentYear = computed(() => new Date().getFullYear());

const handleLogout = () => {
  authStore.logout();
  toastStore.show('You have been logged out.', 'info')
  router.push('/');
};
</script>
