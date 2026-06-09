<template>
  <div class="bg-slate-50 text-slate-900">
    <section
      class="hero-premium relative -mt-20 flex min-h-screen w-full items-center overflow-hidden pt-20"
    >
      <template v-if="showVideoHero">
        <video
          autoplay
          muted
          loop
          playsinline
          preload="metadata"
          :poster="heroPosterImage"
          class="absolute inset-0 h-full w-full object-cover"
          @error="showVideoHero = false"
        >
          <source :src="droneBeachHeroVideo" type="video/mp4" />
        </video>
      </template>
      <div
        v-else
        class="absolute inset-0 bg-cover bg-center"
        :style="{ backgroundImage: `url(${heroPosterImage})` }"
      ></div>
      <div class="absolute inset-0 bg-slate-950/60"></div>
      <div
        class="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(34,211,238,0.18),_transparent_40%)]"
      ></div>
      <div
        class="hero-gradient-overlay absolute inset-0"
      ></div>
      <div
        class="hero-glow hero-glow-aqua absolute left-[-10%] top-[12%] h-[24rem] w-[24rem] rounded-full"
      ></div>
      <div
        class="hero-glow hero-glow-sand absolute right-[-8%] top-[18%] h-[20rem] w-[20rem] rounded-full"
      ></div>
      <div
        class="hero-glow hero-glow-lagoon absolute bottom-[-8%] left-[12%] h-[18rem] w-[18rem] rounded-full"
      ></div>

      <div
        class="relative z-10 mx-auto flex w-full max-w-7xl items-center justify-center px-4 sm:px-6 lg:px-8">
        <div class="hero-copy-shell flex max-w-3xl flex-col items-center text-center">
          <p
            class="hero-reveal hero-reveal-1 hero-kicker inline-flex items-center rounded-full border border-white/15 bg-white/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.32em] text-cyan-100 backdrop-blur-md sm:text-sm">
            Caribbean travel, Simplified for you
          </p>
          <h1
            class="hero-reveal hero-reveal-2 hero-title mt-5 text-4xl font-bold leading-tight text-white drop-shadow-lg sm:text-5xl lg:text-7xl">
            Plan Your Island Adventure Trip Today.
          </h1>

          <p
            class="hero-reveal hero-reveal-3 mt-6 max-w-2xl text-base leading-7 text-slate-100/90 sm:text-lg">
            Search stays and experiences, then shape them into a trip that
            feels clear from the first idea to the final booking.
          </p>

          <div class="hero-reveal hero-reveal-4 mt-10 w-full max-w-4xl">
            <div
              class="hero-search-panel flex flex-col gap-4 rounded-[2rem] border border-white/20 bg-white/[0.12] p-3 shadow-[0_28px_80px_rgba(15,23,42,0.3)] backdrop-blur-2xl sm:flex-row sm:items-center">
              <div
                class="hero-search-input-wrap flex min-w-0 flex-1 items-center gap-3 rounded-[1.4rem] border border-white/10 bg-slate-950/20 px-4 py-3 text-white">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-5 w-5 shrink-0 text-cyan-300"
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
                  v-model="searchQuery"
                  type="text"
                  placeholder="Search stays, beaches, restaurants, or tours"
                  class="w-full bg-transparent text-sm text-white placeholder:text-slate-300/80 focus:outline-none sm:text-base"
                  @keyup.enter="submitSearch"/>
              </div>

              <div class="flex gap-3 sm:contents">
                <button
                  type="button"
                  @click="submitSearch"
                  class="hero-primary-cta inline-flex flex-1 items-center justify-center rounded-2xl bg-cyan-300 px-4 py-2.5 text-sm font-semibold text-slate-950 transition hover:-translate-y-0.5 hover:bg-cyan-200 sm:flex-none sm:px-7 sm:py-4">
                  Search stays
                </button>

                <router-link
                  :to="{ name: 'ItineraryPlanner' }"
                  class="hero-secondary-cta inline-flex flex-1 items-center justify-center rounded-2xl border border-white/20 bg-white/10 px-4 py-2.5 text-sm font-semibold text-white backdrop-blur-md transition hover:-translate-y-0.5 hover:bg-white/15 sm:flex-none sm:px-8 sm:py-4">
                  Build itinerary
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>

    </section>

    <section class="px-4 pt-14 pb-8 sm:px-6 sm:pt-20 sm:pb-10 lg:px-8">
      <div class="mx-auto max-w-7xl">
        <div
          class="mb-8 flex flex-col items-start justify-between gap-6 lg:mb-12 lg:flex-row lg:items-end">
          <div class="max-w-2xl">
            <p
              class="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-600">
              {{ discoveryEyebrow }}
            </p>
            <h2 class="mt-3 text-3xl font-bold text-slate-900 sm:text-4xl">
              {{ discoveryTitle }}
            </h2>
            <p class="mt-4 text-base leading-7 text-slate-600">
              {{ discoveryBody }}
            </p>
          </div>

          <div class="hidden items-center gap-3 sm:flex">
            <button
              type="button"
              :aria-label="'Show previous listing'"
              @click="prevSlide"
              :disabled="carouselIndex === 0"
              class="flex h-12 w-12 items-center justify-center rounded-2xl border border-slate-200 bg-white text-slate-700 shadow-sm transition hover:-translate-y-0.5 hover:border-slate-300 hover:text-slate-950 disabled:cursor-not-allowed disabled:opacity-40">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 19l-7-7 7-7"/>
              </svg>
            </button>

            <button
              type="button"
              :aria-label="'Show next listing'"
              @click="nextSlide"
              :disabled="carouselIndex >= maxIndex"
              class="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-900 text-white shadow-lg shadow-slate-900/10 transition hover:-translate-y-0.5 hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-300">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5l7 7-7 7"/>
              </svg>
            </button>
          </div>
        </div>

        <div
          v-if="loading"
          class="rounded-[2rem] border border-slate-200 bg-white px-6 py-16 text-center shadow-sm">
          <svg
            class="mx-auto h-8 w-8 animate-spin text-cyan-500"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24">
            <circle
              class="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              stroke-width="4"/>
            <path
              class="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"/>
          </svg>
          <p class="mt-4 text-sm font-medium text-slate-500">
            Loading suggestions for you...
          </p>
        </div>

        <div
          v-else-if="personalizedListings.length === 0"
          class="rounded-[2rem] border border-slate-200 bg-white px-6 py-14 text-center shadow-sm">
          <p class="text-lg font-semibold text-slate-900">
            {{
              listingsLoadFailed
                ? "We couldn't load suggestions right now."
                : "Nothing has been added here yet."
            }}
          </p>
          <p class="mt-3 text-sm leading-6 text-slate-500">
            {{
              listingsLoadFailed
                ? "Try again in a moment, or browse the full listings page instead."
                : "You can still browse every available stay and experience from the listings page."
            }}
          </p>
          <div class="mt-6 flex flex-wrap justify-center gap-3">
            <button
              v-if="listingsLoadFailed"
              type="button"
              @click="fetchPersonalizedListings"
              class="rounded-2xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100">
              Try again
            </button>
            <router-link
              :to="{ name: 'Listings' }"
              class="rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800">
              View listings
            </router-link>
          </div>
        </div>

        <div v-else class="space-y-5">
          <div
            class="rounded-[2rem] border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
            <div
              class="overflow-hidden"
              role="region"
              aria-label="Suggested places"
              @touchstart.passive="onTouchStart"
              @touchend.passive="onTouchEnd">
              <div
                ref="trackRef"
                class="flex gap-6 transition-transform duration-500 ease-out"
                :style="{ transform: `translateX(-${carouselOffset}px)` }">
                <div
                  v-for="listing in personalizedListings"
                  :key="listing.id"
                  class="shrink-0"
                  :style="{ width: `${cardWidth}px` }">
                  <DestinationCard :listing="listing" />
                </div>
              </div>
            </div>
          </div>

          <div
            class="flex flex-col gap-3 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between">
            
            <router-link
              :to="{ name: 'Listings' }"
              class="font-semibold text-cyan-700 transition hover:text-cyan-800">
              Browse all listings
            </router-link>
          </div>
        </div>
      </div>
    </section>

    <section class="bg-white px-4 pt-8 pb-14 sm:px-6 sm:pt-10 sm:pb-16 lg:px-8">
      <div class="mx-auto max-w-7xl">
        <div class="max-w-2xl">
          <p
            class="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-600">
            Quick paths
          </p>
          <h2 class="mt-3 text-3xl font-bold text-slate-900 sm:text-4xl">
            Start with what matters most.
          </h2>
          <p class="mt-4 text-base leading-7 text-slate-600">
            Choose a direction first, then narrow your trip from there.
          </p>
        </div>

        <div class="mt-10 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
          <router-link
            v-for="shortcut in categoryShortcuts"
            :key="shortcut.title"
            :to="{ name: 'Listings', query: { category: shortcut.category } }"
            class="group rounded-[1.75rem] border border-slate-200 bg-slate-50 p-6 transition hover:-translate-y-1 hover:border-slate-300 hover:bg-white hover:shadow-lg">
            <p class="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-700">
              {{ shortcut.eyebrow }}
            </p>
            <h3 class="mt-3 text-xl font-bold text-slate-900">
              {{ shortcut.title }}
            </h3>
            <p class="mt-3 text-sm leading-6 text-slate-600">
              {{ shortcut.description }}
            </p>
            <div
              class="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-slate-900">
              View options
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4 transition group-hover:translate-x-1"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5l7 7-7 7"/>
              </svg>
            </div>
          </router-link>
        </div>
      </div>
    </section>

    <section
      class="relative my-14 flex min-h-[26rem] w-full items-center overflow-hidden sm:my-16 sm:min-h-[30rem] lg:min-h-[34rem]"
    >
      <div
        class="absolute inset-0 bg-cover bg-center bg-no-repeat md:bg-fixed"
        :style="{ backgroundImage: `url(${promoBannerImage})` }"
      ></div>
      <div class="absolute inset-0 bg-slate-950/45"></div>
      <div
        class="absolute inset-0 bg-[linear-gradient(90deg,rgba(15,23,42,0.82)_0%,rgba(15,23,42,0.5)_38%,rgba(15,23,42,0.18)_100%)]"
      ></div>

      <div class="relative z-10 mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="max-w-2xl py-16 sm:py-20 lg:py-24">
          <p class="text-sm font-semibold uppercase tracking-[0.32em] text-white/80">
            Special Promo
          </p>
          <h2 class="mt-4 text-4xl font-bold leading-tight text-white sm:text-5xl lg:text-6xl">
            Build your itinerary with us and get 10% off.
          </h2>
          <p class="mt-5 max-w-xl text-base leading-7 text-slate-100 sm:text-lg">
            Use the itinerary builder to shape your trip in one place, then unlock a limited-time
            discount before you book.
          </p>
          <router-link
            :to="{ name: 'ItineraryPlanner' }"
            class="mt-8 inline-flex items-center justify-center rounded-2xl bg-cyan-300 px-6 py-3 text-sm font-semibold uppercase tracking-[0.18em] text-slate-950 transition hover:-translate-y-0.5 hover:bg-red-400 focus:outline-none focus:ring-2 focus:ring-red-200 focus:ring-offset-2 focus:ring-offset-slate-900 sm:px-7 sm:py-4">
            Build Your Itinerary
          </router-link>
        </div>
      </div>
    </section>

    <section class="px-4 py-10 sm:px-6W lg:px-8">
      <div class="mx-auto max-w-7xl">
        <div class="overflow-hidden rounded-[2rem] border border-slate-200 bg-slate-900 text-white shadow-2xl shadow-slate-900/10">
          <div class="bg-[radial-gradient(circle_at_top_left,_rgba(34,211,238,0.18),_transparent_35%),linear-gradient(135deg,_rgba(15,23,42,1),_rgba(30,41,59,0.98))] px-6 py-14 sm:px-8 lg:px-10">
            <div
              class="flex flex-col gap-10 lg:flex-row lg:items-start lg:justify-between"
            >
              <div class="max-w-2xl">
                <p class="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-300">
                  Continue your trip
                </p>
                <h2 class="mt-4 text-3xl font-bold sm:text-4xl">
                  {{ authStore.isAuthenticated ? "Pick up where you left off." : "Save your trip ideas for later." }}
                </h2>
                <p class="mt-4 max-w-2xl text-base leading-7 text-slate-300 sm:text-lg">
                  {{
                    authStore.isAuthenticated
                      ? "Jump back into the parts of the platform that help you keep planning without starting over."
                      : "Create an account to keep your favourite places, return to your itinerary, and manage bookings in one place."
                  }}
                </p>
              </div>

              <div
                v-if="authStore.isAuthenticated"
                class="grid w-full gap-4 lg:max-w-3xl lg:grid-cols-3"
              >
                <router-link
                  v-for="action in tripPlanningActions"
                  :key="action.title"
                  :to="{ name: action.routeName }"
                  class="group flex h-full flex-col rounded-[1.5rem] border border-white/10 bg-white/5 p-6 backdrop-blur-sm transition hover:-translate-y-1 hover:border-cyan-300/40 hover:bg-white/10"
                >
                  <span class="inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-cyan-300/15 text-cyan-200">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      class="h-5 w-5"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="1.8"
                        :d="action.iconPath"
                      />
                    </svg>
                  </span>
                  <p class="mt-5 text-lg font-bold text-white">
                    {{ action.title }}
                  </p>
                  <p class="mt-3 flex-1 text-sm leading-6 text-slate-300">
                    {{ action.description }}
                  </p>
                  <div class="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-cyan-200">
                    {{ action.cta }}
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      class="h-4 w-4 transition group-hover:translate-x-1"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M9 5l7 7-7 7"
                      />
                    </svg>
                  </div>
                </router-link>
              </div>

              <div
                v-else
                class="w-full rounded-[1.75rem] border border-white/10 bg-white/5 p-6 backdrop-blur-sm lg:max-w-xl"
              >
                <p class="text-sm font-semibold uppercase tracking-[0.22em] text-cyan-200">
                  Travel account
                </p>
                <div class="mt-5 space-y-4">
                  <div
                    v-for="benefit in guestPlanningBenefits"
                    :key="benefit"
                    class="flex items-start gap-3 text-sm leading-6 text-slate-200"
                  >
                    <span class="mt-1 h-2.5 w-2.5 rounded-full bg-cyan-300"></span>
                    <span>{{ benefit }}</span>
                  </div>
                </div>
                <div class="mt-8 flex flex-col gap-3 sm:flex-row">
                  <router-link
                    :to="{ name: 'Register' }"
                    class="inline-flex items-center justify-center rounded-2xl bg-cyan-300 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:-translate-y-0.5 hover:bg-cyan-200"
                  >
                    Create account
                  </router-link>
                  <router-link
                    :to="{ name: 'Login' }"
                    class="inline-flex items-center justify-center rounded-2xl border border-white/15 bg-white/5 px-6 py-3 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-white/10"
                  >
                    Sign in
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <InterestsModal
      v-if="showInterestsModal"
      @close="showInterestsModal = false"
      @interests-saved="onInterestsSaved"/>
  </div>
