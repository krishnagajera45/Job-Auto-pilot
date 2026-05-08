interface StatCardProps {
  label: string;
  value: string;
  trend?: string;
}

export default function StatCard({ label, value, trend }: StatCardProps) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
      <p className="text-xs uppercase tracking-[0.2em] text-slate-400">{label}</p>
      <div className="mt-3 flex items-end gap-2">
        <span className="text-2xl font-semibold text-white">{value}</span>
        {trend ? <span className="text-xs text-emerald-400">{trend}</span> : null}
      </div>
    </div>
  );
}
