<template>
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
          <h3 class="text-sm font-semibold uppercase tracking-[0.2em] text-white">Explore</h3>
          <div class="mt-4 space-y-3 text-sm text-slate-400">
            <p><router-link to="/" class="transition hover:text-white">Home</router-link></p>
            <p><router-link to="/listings" class="transition hover:text-white">Listings</router-link></p>
            <p><router-link to="/favorites" class="transition hover:text-white">Favorites</router-link></p>
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
</template>

<script setup>
import { computed } from 'vue'

const currentYear = computed(() => new Date().getFullYear())
</script>
