<template>
  <div class="min-h-screen overflow-hidden bg-slate-950">
    <div class="relative flex min-h-screen items-center justify-center px-4 py-4 sm:px-6 lg:px-8">
      <div class="absolute inset-0">
        <div
          v-for="(image, index) in authBackgrounds"
          :key="image"
          class="absolute inset-0 bg-cover bg-center transition-opacity duration-[1800ms] ease-out"
          :class="currentSlide === index ? 'opacity-100' : 'opacity-0'"
          :style="{ backgroundImage: `url(${image})` }"
        ></div>
        <div class="absolute left-[-10%] top-[-10%] h-72 w-72 rounded-full bg-cyan-500/15 blur-3xl"></div>
        <div class="absolute bottom-[-10%] right-[-10%] h-80 w-80 rounded-full bg-emerald-400/15 blur-3xl"></div>
        <div class="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(255,255,255,0.08),_transparent_45%)]"></div>
        <div class="absolute inset-0 bg-slate-950/65"></div>
      </div>

      <div class="relative z-10 w-full max-w-5xl">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from "vue";
import trinidadImage from "../../images/trinidad.jpg";
import caribbeanImage from "../../images/carib-bkg.jpg";
import islandImage from "../../images/island-bkg.jpg";
import homePromoBannerImage from "../../images/home-promo-banner.jpg";

const authBackgrounds = [
  trinidadImage,
  caribbeanImage,
  islandImage,
  homePromoBannerImage,
];

const currentSlide = ref(0);

let slideInterval = null;
let reducedMotionQuery = null;

onMounted(() => {
  reducedMotionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  reducedMotionQuery.addEventListener("change", handleReducedMotionChange);
  if (!reducedMotionQuery.matches) {
    startCarousel();
  }
});

onUnmounted(() => {
  stopCarousel();
  reducedMotionQuery?.removeEventListener("change", handleReducedMotionChange);
});

function startCarousel() {
  stopCarousel();
  slideInterval = window.setInterval(() => {
    currentSlide.value = (currentSlide.value + 1) % authBackgrounds.length;
  }, 6000);
}

function stopCarousel() {
  if (slideInterval !== null) {
    window.clearInterval(slideInterval);
    slideInterval = null;
  }
}

function handleReducedMotionChange(event) {
  if (event.matches) {
    stopCarousel();
    currentSlide.value = 0;
    return;
  }

  startCarousel();
}
</script>
