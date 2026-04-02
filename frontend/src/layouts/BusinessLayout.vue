<template>
  <div class="min-h-screen bg-slate-50 text-slate-900">
    <header class="sticky top-0 z-50 border-b border-slate-200/80 bg-white/85 backdrop-blur-xl">
      <div class="mx-auto grid h-16 max-w-7xl grid-cols-3 items-center px-4 sm:h-20 sm:px-6 lg:px-8">
        <router-link to="/business" class="flex items-center gap-3">
          <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-slate-900 text-sm font-bold text-white shadow-lg shadow-slate-900/10">
            IBT
          </div>
          <div>
            <p class="hidden text-xs font-semibold uppercase tracking-[0.28em] text-cyan-600 sm:block">Travel Platform</p>
            <p class="text-base font-bold text-slate-900 sm:text-lg">Isle Be There</p>
          </div>
        </router-link>

        <div class="hidden items-center justify-center md:flex">
          <span class="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Business Portal</span>
        </div>

        <div class="hidden items-center justify-end gap-3 md:flex">
          <div class="relative">
            <button
              @click="desktopDropdownOpen = !desktopDropdownOpen"
              class="flex items-center gap-1 rounded-2xl border border-slate-200 bg-slate-100 p-1.5 text-sm font-medium text-slate-700 transition hover:bg-slate-200"
            >
              <img
                v-if="authStore.user?.avatar_url"
                :src="authStore.user.avatar_url"
                alt="Profile"
                class="h-8 w-8 rounded-full object-cover ring-2 ring-slate-200"
              />
              <div
                v-else
                class="flex h-8 w-8 items-center justify-center rounded-full bg-cyan-500 text-sm font-bold text-white ring-2 ring-slate-200"
              >
                {{ userInitial }}
              </div>
              <svg class="h-4 w-4 transition-transform" :class="{ 'rotate-180': desktopDropdownOpen }" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M5.22 8.22a.75.75 0 0 1 1.06 0L10 11.94l3.72-3.72a.75.75 0 1 1 1.06 1.06l-4.25 4.25a.75.75 0 0 1-1.06 0L5.22 9.28a.75.75 0 0 1 0-1.06z" clip-rule="evenodd" />
              </svg>
            </button>

            <div
              v-if="desktopDropdownOpen"
              class="absolute right-0 mt-2 w-64 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-lg"
            >
              <!-- Business name -->
              <div class="border-b border-slate-100 px-4 py-3">
                <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Business</p>
                <p class="mt-0.5 truncate text-sm font-semibold text-slate-800">
                  {{ businessStore.business?.name || authStore.user?.username }}
                </p>
              </div>

              <!-- Listings switcher -->
              <div class="border-b border-slate-100">
                <p class="px-4 pb-1 pt-3 text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">My Listings</p>
                <div class="max-h-48 overflow-y-auto">
                  <p v-if="businessStore.loading" class="px-4 py-3 text-xs text-slate-400">Loading...</p>
                  <p v-else-if="businessStore.listings.length === 0" class="px-4 py-3 text-xs text-slate-400">No listings yet.</p>
                  <button
                    v-for="listing in businessStore.listings"
                    :key="listing.id"
                    @click="switchListing(listing.id)"
                    class="flex w-full items-center gap-3 px-4 py-2.5 text-left text-sm transition hover:bg-slate-50"
                    :class="businessStore.activeListingId === listing.id ? 'font-semibold text-slate-900' : 'font-medium text-slate-600'"
                  >
                    <span
                      class="h-2 w-2 shrink-0 rounded-full transition-colors"
                      :class="businessStore.activeListingId === listing.id ? 'bg-cyan-400' : 'bg-slate-200'"
                    ></span>
                    <span class="truncate">{{ listing.title }}</span>
                  </button>
                </div>
                <button
                  @click="triggerAddListing"
                  class="flex w-full items-center gap-2 px-4 py-3 text-left text-sm font-medium text-cyan-600 transition hover:bg-cyan-50"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
                  </svg>
                  Add a listing
                </button>
              </div>

              <!-- Profile / Logout -->
              <div class="py-1">
                <router-link
                  to="/business/profile"
                  @click="desktopDropdownOpen = false"
                  class="block w-full px-4 py-2.5 text-left text-sm font-medium text-slate-700 transition hover:bg-slate-50"
                >Profile</router-link>
                <button
                  @click="handleLogout"
                  class="block w-full px-4 py-2.5 text-left text-sm font-semibold text-red-600 transition hover:bg-slate-50"
                >Logout</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Mobile hamburger -->
        <button
          @click="mobileMenuOpen = !mobileMenuOpen"
          class="col-start-3 flex items-center justify-center justify-self-end rounded-xl p-2 text-slate-700 transition hover:bg-slate-100 md:hidden"
        >
          <svg v-if="!mobileMenuOpen" class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
          <svg v-else class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Mobile menu -->
      <div v-if="mobileMenuOpen" class="border-t border-slate-200 bg-white md:hidden">
        <div class="mx-auto max-w-7xl px-4 py-3 sm:px-6">
          <div class="flex items-center gap-3 rounded-2xl bg-slate-50 px-3 py-3 mb-2">
            <img
              v-if="authStore.user?.avatar_url"
              :src="authStore.user.avatar_url"
              alt="Profile"
              class="h-12 w-12 rounded-full object-cover ring-2 ring-slate-200 shrink-0"
            />
            <div
              v-else
              class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-cyan-500 text-base font-bold text-white ring-2 ring-slate-200"
            >
              {{ userInitial }}
            </div>
            <div class="min-w-0">
              <p class="truncate text-sm font-semibold text-slate-800">{{ businessStore.business?.name || authStore.user?.username }}</p>
              <p class="truncate text-xs text-slate-400">{{ authStore.user?.email }}</p>
            </div>
          </div>

          <div class="border-t border-slate-100 py-2">
            <p class="px-3 pb-1 pt-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">My Listings</p>
            <button
              v-for="listing in businessStore.listings"
              :key="listing.id"
              @click="switchListing(listing.id)"
              class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm transition hover:bg-slate-100"
              :class="businessStore.activeListingId === listing.id ? 'font-semibold text-slate-900' : 'font-medium text-slate-600'"
            >
              <span
                class="h-2 w-2 shrink-0 rounded-full"
                :class="businessStore.activeListingId === listing.id ? 'bg-cyan-400' : 'bg-slate-200'"
              ></span>
              {{ listing.title }}
            </button>
            <button
              @click="triggerAddListing"
              class="flex w-full items-center gap-2 rounded-xl px-3 py-2.5 text-left text-sm font-medium text-cyan-600 transition hover:bg-cyan-50"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
              </svg>
              Add a listing
            </button>
          </div>

          <div class="border-t border-slate-100 pt-2">
            <router-link
              to="/business/profile"
              @click="mobileMenuOpen = false"
              class="block w-full rounded-xl px-3 py-2.5 text-left text-sm font-medium text-slate-700 transition hover:bg-slate-100"
            >Profile</router-link>
            <button
              @click="handleLogout"
              class="block w-full rounded-xl px-3 py-2.5 text-left text-sm font-semibold text-red-600 transition hover:bg-slate-100"
            >Logout</button>
          </div>
        </div>
      </div>
    </header>

    <main><slot /></main>

    <footer class="relative mt-16 overflow-hidden border-t border-slate-200 bg-slate-950 text-slate-200">
      <div class="absolute inset-0">
        <div class="absolute left-0 top-0 h-56 w-56 rounded-full bg-cyan-500/10 blur-3xl"></div>
        <div class="absolute bottom-0 right-0 h-64 w-64 rounded-full bg-emerald-400/10 blur-3xl"></div>
      </div>
      <div class="relative mx-auto max-w-7xl px-4 py-14 sm:px-6 lg:px-8">
        <div class="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.3em] text-cyan-400">Isle Be There</p>
            <h2 class="mt-4 text-2xl font-bold text-white">Travel planning with a cleaner, calmer experience.</h2>
            <p class="mt-4 text-sm leading-6 text-slate-400">Discover stays, manage bookings, and keep your travel plans organized in one place.</p>
          </div>
          <div>
            <h3 class="text-sm font-semibold uppercase tracking-[0.2em] text-white">Explore</h3>
            <div class="mt-4 space-y-3 text-sm text-slate-400">
              <p><router-link to="/" class="transition hover:text-white">Home</router-link></p>
              <p><router-link to="/listings" class="transition hover:text-white">Listings</router-link></p>
              <p><router-link to="/favourites" class="transition hover:text-white">Favourites</router-link></p>
              <p><router-link to="/bookings" class="transition hover:text-white">Bookings</router-link></p>
            </div>
          </div>
          <div>
            <h3 class="text-sm font-semibold uppercase tracking-[0.2em] text-white">Contact</h3>
            <div class="mt-4 space-y-3 text-sm text-slate-400">
              <p>Email: <a href="mailto:hello@islebethere.com" class="transition hover:text-white">hello@islebethere.com</a></p>
              <p>Phone: <a href="tel:+6561234567" class="transition hover:text-white">+65 6123 4567</a></p>
              <p>Support: <a href="mailto:support@islebethere.com" class="transition hover:text-white">support@islebethere.com</a></p>
            </div>
          </div>
          <div>
            <h3 class="text-sm font-semibold uppercase tracking-[0.2em] text-white">Office</h3>
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
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'
import { useBusinessStore } from '../stores/business'

const router = useRouter()
const authStore = useAuthStore()
const toastStore = useToastStore()
const businessStore = useBusinessStore()

const currentYear = computed(() => new Date().getFullYear())
const desktopDropdownOpen = ref(false)
const mobileMenuOpen = ref(false)

const userInitial = computed(() => {
  const name = authStore.user?.first_name || authStore.user?.username || '?'
  return name.charAt(0).toUpperCase()
})

onMounted(() => {
  businessStore.fetchBusiness()
})

function switchListing(id) {
  businessStore.setActiveListing(id)
  desktopDropdownOpen.value = false
  mobileMenuOpen.value = false
}

function triggerAddListing() {
  businessStore.showCreateModal = true
  desktopDropdownOpen.value = false
  mobileMenuOpen.value = false
}

function handleLogout() {
  authStore.logout()
  businessStore.reset()
  toastStore.show('You have been logged out.', 'info')
  desktopDropdownOpen.value = false
  mobileMenuOpen.value = false
  router.push('/')
}
</script>
