import { ReactNode } from "react";

interface SectionCardProps {
  title: string;
  description: string;
  children?: ReactNode;
}

export default function SectionCard({ title, description, children }: SectionCardProps) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-sm">
      <h3 className="text-lg font-semibold text-white">{title}</h3>
      <p className="mt-2 text-sm text-slate-300">{description}</p>
      {children ? <div className="mt-4">{children}</div> : null}
    </div>
  );
}