</template>

<script setup>
import {
  ref,
  computed,
  onMounted,
  onUnmounted,
  nextTick,
  watch,
} from "vue";
import { useRouter } from "vue-router";
import { listingsAPI } from "../services/api";
import { useAuthStore } from "../stores/auth";
import { useFavouritesStore } from "../stores/favourites";
import DestinationCard from "../components/DestinationCard.vue";
import InterestsModal from "../components/interestsModal.vue";
import beachImage from "../../images/beach-bkg.jpg";
import promoBannerImage from "../../images/home-promo-banner.jpg";
import droneBeachHeroVideo from "../../clips/drone_beach.mp4";

const authStore = useAuthStore();
const favouritesStore = useFavouritesStore();
const router = useRouter();

const heroPosterImage = beachImage;

const categoryShortcuts = [
  {
    eyebrow: "Stay well",
    title: "Hotels",
    description: "Start with places to stay, from quick resort breaks to longer villa stays.",
    category: "hotel",
  },
  {
    eyebrow: "Local food",
    title: "Restaurants",
    description: "Find places to eat when food is one of the main reasons for the trip.",
    category: "restaurant",
  },
  {
    eyebrow: "Guided plans",
    title: "Tours",
    description: "Browse guided experiences, day trips, and planned ways to explore the island.",
    category: "tour",
  },
  {
    eyebrow: "Get outside",
    title: "Activities",
    description: "See active experiences and one-off things to do when you want more flexibility.",
    category: "activity",
  },
];

