<template>
  <header class="sticky top-0 z-50 border-b border-slate-200/80 bg-white/85 backdrop-blur-xl">
    <div class="mx-auto grid h-16 max-w-7xl grid-cols-3 items-center px-4 sm:h-20 sm:px-6 lg:px-8">
      <router-link :to="homeLink" class="flex items-center gap-3">
        <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-slate-900 text-sm font-bold text-white shadow-lg shadow-slate-900/10">
          IBT
        </div>
        <div>
          <p class="hidden text-xs font-semibold uppercase tracking-[0.28em] text-cyan-600 sm:block">
            Travel Platform
          </p>
          <p class="text-base font-bold text-slate-900 sm:text-lg">
            Isle Be There
          </p>
        </div>
      </router-link>

      <nav v-if="navigation.length" class="hidden items-center justify-center gap-8 md:flex">
        <router-link
          v-for="item in navigation"
          :key="item.to"
          :to="item.to"
          class="text-sm font-medium text-slate-600 transition hover:text-slate-900"
        >
          {{ item.label }}
        </router-link>
      </nav>
      <div v-else class="hidden items-center justify-center md:flex">
        <span class="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">{{ portalLabel }}</span>
      </div>

      <div class="hidden items-center justify-end gap-3 md:flex">
        <template v-if="authStore.isAuthenticated">
          <div class="relative">
            <button
              class="flex items-center gap-2 rounded-2xl border border-slate-200 bg-slate-100 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-200"
              @click="desktopMenuOpen = !desktopMenuOpen"
            >
              {{ authStore.user?.username || 'Account' }}
              <svg class="h-4 w-4 transition-transform" :class="{ 'rotate-180': desktopMenuOpen }" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M5.22 8.22a.75.75 0 0 1 1.06 0L10 11.94l3.72-3.72a.75.75 0 1 1 1.06 1.06l-4.25 4.25a.75.75 0 0 1-1.06 0L5.22 9.28a.75.75 0 0 1 0-1.06z" clip-rule="evenodd" />
              </svg>
            </button>
            <div
              v-if="desktopMenuOpen"
              class="absolute right-0 mt-2 w-48 rounded-2xl border border-slate-200 bg-white py-1 shadow-lg"
            >
              <router-link
                v-for="item in accountLinks"
                :key="item.to"
                :to="item.to"
                class="block px-4 py-2.5 text-sm text-slate-700 transition hover:bg-slate-50"
                @click="closeMenus"
              >
                {{ item.label }}
              </router-link>
              <hr class="my-1 border-slate-100" />
              <button
                class="block w-full px-4 py-2.5 text-left text-sm font-semibold text-red-600 transition hover:bg-slate-50"
                @click="handleLogout"
              >
                Logout
              </button>
            </div>
          </div>
        </template>

        <template v-else>
          <router-link to="/login" class="rounded-2xl px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100">
            Login
          </router-link>
          <router-link to="/register" class="rounded-2xl bg-cyan-500 px-4 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400">
            Sign Up
          </router-link>
        </template>
      </div>

      <button
        class="col-start-3 justify-self-end flex items-center justify-center rounded-xl p-2 text-slate-700 transition hover:bg-slate-100 md:hidden"
        @click="mobileMenuOpen = !mobileMenuOpen"
      >
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
        <router-link
          v-for="item in navigation"
          :key="item.to"
          :to="item.to"
          class="block rounded-xl px-3 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
          @click="closeMenus"
        >
          {{ item.label }}
        </router-link>

        <template v-if="authStore.isAuthenticated">
          <hr class="border-slate-100" />
          <div class="px-3 py-1.5 text-xs font-semibold uppercase tracking-wider text-slate-400">
            {{ authStore.user?.username || 'Account' }}
          </div>
          <router-link
            v-for="item in accountLinks"
            :key="item.to"
            :to="item.to"
            class="block rounded-xl px-3 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
            @click="closeMenus"
          >
            {{ item.label }}
          </router-link>
          <button
            class="block w-full rounded-xl px-3 py-2.5 text-left text-sm font-semibold text-red-600 transition hover:bg-slate-100"
            @click="handleLogout"
          >
            Logout
          </button>
        </template>

        <template v-else>
          <hr class="border-slate-100" />
          <router-link to="/login" class="block rounded-xl px-3 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100" @click="closeMenus">
            Login
          </router-link>
          <router-link to="/register" class="block rounded-xl bg-cyan-500 px-3 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400" @click="closeMenus">
            Sign Up
          </router-link>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'

defineProps({
  homeLink: {
    type: String,
    default: '/',
  },
  navigation: {
    type: Array,
    default: () => [],
  },
  accountLinks: {
    type: Array,
    default: () => [],
  },
  portalLabel: {
    type: String,
    default: '',
  },
})

const router = useRouter()
const authStore = useAuthStore()
const toastStore = useToastStore()

const desktopMenuOpen = ref(false)
const mobileMenuOpen = ref(false)

function closeMenus() {
  desktopMenuOpen.value = false
  mobileMenuOpen.value = false
}

function handleLogout() {
  authStore.logout()
  toastStore.show('You have been logged out.', 'info')
  closeMenus()
  router.push('/')
}
</script>
