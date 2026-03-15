<template>
  <div class="min-h-screen overflow-hidden bg-slate-950">
    <div class="relative flex min-h-screen items-center justify-center px-4 py-4 sm:px-6 lg:px-8">
      <div class="absolute inset-0">
        <div class="absolute left-[-10%] top-[-10%] h-72 w-72 rounded-full bg-cyan-500/20 blur-3xl"></div>
        <div class="absolute bottom-[-10%] right-[-10%] h-80 w-80 rounded-full bg-emerald-400/20 blur-3xl"></div>
        <div class="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(255,255,255,0.08),_transparent_45%)]"></div>
      </div>

      <div class="relative z-10 w-full max-w-5xl">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup>
</script>