const tripPlanningActions = [
  {
    title: "Saved listings",
    description: "Reopen the stays and experiences you marked so you can compare options faster.",
    cta: "View saved places",
    routeName: "Favourites",
    iconPath: "M5.121 19.364A9 9 0 1118.88 6.636L12 21l-6.879-1.636z",
  },
  {
    title: "Itinerary planner",
    description: "Return to your trip flow and keep shaping the route around the ideas you like most.",
    cta: "Open planner",
    routeName: "ItineraryPlanner",
    iconPath: "M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z",
  },
  {
    title: "Bookings",
    description: "Check upcoming reservations, pending requests, and confirmed plans in one place.",
    cta: "See bookings",
    routeName: "Bookings",
    iconPath: "M9 12l2 2 4-4m5 2a9 9 0 11-18 0 9 9 0 0118 0z",
  },
];

const guestPlanningBenefits = [
  "Save listings you want to come back to without searching again.",
  "Keep your itinerary work in one place as the trip starts to take shape.",
  "Manage reservations and trip details once you are ready to book.",
];

const loading = ref(true);
const listingsLoadFailed = ref(false);
const personalizedListings = ref([]);
const searchQuery = ref("");
const showVideoHero = ref(true);

const trackRef = ref(null);
const carouselIndex = ref(0);
const cardWidth = ref(350);
const visibleCards = ref(3);
const gap = 24;

