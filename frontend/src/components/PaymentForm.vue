<template>
  <div class="rounded-3xl border border-slate-200 bg-white p-6">
    <div class="mb-4">
      <p class="text-sm font-semibold text-slate-700">Card Details</p>
      <p class="mt-1 text-xs text-slate-500">Enter your card information to complete the payment.</p>
    </div>

    <!-- Card Element Mount Point -->
    <div
      id="card-element"
      class="mb-4 min-h-[50px] rounded-xl border border-slate-200 bg-white p-4 transition focus-within:border-cyan-500 focus-within:ring-4 focus-within:ring-cyan-100"
    ></div>

    <!-- Error Message -->
    <div v-if="errorMessage" class="mb-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
      {{ errorMessage }}
    </div>

    <!-- Success Message -->
    <div v-if="successMessage" class="mb-4 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-600">
      {{ successMessage }}
    </div>

    <!-- Submit Button -->
    <button
      @click="handleSubmit"
      :disabled="processing || !stripeReady"
      class="w-full rounded-2xl py-3 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-50"
      :class="processing || !stripeReady ? 'bg-slate-200 text-slate-400' : 'bg-slate-900 text-white hover:bg-slate-800'"
    >
      {{ processing ? 'Processing payment...' : (stripeReady ? 'Pay' : 'Loading payment form...') }}
    </button>

    <p class="mt-3 text-center text-xs text-slate-400">
      <svg class="mr-1 inline-block h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
      </svg>
      Secured by Stripe
    </p>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { loadStripe } from '@stripe/stripe-js'
import { createPaymentIntent, confirmPayment } from '../services/payment'

const props = defineProps({
  bookingId: {
    type: String,
    required: true
  },
  clientSecret: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['payment-success', 'payment-error'])

const stripe = ref(null)
const elements = ref(null)
const cardElement = ref(null)
const processing = ref(false)
const stripeReady = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// Card element styling to match the app's design
const cardStyle = {
  base: {
    fontSize: '16px',
    color: '#334155',
    fontFamily: 'ui-sans-serif, system-ui, sans-serif',
    fontSmoothing: 'antialiased',
    '::placeholder': {
      color: '#94a3b8'
    }
  },
  invalid: {
    color: '#ef4444',
    iconColor: '#ef4444'
  }
}

async function initializeStripe() {
  try {
    // Load Stripe with publishable key
    const STRIPE_PUBLISHABLE_KEY = import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY

    console.log('Stripe key present:', !!STRIPE_PUBLISHABLE_KEY, STRIPE_PUBLISHABLE_KEY ? STRIPE_PUBLISHABLE_KEY.substring(0, 10) + '...' : 'none')

    if (!STRIPE_PUBLISHABLE_KEY || STRIPE_PUBLISHABLE_KEY === 'pk_test_your_stripe_publishable_key_here') {
      errorMessage.value = 'Stripe key not configured. Please set VITE_STRIPE_PUBLISHABLE_KEY in .env'
      stripeReady.value = false
      return
    }

    stripe.value = await loadStripe(STRIPE_PUBLISHABLE_KEY)

    if (!stripe.value) {
      errorMessage.value = 'Failed to load Stripe. Please refresh the page.'
      stripeReady.value = false
      return
    }

    // If no clientSecret provided via prop, fetch it
    let secret = props.clientSecret
    if (!secret) {
      try {
        const intentData = await createPaymentIntent(props.bookingId)
        secret = intentData.client_secret
      } catch (err) {
        errorMessage.value = 'Failed to create payment: ' + (err.message || 'Unknown error')
        stripeReady.value = false
        return
      }
    }

    // Create Elements instance with client secret
    elements.value = stripe.value.elements({ clientSecret: secret })

    // Create card element
    cardElement.value = elements.value.create('card', { style: cardStyle })

    // Mount to DOM after next tick to ensure DOM is ready
    await nextTick()
    cardElement.value.mount('#card-element')

    // Listen for change events to clear errors
    cardElement.value.on('change', (event) => {
      if (event.error) {
        errorMessage.value = event.error.message
      } else {
        errorMessage.value = ''
      }
    })

    stripeReady.value = true
  } catch (err) {
    console.error('Stripe initialization error:', err)
    errorMessage.value = 'Failed to load payment form. Please try again.'
  }
}

async function handleSubmit() {
  // Clear previous messages
  errorMessage.value = ''
  successMessage.value = ''

  if (!stripe.value || !cardElement.value) {
    errorMessage.value = 'Payment form is not ready. Please try again.'
    emit('payment-error', { error: errorMessage.value })
    return
  }

  processing.value = true

  try {
    // Get client secret - either from prop or stored
    let secret = props.clientSecret
    if (!secret) {
      const intentData = await createPaymentIntent(props.bookingId)
      secret = intentData.client_secret
    }

    const result = await stripe.value.confirmCardPayment(secret, {
      payment_method: {
        card: cardElement.value
      }
    })

    if (result.error) {
      errorMessage.value = result.error.message || 'Payment failed. Please try again.'
      emit('payment-error', { error: errorMessage.value })
    } else if (result.paymentIntent && result.paymentIntent.status === 'succeeded') {
      successMessage.value = 'Payment successful!'

      // Confirm payment on backend
      try {
        await confirmPayment(props.bookingId)
      } catch (confirmErr) {
        // Log but don't fail - payment already succeeded on Stripe
        console.warn('Backend payment confirmation failed:', confirmErr)
      }

      emit('payment-success', { paymentIntent: result.paymentIntent })
    }
  } catch (err) {
    console.error('Payment error:', err)
    errorMessage.value = 'An unexpected error occurred. Please try again.'
    emit('payment-error', { error: errorMessage.value })
  } finally {
    processing.value = false
  }
}

// Helper for next tick
function nextTick() {
  return new Promise(resolve => setTimeout(resolve, 0))
}

onMounted(() => {
  initializeStripe()
})

onUnmounted(() => {
  // Clean up card element
  if (cardElement.value) {
    cardElement.value.destroy()
    cardElement.value = null
  }
})

// Watch for clientSecret prop changes
watch(() => props.clientSecret, async (newSecret) => {
  if (newSecret && stripe.value && !elements.value) {
    elements.value = stripe.value.elements({ clientSecret: newSecret })
    cardElement.value = elements.value.create('card', { style: cardStyle })
    await nextTick()
    cardElement.value.mount('#card-element')

    cardElement.value.on('change', (event) => {
      if (event.error) {
        errorMessage.value = event.error.message
      } else {
        errorMessage.value = ''
      }
    })

    stripeReady.value = true
  }
})
</script>