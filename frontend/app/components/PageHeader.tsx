import Link from "next/link";
import { ReactNode } from "react";

interface PageHeaderProps {
  title: string;
  subtitle: string;
  actions?: ReactNode;
}

export default function PageHeader({ title, subtitle, actions }: PageHeaderProps) {
  return (
    <div className="flex flex-col gap-4 border-b border-slate-800/70 pb-6 md:flex-row md:items-center md:justify-between">
      <div>
        <h1 className="text-3xl font-semibold text-white">{title}</h1>
        <p className="mt-2 text-sm text-slate-300">{subtitle}</p>
      </div>
      <div className="flex flex-wrap gap-3 text-sm text-slate-200">
        {actions}
        {!actions ? (
          <Link className="rounded-full border border-slate-700 px-4 py-2 hover:border-slate-500" href="/dashboard">
            Back to Dashboard
          </Link>
        ) : null}
      </div>
    </div>
  );
}