const showInterestsModal = ref(false);
let interestsPromptTimeout = null;
let interestsPromptQueued = false;
let reducedMotionMediaQuery = null;

const discoveryEyebrow = computed(() =>
  authStore.isAuthenticated ? "Tailored picks" : "Where to start",
);

const discoveryTitle = computed(() =>
  authStore.isAuthenticated
    ? "A short list worth opening first."
    : "A good place to begin.",
);

const discoveryBody = computed(() =>
  authStore.isAuthenticated
    ? "These suggestions use your interest so the page gets you to better options faster."
    : "Start with a small set of places to stay and things to do, then open the ones that feel right for your trip.",
);

const maxIndex = computed(() =>
  Math.max(0, personalizedListings.value.length - visibleCards.value),
);

const carouselOffset = computed(
  () => carouselIndex.value * (cardWidth.value + gap),
);

watch(
  () => authStore.isAuthenticated,
  (isAuthenticated, wasAuthenticated) => {
    if (isAuthenticated !== wasAuthenticated) {
      fetchPersonalizedListings();
    }
  },
);

watch(
  () => authStore.isAuthenticated,
  (isAuthenticated) => {
    if (isAuthenticated && !favouritesStore.loaded) {
      favouritesStore.fetchAll().catch((err) => {
        console.error("Failed to load favourites", err);
      });
    }
  },
  { immediate: true },
);

