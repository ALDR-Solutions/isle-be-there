import { loadStripe } from '@stripe/stripe-js';
import api from './api';

const STRIPE_PUBLISHABLE_KEY = import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || '';

/**
 * Create a Stripe Payment Intent for a booking
 * @param {string} bookingId - The booking ID
 * @returns {Promise<{client_secret: string}>}
 */
export async function createPaymentIntent(bookingId) {
  const response = await api.post(`/api/bookings/${bookingId}/payment-intent`);
  return response.data;
}

/**
 * Confirm payment was successful on the backend
 * @param {string} bookingId - The booking ID
 * @returns {Promise<{status: string, message: string}>}
 */
export async function confirmPayment(bookingId) {
  const response = await api.post(`/api/bookings/${bookingId}/confirm-payment`);
  return response.data;
}

/**
 * Load Stripe instance with publishable key
 * @returns {Promise<Stripe | null>}
 */
export async function getStripe() {
  if (!STRIPE_PUBLISHABLE_KEY) {
    console.warn('VITE_STRIPE_PUBLISHABLE_KEY not set');
    return null;
  }
  return loadStripe(STRIPE_PUBLISHABLE_KEY);
}

export default {
  createPaymentIntent,
  confirmPayment,
  getStripe,
};