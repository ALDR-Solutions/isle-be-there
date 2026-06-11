<template>
  <div class="min-h-screen bg-slate-50">
    <div class="border-b border-slate-200 bg-white">
      <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <p class="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-600">
          Admin Panel
        </p>
        <h1 class="mt-3 text-3xl font-bold text-slate-900 sm:text-4xl">
          Pricing Settings
        </h1>
        <p class="mt-3 max-w-3xl text-sm text-slate-500">
          Manage the global booking service fee and the package discount used for bulk itinerary bookings.
          These values are stored as fractions in the API and shown here as normal percentages.
        </p>
      </div>
    </div>

    <div class="mx-auto max-w-7xl space-y-8 px-4 py-10 sm:px-6 lg:px-8">
      <div
        v-if="loading"
        class="rounded-3xl border border-slate-200 bg-white px-6 py-16 text-center shadow-sm"
      >
        <svg
          class="mx-auto h-8 w-8 animate-spin text-cyan-500"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
        </svg>
        <p class="mt-4 text-sm text-slate-500">Loading current admin settings...</p>
      </div>

      <div
        v-else-if="loadError"
        class="rounded-3xl border border-red-200 bg-white px-6 py-8 text-center shadow-sm"
      >
        <p class="text-sm font-semibold text-red-600">{{ loadError }}</p>
        <button
          @click="loadSettings"
          class="mt-4 rounded-2xl bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800"
        >
          Retry
        </button>
      </div>

      <template v-else>
        <div
          v-if="hasMultipleManagedRecords"
          class="rounded-3xl border border-amber-200 bg-amber-50 px-6 py-5 shadow-sm"
        >
          <p class="text-sm font-semibold text-amber-700">
            Multiple active global pricing or package discount records were found.
          </p>
          <p class="mt-2 text-sm leading-6 text-amber-700/90">
            This page is using the first active record for each setting in line with the current v1 admin flow.
            If you want full multi-config management later, we can add that as a separate admin feature.
          </p>
        </div>

        <form @submit.prevent="saveSettings" class="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <section class="space-y-6">
            <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-[0.25em] text-cyan-600">
                Global Booking Fee
              </p>
              <h2 class="mt-3 text-2xl font-bold text-slate-900">Service fee percentage</h2>
              <p class="mt-2 text-sm leading-6 text-slate-500">
                This fee applies to booking totals across the platform. The backend stores this as a fractional value,
                but you can edit it here as a normal percentage like <span class="font-semibold text-slate-700">10</span>.
              </p>

              <label class="mt-6 block">
                <span class="text-sm font-semibold text-slate-700">Service fee (%)</span>
                <input
                  v-model.number="serviceFeePercent"
                  type="number"
                  min="0"
                  max="100"
                  step="0.01"
                  class="mt-2 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-medium text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100"
                />
              </label>

              <div class="mt-6 rounded-2xl bg-slate-50 p-4 text-sm text-slate-600">
                <p>
                  Active API value:
                  <span class="font-semibold text-slate-900">{{ formatFraction(serviceFeeFractionPreview) }}</span>
                </p>
                <p class="mt-1">
                  Managed config:
                  <span class="font-semibold text-slate-900">
                    {{ managedPricingConfig ? 'Existing global config' : 'A new global config will be created on save' }}
                  </span>
                </p>
              </div>
            </article>

            <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-[0.25em] text-cyan-600">
                Bulk Booking Discount
              </p>
              <h2 class="mt-3 text-2xl font-bold text-slate-900">Package discount percentage</h2>
              <p class="mt-2 text-sm leading-6 text-slate-500">
                This is the single active package discount used for eligible itinerary bulk bookings.
                The discount is applied automatically when the itinerary qualifies.
              </p>

              <label class="mt-6 block">
                <span class="text-sm font-semibold text-slate-700">Discount (%)</span>
                <input
                  v-model.number="discountPercent"
                  type="number"
                  min="1"
                  max="50"
                  step="0.01"
                  class="mt-2 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-medium text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100"
                />
              </label>

              <div class="mt-6 rounded-2xl bg-slate-50 p-4 text-sm text-slate-600">
                <p>
                  Active API value:
                  <span class="font-semibold text-slate-900">{{ formatFraction(discountFractionPreview) }}</span>
                </p>
                <p class="mt-1">
                  Managed discount:
                  <span class="font-semibold text-slate-900">
                    {{ managedPackageDiscount ? managedPackageDiscount.name || 'Package Discount' : 'A new package discount will be created on save' }}
                  </span>
                </p>
              </div>
            </article>
          </section>

          <aside class="space-y-6">
            <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-400">
                Save Changes
              </p>
              <h2 class="mt-3 text-xl font-bold text-slate-900">Apply updated pricing</h2>
              <p class="mt-2 text-sm leading-6 text-slate-500">
                Saving here updates the global fee used in booking totals and the active package discount used in bulk booking.
              </p>

              <div class="mt-6 space-y-3 rounded-2xl bg-slate-950 p-5 text-white">
                <div class="flex items-center justify-between gap-4">
                  <span class="text-sm text-slate-300">Service fee</span>
                  <span class="text-lg font-bold">{{ formatPercent(serviceFeePercent) }}</span>
                </div>
                <div class="flex items-center justify-between gap-4">
                  <span class="text-sm text-slate-300">Package discount</span>
                  <span class="text-lg font-bold">{{ formatPercent(discountPercent) }}</span>
                </div>
              </div>

              <button
                type="submit"
                :disabled="saving"
                class="mt-6 w-full rounded-2xl bg-cyan-500 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {{ saving ? 'Saving...' : 'Save settings' }}
              </button>
            </div>

            <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-400">
                Current Scope
              </p>
              <div class="mt-4 space-y-3 text-sm leading-6 text-slate-500">
                <p>This page manages one global service fee configuration.</p>
                <p>This page manages one active package discount record.</p>
                <p>Per-business-type pricing and multi-discount management are intentionally out of scope for this v1 screen.</p>
              </div>
            </div>
          </aside>
        </form>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';