watch(
  () => authStore.shouldPromptForInterests,
  (shouldPrompt) => {
    if (!shouldPrompt || interestsPromptQueued) return;

    interestsPromptQueued = true;
    interestsPromptTimeout = window.setTimeout(() => {
      showInterestsModal.value = true;
    }, 700);
  },
  { immediate: true },
);

onMounted(() => {
  reducedMotionMediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  showVideoHero.value = !reducedMotionMediaQuery.matches;
  reducedMotionMediaQuery.addEventListener("change", handleReducedMotionChange);
  fetchPersonalizedListings();
  window.addEventListener("resize", updateCardWidth);
  updateCardWidth();
});

onUnmounted(() => {
  window.clearTimeout(interestsPromptTimeout);
  reducedMotionMediaQuery?.removeEventListener("change", handleReducedMotionChange);
  window.removeEventListener("resize", updateCardWidth);
});

function handleReducedMotionChange(event) {
  showVideoHero.value = !event.matches;
}

function onInterestsSaved() {
  fetchPersonalizedListings();
}

function submitSearch() {
  const q = searchQuery.value.trim();
  router.push({
    name: "Listings",
    query: q ? { q } : {},
  });
}

async function fetchPersonalizedListings() {
  loading.value = true;
  listingsLoadFailed.value = false;

  try {
    if (!authStore.isAuthenticated) {
      const response = await listingsAPI.getAll({ limit: 20 });
      personalizedListings.value = response.data;
      return;
    }

    const response = await listingsAPI.getPersonalized({ limit: 20 });
    personalizedListings.value = response.data;
  } catch (e) {
    if (e?.response?.status === 401) {
      try {
        const response = await listingsAPI.getAll({ limit: 20 });
        personalizedListings.value = response.data;
        return;
      } catch (fallbackError) {
        listingsLoadFailed.value = true;
        personalizedListings.value = [];
        console.error("Failed to load fallback listings", fallbackError);
      }
    } else {
      listingsLoadFailed.value = true;
      personalizedListings.value = [];
      console.error("Failed to load personalized listings", e);
    }
  } finally {
    loading.value = false;
    nextTick(() => updateCardWidth());
  }
}

