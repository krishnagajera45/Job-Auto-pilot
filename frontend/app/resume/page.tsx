import PageHeader from "../components/PageHeader";
import SectionCard from "../components/SectionCard";

export default function ResumePage() {
  return (
    <div className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
      <div className="mx-auto flex max-w-5xl flex-col gap-8">
        <PageHeader
          title="Resume Studio"
          subtitle="Import, version, and tailor resumes for each job pipeline."
        />

        <section className="grid gap-6 md:grid-cols-2">
          <SectionCard
            title="Resume library"
            description="Store multiple base resumes and track revisions."
          >
            <ul className="mt-4 space-y-2 text-sm text-slate-300">
              <li>• Product Engineer - Base Resume</li>
              <li>• ML Platform Engineer - Tailored Resume</li>
              <li>• Research Scientist - Academic Resume</li>
            </ul>
          </SectionCard>
          <SectionCard
            title="Versioning"
            description="Generate new versions per job or template."
          >
            <ul className="mt-4 space-y-2 text-sm text-slate-300">
              <li>• v12 - Tesla AI (keyword coverage 93%)</li>
              <li>• v11 - Ramp (impact highlights)</li>
              <li>• v10 - Anthropic (RAG optimization)</li>
            </ul>
          </SectionCard>
        </section>

        <SectionCard
          title="Import options"
          description="Bring in resumes from PDF, LinkedIn, or ATS exports."
        />
      </div>
    </div>
  );
}