import { discountsAPI, pricingAPI } from '../services/api';
import { useToastStore } from '../stores/toast';

const DEFAULT_SERVICE_FEE_PERCENT = 10;
const DEFAULT_PACKAGE_DISCOUNT_PERCENT = 10;

const toastStore = useToastStore();

const loading = ref(true);
const saving = ref(false);
const loadError = ref('');

const pricingConfigs = ref([]);
const packageDiscounts = ref([]);
const serviceFeePercent = ref(DEFAULT_SERVICE_FEE_PERCENT);
const discountPercent = ref(DEFAULT_PACKAGE_DISCOUNT_PERCENT);

const globalActiveConfigs = computed(() =>
  pricingConfigs.value.filter((config) => isActivePricingConfig(config) && config.business_type_id == null),
);

const managedPricingConfig = computed(() => globalActiveConfigs.value[0] ?? null);
const managedPackageDiscount = computed(() => packageDiscounts.value[0] ?? null);

const hasMultipleManagedRecords = computed(
  () => globalActiveConfigs.value.length > 1 || packageDiscounts.value.length > 1,
);

const serviceFeeFractionPreview = computed(() => toFraction(serviceFeePercent.value));
const discountFractionPreview = computed(() => toFraction(discountPercent.value));

function normalizeFractionalPercent(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return 0;
  if (numeric > 1) return numeric / 100;
  return Math.max(numeric, 0);
}

function toWholePercent(value, fallback) {
  const fraction = normalizeFractionalPercent(value);
  return Number.isFinite(fraction) ? Number((fraction * 100).toFixed(2)) : fallback;
}

function toFraction(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return 0;
  return Number((numeric / 100).toFixed(4));
}

function isActivePricingConfig(config) {
  if (!config?.is_active || !config?.effective_from) return false;

  const now = new Date();
  const effectiveFrom = new Date(config.effective_from);
  const effectiveTo = config.effective_to ? new Date(config.effective_to) : null;

  if (Number.isNaN(effectiveFrom.getTime())) return false;
  if (effectiveFrom > now) return false;
  if (effectiveTo && !Number.isNaN(effectiveTo.getTime()) && effectiveTo < now) return false;

  return true;
}