function getVisibleCount() {
  if (window.innerWidth <= 640) return 1;
  if (window.innerWidth <= 1080) return 2;
  return 3;
}

function updateCardWidth() {
  const containerWidth = trackRef.value?.parentElement?.offsetWidth || 900;
  const count = getVisibleCount();
  visibleCards.value = count;
  cardWidth.value = Math.max(0, (containerWidth - gap * (count - 1)) / count);

  if (carouselIndex.value > maxIndex.value) {
    carouselIndex.value = maxIndex.value;
  }
}

function prevSlide() {
  if (carouselIndex.value > 0) carouselIndex.value--;
}

function nextSlide() {
  if (carouselIndex.value < maxIndex.value) carouselIndex.value++;
}

let touchStartX = 0;

function onTouchStart(e) {
  touchStartX = e.touches[0].clientX;
}

function onTouchEnd(e) {
  const delta = touchStartX - e.changedTouches[0].clientX;
  if (Math.abs(delta) < 50) return;
  if (delta > 0) nextSlide();
  else prevSlide();
}
</script>

<style scoped>
input::placeholder {
  letter-spacing: 0.01em;
}

.hero-premium {
  isolation: isolate;
}

.hero-gradient-overlay {
  background:
    radial-gradient(circle at 20% 18%, rgba(94, 234, 212, 0.14), transparent 28%),
    radial-gradient(circle at 80% 22%, rgba(251, 191, 153, 0.12), transparent 24%),
    linear-gradient(180deg, rgba(15, 23, 42, 0.1) 0%, rgba(15, 23, 42, 0.45) 100%);
}

.hero-glow {
  pointer-events: none;
  opacity: 0.38;
  filter: blur(22px);
  mix-blend-mode: screen;
}

.hero-glow-aqua {
  background: radial-gradient(circle, rgba(110, 231, 255, 0.32) 0%, rgba(110, 231, 255, 0.08) 42%, transparent 72%);
  animation: heroGlowDriftA 18s ease-in-out infinite;
}

.hero-glow-sand {
  background: radial-gradient(circle, rgba(253, 186, 116, 0.26) 0%, rgba(253, 186, 116, 0.06) 40%, transparent 74%);
  animation: heroGlowDriftB 22s ease-in-out infinite;
}

.hero-glow-lagoon {
  background: radial-gradient(circle, rgba(45, 212, 191, 0.18) 0%, rgba(45, 212, 191, 0.05) 46%, transparent 74%);
  animation: heroGlowDriftC 20s ease-in-out infinite;
}

.hero-copy-shell {
  position: relative;
  animation: heroFloat 14s ease-in-out 1.3s infinite;
}

.hero-kicker {
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.16);
}

.hero-title {
  text-wrap: balance;
  text-shadow: 0 18px 40px rgba(15, 23, 42, 0.3);
}

