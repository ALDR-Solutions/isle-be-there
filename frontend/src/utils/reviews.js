export function getPublicReviewComment(review) {
  if (!review || typeof review !== "object") {
    return ""
  }

  return review.censored_comment || review.comment || ""
}

export function canReplyToReview(listing) {
  if (!listing) {
    return false
  }

  return ["active", "pending"].includes(listing.status)
}
