export function getUserRole(user) {
  if (!user) return 'guest'
  if (user.is_super_admin) return 'admin'
  if (user.is_business) return 'business'
  return 'user'
}

export function hasAnyRole(user, roles = []) {
  if (!roles.length) return true
  return roles.includes(getUserRole(user))
}