.hero-reveal {
  opacity: 0;
  transform: translateY(24px) scale(0.985);
  filter: blur(10px);
  animation: heroReveal 0.95s cubic-bezier(0.22, 1, 0.36, 1) forwards;
  will-change: opacity, transform, filter;
}

.hero-reveal-1 {
  animation-delay: 0.12s;
}

.hero-reveal-2 {
  animation-delay: 0.26s;
}

.hero-reveal-3 {
  animation-delay: 0.42s;
}

.hero-reveal-4 {
  animation-delay: 0.56s;
}

.hero-search-panel {
  position: relative;
  overflow: hidden;
  box-shadow:
    0 30px 70px rgba(15, 23, 42, 0.28),
    inset 0 1px 0 rgba(255, 255, 255, 0.16);
  transition:
    transform 240ms ease,
    border-color 240ms ease,
    background-color 240ms ease,
    box-shadow 240ms ease;
}

.hero-search-panel::before {
  content: "";
  position: absolute;
  inset: 1px;
  border-radius: calc(2rem - 1px);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.16), rgba(255, 255, 255, 0.03) 45%, rgba(56, 189, 248, 0.08) 100%);
  pointer-events: none;
}

.hero-search-panel:hover,
.hero-search-panel:focus-within {
  transform: translateY(-3px);
  border-color: rgba(255, 255, 255, 0.28);
  background: rgba(255, 255, 255, 0.14);
  box-shadow:
    0 34px 90px rgba(15, 23, 42, 0.36),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.hero-search-input-wrap {
  position: relative;
  z-index: 1;
  transition:
    border-color 220ms ease,
    background-color 220ms ease,
    box-shadow 220ms ease;
}

.hero-search-input-wrap:focus-within {
  border-color: rgba(165, 243, 252, 0.45);
  background: rgba(15, 23, 42, 0.3);
  box-shadow: 0 0 0 1px rgba(165, 243, 252, 0.18);
}

.hero-primary-cta,
.hero-secondary-cta {
  position: relative;
  z-index: 1;
}

.hero-primary-cta {
  overflow: hidden;
}

.hero-primary-cta::after {
  content: "";
  position: absolute;
  inset: -120% auto -120% -35%;
  width: 40%;
  transform: rotate(18deg);
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.35), transparent);
  transition: transform 520ms ease;
}

.hero-primary-cta:hover::after,
.hero-primary-cta:focus-visible::after {
  transform: translateX(240%) rotate(18deg);
}

.hero-secondary-cta:hover,
.hero-secondary-cta:focus-visible {
  border-color: rgba(255, 255, 255, 0.3);
}

@keyframes heroReveal {
  0% {
    opacity: 0;
    transform: translateY(24px) scale(0.985);
    filter: blur(10px);
  }

  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
    filter: blur(0);
  }
}

@keyframes heroFloat {
  0%,
  100% {
    transform: translate3d(0, 0, 0);
  }

  50% {
    transform: translate3d(0, -6px, 0);
  }
}

@keyframes heroGlowDriftA {
  0%,
  100% {
    transform: translate3d(0, 0, 0) scale(1);
  }

  50% {
    transform: translate3d(18px, -14px, 0) scale(1.06);
  }
}

@keyframes heroGlowDriftB {
  0%,
  100% {
    transform: translate3d(0, 0, 0) scale(1);
  }

  50% {
    transform: translate3d(-22px, 16px, 0) scale(1.08);
  }
}

@keyframes heroGlowDriftC {
  0%,
  100% {
    transform: translate3d(0, 0, 0) scale(1);
  }

  50% {
    transform: translate3d(12px, -18px, 0) scale(1.04);
  }
}

@media (prefers-reduced-motion: reduce) {
  .hero-reveal,
  .hero-copy-shell,
  .hero-glow-aqua,
  .hero-glow-sand,
  .hero-glow-lagoon {
    animation: none;
    filter: none;
    opacity: 1;
    transform: none;
  }

  .hero-search-panel,
  .hero-search-input-wrap,
  .hero-primary-cta::after {
    transition: none;
  }
}
</style>
