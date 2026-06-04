export function getPublicReviewComment(review) {
  if (!review || typeof review !== "object") {
    return ""
  }

  return review.censored_comment || review.comment || ""
}
