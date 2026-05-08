import PageHeader from "../../components/PageHeader";
import SectionCard from "../../components/SectionCard";

export default function JobIntakePage() {
  return (
    <div className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
      <div className="mx-auto flex max-w-4xl flex-col gap-8">
        <PageHeader
          title="Job Intake"
          subtitle="Paste a job link or ID to kick off parsing and tailoring workflows."
        />

        <SectionCard
          title="Job source"
          description="Accepted sources: LinkedIn, Greenhouse, Lever, and direct job IDs."
        >
          <div className="mt-4 grid gap-4 text-sm text-slate-300">
            <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-4">
              <p className="text-xs uppercase text-slate-400">Job link</p>
              <p className="mt-2">https://jobs.example.com/roles/ai-engineer</p>
            </div>
            <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-4">
              <p className="text-xs uppercase text-slate-400">Job ID</p>
              <p className="mt-2">GH-2451</p>
            </div>
          </div>
        </SectionCard>

        <SectionCard
          title="Next actions"
          description="After intake, pick a resume version and start the tailoring run."
        >
          <ul className="mt-4 space-y-2 text-sm text-slate-300">
            <li>• Parse job requirements and highlight must-haves.</li>
            <li>• Retrieve matching experience from memory.</li>
            <li>• Draft resume + cover letter for review.</li>
          </ul>
        </SectionCard>
      </div>
    </div>
  );
}
