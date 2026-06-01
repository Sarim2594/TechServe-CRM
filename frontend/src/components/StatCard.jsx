export default function StatCard({ label, value, tone = "blue" }) {
  const tones = {
    blue: "bg-blue-50 text-blue-700",
    amber: "bg-amber-50 text-amber-700",
    emerald: "bg-emerald-50 text-emerald-700",
    rose: "bg-rose-50 text-rose-700",
  };

  return (
    <div className="card">
      <span className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${tones[tone]}`}>{label}</span>
      <p className="mt-4 text-3xl font-bold text-slate-900">{value ?? 0}</p>
    </div>
  );
}
