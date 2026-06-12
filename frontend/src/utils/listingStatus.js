export function statusLabel(status) {
  if (status === "active") return "Active";
  if (status === "pending") return "Pending Approval";
  if (status === "inactive") return "Archived";
  if (status === "suspended") return "Suspended";
  return status ?? "";
}

export function statusBadgeClass(status) {
  if (status === "active") return "bg-emerald-500 text-white";
  if (status === "pending") return "bg-amber-400 text-slate-900";
  if (status === "inactive") return "bg-slate-500 text-white";
  if (status === "suspended") return "bg-orange-500 text-white";
  return "bg-slate-300 text-slate-900";
}