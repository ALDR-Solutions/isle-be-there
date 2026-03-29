export function formatCurrency(value, options = {}) {
  const amount = Number(value || 0)

  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: options.currency || 'USD',
    maximumFractionDigits: 2,
  }).format(amount)
}

export function formatDate(value, options = {}) {
  if (!value) return ''

  return new Date(value).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    ...options,
  })
}

export function formatDateTime(value) {
  if (!value) return ''

  return new Date(value).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

export function formatLocation(address) {
  if (!address) return ''

  return [address.street, address.city, address.state, address.postal_code, address.country]
    .filter(Boolean)
    .join(', ')
}
