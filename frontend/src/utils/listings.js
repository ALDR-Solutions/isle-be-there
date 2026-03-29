import { formatLocation } from '@/utils/formatters'

export function getListingImage(listing) {
  return listing?.image_urls?.[0] || ''
}

export function getListingLocation(listing) {
  if (listing?.address) {
    return formatLocation(listing.address)
  }

  if (listing?.location?.city || listing?.location?.country) {
    return [listing.location.city, listing.location.country].filter(Boolean).join(', ')
  }

  return ''
}

export function getListingTypeName(typeId, businessTypes = []) {
  if (!typeId) return ''
  const match = businessTypes.find((item) => item.id === typeId)
  return match?.name || ''
}
