<template>
  <section class="relative overflow-hidden bg-slate-50">
    <div class="absolute inset-0">
      <div class="absolute left-0 top-0 h-72 w-72 rounded-full bg-cyan-200/40 blur-3xl"></div>
      <div class="absolute bottom-0 right-0 h-80 w-80 rounded-full bg-emerald-200/40 blur-3xl"></div>
    </div>

    <div class="relative mx-auto flex min-h-[calc(100vh-16rem)] max-w-5xl items-center px-4 py-16 sm:px-6 lg:px-8">
      <div class="w-full rounded-[2rem] border border-slate-200 bg-white/90 p-8 shadow-xl shadow-slate-200/50 backdrop-blur sm:p-12">
        <p class="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-600">Error 404</p>
        <h1 class="mt-4 max-w-2xl text-4xl font-bold tracking-tight text-slate-950 sm:text-5xl">
          This page took a wrong turn.
        </h1>
        <p class="mt-4 max-w-2xl text-base leading-7 text-slate-600 sm:text-lg">
          The page you were looking for does not exist, may have moved, or never became part of the trip.
        </p>

        <div class="mt-8 flex flex-col gap-3 sm:flex-row">
          <router-link
            to="/"
            class="inline-flex items-center justify-center rounded-2xl bg-slate-950 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
          >
            Back to Home
          </router-link>
          <router-link
            to="/listings"
            class="inline-flex items-center justify-center rounded-2xl border border-slate-200 bg-white px-6 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
          >
            Browse Listings
          </router-link>
        </div>
      </div>
    </div>
  </section>
</template>