function formatPercent(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return '-';
  return `${numeric.toFixed(2).replace(/\.00$/, '')}%`;
}

function formatFraction(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return '-';
  return numeric.toFixed(4).replace(/0+$/, '').replace(/\.$/, '');
}

function validationError() {
  if (!Number.isFinite(serviceFeePercent.value) || serviceFeePercent.value < 0 || serviceFeePercent.value > 100) {
    return 'Service fee must be between 0% and 100%.';
  }
  if (!Number.isFinite(discountPercent.value) || discountPercent.value < 1 || discountPercent.value > 50) {
    return 'Package discount must be between 1% and 50%.';
  }
  return '';
}

function hydrateFormValues() {
  serviceFeePercent.value = managedPricingConfig.value
    ? toWholePercent(managedPricingConfig.value.service_fee_percent, DEFAULT_SERVICE_FEE_PERCENT)
    : DEFAULT_SERVICE_FEE_PERCENT;

  discountPercent.value = managedPackageDiscount.value
    ? toWholePercent(managedPackageDiscount.value.discount_percent, DEFAULT_PACKAGE_DISCOUNT_PERCENT)
    : DEFAULT_PACKAGE_DISCOUNT_PERCENT;
}

async function loadSettings() {
  loading.value = true;
  loadError.value = '';

  const [pricingResult, discountResult] = await Promise.allSettled([
    pricingAPI.listConfigs(),
    discountsAPI.getPackageDiscounts(),
  ]);

  if (pricingResult.status === 'rejected') {
    loadError.value = pricingResult.reason?.response?.data?.detail || 'Failed to load pricing settings.';
    toastStore.show(loadError.value, 'error');
    loading.value = false;
    return;
  }

  if (discountResult.status === 'rejected') {
    loadError.value = discountResult.reason?.response?.data?.detail || 'Failed to load discount settings.';
    toastStore.show(loadError.value, 'error');
    loading.value = false;
    return;
  }

  pricingConfigs.value = Array.isArray(pricingResult.value.data) ? pricingResult.value.data : [];
  packageDiscounts.value = Array.isArray(discountResult.value.data) ? discountResult.value.data : [];
  hydrateFormValues();
  loading.value = false;
}

async function saveSettings() {
  const error = validationError();
  if (error) {
    toastStore.show(error, 'error');
    return;
  }

  saving.value = true;

  try {
    const pricingPayload = managedPricingConfig.value
      ? {
          business_type_id: managedPricingConfig.value.business_type_id ?? null,
          service_fee_percent: toFraction(serviceFeePercent.value),
          is_active: managedPricingConfig.value.is_active ?? true,
          effective_from: managedPricingConfig.value.effective_from,
          effective_to: managedPricingConfig.value.effective_to ?? null,
        }
      : {
          business_type_id: null,
          service_fee_percent: toFraction(serviceFeePercent.value),
          is_active: true,
          effective_from: new Date().toISOString(),
          effective_to: null,
        };

    if (managedPricingConfig.value?.id) {
      await pricingAPI.updateConfig(managedPricingConfig.value.id, pricingPayload);
    } else {
      await pricingAPI.createConfig(pricingPayload);
    }

    if (managedPackageDiscount.value?.id) {
      await discountsAPI.update(managedPackageDiscount.value.id, {
        discount_percent: toFraction(discountPercent.value),
        is_active: true,
      });
    } else {
      await discountsAPI.create({
        name: 'Package Discount',
        discount_type: 'package',
        discount_percent: toFraction(discountPercent.value),
        min_services: 2,
        is_active: true,
        valid_from: new Date().toISOString(),
        valid_to: null,
        description: 'Automatically applied to eligible itinerary bulk bookings.',
      });
    }

    toastStore.show('Admin pricing settings updated.', 'success');
    await loadSettings();
  } catch (error) {
    toastStore.show(
      error.response?.data?.detail || 'Failed to save admin pricing settings.',
      'error',
    );
  } finally {
    saving.value = false;
  }
}

onMounted(() => {
  loadSettings();
});
</script>
