export default function Badge({ children }) {
  const colors = {
    Open: "bg-blue-100 text-blue-700",
    "In Progress": "bg-amber-100 text-amber-700",
    Resolved: "bg-emerald-100 text-emerald-700",
    Closed: "bg-slate-200 text-slate-700",
    Critical: "bg-rose-100 text-rose-700",
    High: "bg-orange-100 text-orange-700",
    Medium: "bg-yellow-100 text-yellow-700",
    Low: "bg-slate-100 text-slate-600",
    Frustrated: "bg-rose-100 text-rose-700",
    Negative: "bg-orange-100 text-orange-700",
    Positive: "bg-emerald-100 text-emerald-700",
    Neutral: "bg-slate-100 text-slate-600",
    sent: "bg-emerald-100 text-emerald-700",
    failed: "bg-rose-100 text-rose-700",
    logged: "bg-blue-100 text-blue-700",
    skipped: "bg-amber-100 text-amber-700",
  };

  return (
    <span className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${colors[children] || "bg-blue-50 text-blue-700"}`}>
      {children || "Unassigned"}
    </span>
  );
}
