import PageHeader from "../components/PageHeader";
import SectionCard from "../components/SectionCard";

export default function CoverLettersPage() {
  return (
    <div className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
      <div className="mx-auto flex max-w-5xl flex-col gap-8">
        <PageHeader
          title="Cover Letter Management"
          subtitle="Review templates, AI drafts, and final submissions."
        />

        <section className="grid gap-6 md:grid-cols-2">
          <SectionCard
            title="Templates"
            description="Reusable structures for different roles and industries."
          >
            <ul className="mt-4 space-y-2 text-sm text-slate-300">
              <li>• Tech Startup - Story-driven</li>
              <li>• Enterprise - Metrics first</li>
              <li>• Research - Publication focus</li>
            </ul>
          </SectionCard>
          <SectionCard
            title="Recent drafts"
            description="AI-generated drafts awaiting approval."
          >
            <ul className="mt-4 space-y-2 text-sm text-slate-300">
              <li>• OpenAI - Pending review</li>
              <li>• Stripe - Approved</li>
              <li>• Scale AI - Needs edits</li>
            </ul>
          </SectionCard>
        </section>
      </div>
    </div>
  );
}
