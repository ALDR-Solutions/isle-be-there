<template>
  <div class="min-h-screen bg-slate-50 text-slate-900">
    <header class="sticky top-0 z-50 border-b border-slate-200/80 bg-white/85 backdrop-blur-xl">
      <div class="mx-auto flex h-16 max-w-7xl items-center gap-4 px-4 sm:h-20 sm:px-6 lg:px-8">
        <router-link to="/" class="flex shrink-0 items-center gap-3">
          <img
            src="/isle-logo-solo.png"
            alt="Isle Be There logo"
            class="h-11 w-11 shrink-0 object-contain"
          />
          <div>
            <p class="hidden text-xs font-semibold uppercase tracking-[0.28em] text-cyan-600 sm:block">
              Travel Platform
            </p>
            <p class="text-base font-bold text-slate-900 sm:text-lg">
              Isle Be There
            </p>
          </div>
        </router-link>

        <div class="hidden min-w-0 flex-1 items-center justify-end gap-4 md:flex lg:gap-6">
          <nav class="flex shrink-0 items-center gap-5 lg:gap-8">
            <router-link to="/" class="text-sm font-medium text-slate-600 transition hover:text-slate-900">
              Home
            </router-link>
            <router-link to="/listings" class="text-sm font-medium text-slate-600 transition hover:text-slate-900">
              Listings
            </router-link>
          </nav>

          <form
            class="min-w-0 flex-1 max-w-xs lg:max-w-sm xl:max-w-md"
            @submit.prevent="submitSearch">
            <label for="desktop-navbar-search" class="sr-only">Search listings</label>
            <div class="group flex items-center gap-3 rounded-full border border-slate-200 bg-slate-100/85 px-3 py-2 text-slate-700 shadow-sm transition duration-200 hover:border-cyan-200 hover:bg-white focus-within:border-cyan-300 focus-within:bg-white focus-within:ring-2 focus-within:ring-cyan-100">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4 shrink-0 text-cyan-600 transition group-focus-within:text-cyan-700"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.8"
                  d="M21 21l-4.35-4.35M10.5 18a7.5 7.5 0 100-15 7.5 7.5 0 000 15z"/>
              </svg>
              <input
                id="desktop-navbar-search"
                v-model="searchInput"
                type="text"
                placeholder="Search"
                class="w-full min-w-0 bg-transparent text-sm text-slate-700 placeholder:text-slate-400 focus:outline-none"/>
              
            </div>
          </form>

          <div class="flex shrink-0 items-center justify-end gap-3">
            <template v-if="authStore.isAuthenticated">
              <div class="relative">
                <button
                  @click="desktopDropdownOpen = !desktopDropdownOpen"
                  class="flex items-center gap-1 rounded-2xl border border-slate-200 bg-slate-100 p-1.5 text-sm font-medium text-slate-700 transition hover:bg-slate-200">
                  <img
                    v-if="authStore.user?.avatar_url"
                    :src="authStore.user.avatar_url"
                    alt="Profile"
                    class="h-8 w-8 rounded-full object-cover ring-2 ring-slate-200"/>
                  <div
                    v-else
                    class="flex h-8 w-8 items-center justify-center rounded-full bg-cyan-500 text-sm font-bold text-white ring-2 ring-slate-200">
                    {{ userInitial }}
                  </div>
                  <svg class="h-4 w-4 transition-transform" :class="{ 'rotate-180': desktopDropdownOpen }" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M5.22 8.22a.75.75 0 0 1 1.06 0L10 11.94l3.72-3.72a.75.75 0 1 1 1.06 1.06l-4.25 4.25a.75.75 0 0 1-1.06 0L5.22 9.28a.75.75 0 0 1 0-1.06z" clip-rule="evenodd" />
                  </svg>
                </button>
                <div
                  v-if="desktopDropdownOpen"
                  class="absolute right-0 mt-2 w-44 rounded-2xl border border-slate-200 bg-white py-1 shadow-lg">
                  <router-link
                    to="/profile"
                    @click="desktopDropdownOpen = false"
                    class="block px-4 py-2.5 text-sm text-slate-700 transition hover:bg-slate-50">
                    Profile
                  </router-link>
                  <router-link
                    to="/bookings"
                    @click="desktopDropdownOpen = false"
                    class="block px-4 py-2.5 text-sm text-slate-700 transition hover:bg-slate-50">
                    Bookings
                  </router-link>
                  <router-link
                    to="/calendar"
                    @click="desktopDropdownOpen = false"
                    class="block px-4 py-2.5 text-sm text-slate-700 transition hover:bg-slate-50">
                    Calendar
                  </router-link>
                  <router-link
                    to="/favourites"
                    @click="desktopDropdownOpen = false"
                    class="block px-4 py-2.5 text-sm text-slate-700 transition hover:bg-slate-50">
                    Favourites
                  </router-link>
                  <hr class="my-1 border-slate-100" />
                  <button
                    @click="handleLogout"
                    class="block w-full px-4 py-2.5 text-left text-sm font-semibold text-red-600 transition hover:bg-slate-50">
                    Logout
                  </button>
                </div>
              </div>
            </template>

            <template v-else>
              <router-link
                to="/login"
                class="rounded-2xl px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100">
                Login
              </router-link>
              <router-link
                to="/register"
                class="rounded-2xl bg-cyan-500 px-4 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400">
                Sign Up
              </router-link>
            </template>
          </div>
        </div>

        <button
          @click="mobileMenuOpen = !mobileMenuOpen"
          class="ml-auto flex items-center justify-center rounded-xl p-2 text-slate-700 transition hover:bg-slate-100 md:hidden">
          <svg v-if="!mobileMenuOpen" class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
          <svg v-else class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

      </div>

      <div v-if="mobileMenuOpen" class="border-t border-slate-200 bg-white md:hidden">
        <div class="mx-auto max-w-7xl space-y-1 px-4 py-3 sm:px-6">
          <form
            class="mb-3"
            @submit.prevent="submitSearch">
            <label for="mobile-navbar-search" class="sr-only">Search listings</label>
            <div class="rounded-[1.6rem] border border-slate-200 bg-slate-50 p-2 shadow-sm">
              <div class="flex items-center gap-3 rounded-[1.2rem] border border-slate-200 bg-white px-3 py-3 text-slate-700 focus-within:border-cyan-300 focus-within:ring-2 focus-within:ring-cyan-100">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-5 w-5 shrink-0 text-cyan-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="1.8"
                    d="M21 21l-4.35-4.35M10.5 18a7.5 7.5 0 100-15 7.5 7.5 0 000 15z"/>
                </svg>
                <input
                  id="mobile-navbar-search"
                  v-model="searchInput"
                  type="text"
                  placeholder="Search stays, beaches, or experiences"
                  class="w-full bg-transparent text-sm text-slate-700 placeholder:text-slate-400 focus:outline-none"/>
                <button
                  type="submit"
                  class="inline-flex shrink-0 items-center justify-center rounded-full bg-cyan-500 px-3 py-1.5 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400">
                  Search
                </button>
              </div>
            </div>
          </form>

          <router-link
            to="/"
            @click="mobileMenuOpen = false"
            class="block rounded-xl px-3 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-100">
            Home
          </router-link>
          <router-link
            to="/listings"
            @click="mobileMenuOpen = false"
            class="block rounded-xl px-3 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-100">
            Listings
          </router-link>

          <template v-if="authStore.isAuthenticated">
            <hr class="border-slate-100" />
            <div class="flex items-center gap-3 rounded-2xl bg-slate-50 px-3 py-3 mb-2">
              <img
                v-if="authStore.user?.avatar_url"
                :src="authStore.user.avatar_url"
                alt="Profile"
                class="h-12 w-12 rounded-full object-cover ring-2 ring-slate-200 shrink-0"/>
              <div
                v-else
                class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-cyan-500 text-base font-bold text-white ring-2 ring-slate-200">
                {{ userInitial }}
              </div>
              <div class="min-w-0">
                <p class="truncate text-sm font-semibold text-slate-800">{{ authStore.user?.username }}</p>
                <p class="truncate text-xs text-slate-400">{{ authStore.user?.email }}</p>
              </div>
            </div>
            <router-link
              to="/profile"
              @click="mobileMenuOpen = false"
              class="block rounded-xl px-3 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-100">
              Profile
            </router-link>
            <router-link
              to="/bookings"
              @click="mobileMenuOpen = false"
              class="block rounded-xl px-3 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-100">
              Bookings
            </router-link>
            <router-link
              to="/calendar"
              @click="mobileMenuOpen = false"
              class="block rounded-xl px-3 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-100">
              Calendar
            </router-link>
            <router-link
              to="/favourites"
              @click="mobileMenuOpen = false"
              class="block rounded-xl px-3 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-100">
              Favourites
            </router-link>
            <button
              @click="handleLogout"
              class="block w-full rounded-xl px-3 py-2.5 text-left text-sm font-semibold text-red-600 transition hover:bg-slate-100">
              Logout
            </button>
          </template>

          <template v-else>
            <hr class="border-slate-100" />
            <router-link
              to="/login"
              @click="mobileMenuOpen = false"
              class="block rounded-xl px-3 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100">
              Login
            </router-link>
            <router-link
              to="/register"
              @click="mobileMenuOpen = false"
              class="block rounded-xl bg-cyan-500 px-3 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400">
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
        <div class="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
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
                  islebethere@outlook.com
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
              <p>Trinidad 000000</p>
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
import { computed, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useToastStore } from '../stores/toast';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const toastStore = useToastStore();

const currentYear = computed(() => new Date().getFullYear());
const desktopDropdownOpen = ref(false);
const mobileMenuOpen = ref(false);
const searchInput = ref('');

const userInitial = computed(() => {
  const name = authStore.user?.first_name || authStore.user?.username || '?'
  return name.charAt(0).toUpperCase()
});

watch(
  () => [route.name, route.query.q],
  ([routeName, queryValue]) => {
    if (routeName === 'Listings') {
      searchInput.value = typeof queryValue === 'string' ? queryValue.trim() : '';
      return;
    }

    searchInput.value = '';
  },
  { immediate: true },
);

const submitSearch = async () => {
  const q = searchInput.value.trim();

  desktopDropdownOpen.value = false;

  if (!q) {
    await router.push({ name: 'Listings' });
    mobileMenuOpen.value = false;
    return;
  }

  await router.push({
    name: 'Listings',
    query: { q },
  });
  mobileMenuOpen.value = false;
};

const handleLogout = () => {
  authStore.logout();
  toastStore.show('You have been logged out.', 'info');
  desktopDropdownOpen.value = false;
  mobileMenuOpen.value = false;
  router.push('/');
};
</script>
