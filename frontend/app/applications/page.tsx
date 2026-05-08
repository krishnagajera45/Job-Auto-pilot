import PageHeader from "../components/PageHeader";
import SectionCard from "../components/SectionCard";

export default function ApplicationsPage() {
  return (
    <div className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
      <div className="mx-auto flex max-w-5xl flex-col gap-8">
        <PageHeader
          title="Application Pipeline"
          subtitle="Monitor every submission, approval, and response."
        />

        <SectionCard
          title="Pipeline overview"
          description="Keep track of each stage from tailoring to offer."
        >
          <div className="mt-4 grid gap-4 text-sm text-slate-300">
            <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-4">
              <p className="text-xs uppercase text-slate-400">Submitted</p>
              <p className="mt-2">12 applications submitted via automation.</p>
            </div>
            <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-4">
              <p className="text-xs uppercase text-slate-400">Awaiting approval</p>
              <p className="mt-2">4 applications need final review.</p>
            </div>
            <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-4">
              <p className="text-xs uppercase text-slate-400">Interviews</p>
              <p className="mt-2">2 active interview loops.</p>
            </div>
          </div>
        </SectionCard>
      </div>
    </div>
  );
}
