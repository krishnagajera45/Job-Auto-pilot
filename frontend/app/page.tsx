import Link from "next/link";
import SectionCard from "./components/SectionCard";

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800/60">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
          <div>
            <p className="text-sm uppercase tracking-[0.25em] text-slate-400">Job Autopilot</p>
            <h1 className="text-2xl font-semibold text-white">Agentic job application platform</h1>
          </div>
          <nav className="flex items-center gap-4 text-sm text-slate-300">
            <Link className="hover:text-white" href="/dashboard">
              Dashboard
            </Link>
            <Link className="hover:text-white" href="/jobs/new">
              Job Intake
            </Link>
            <Link className="hover:text-white" href="/resume">
              Resume Studio
            </Link>
            <Link className="hover:text-white" href="/auth">
              Sign In
            </Link>
          </nav>
        </div>
      </header>

      <main className="mx-auto flex max-w-6xl flex-col gap-12 px-6 py-12">
        <section className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr]">
          <div>
            <p className="text-sm font-semibold text-slate-300">AI-powered job applications</p>
            <h2 className="mt-3 text-4xl font-semibold leading-tight text-white">
              Paste a job link, review tailored docs, and let the agents apply for you.
            </h2>
            <p className="mt-4 text-base text-slate-300">
              Job Autopilot orchestrates job intake, resume versioning, cover letter drafting, and ATS
              automation with approvals and audit trails.
            </p>
            <div className="mt-6 flex flex-wrap gap-4">
              <Link
                className="rounded-full bg-indigo-500 px-5 py-2 text-sm font-semibold text-white hover:bg-indigo-400"
                href="/dashboard"
              >
                Open Dashboard
              </Link>
              <Link
                className="rounded-full border border-slate-700 px-5 py-2 text-sm font-semibold text-slate-200 hover:border-slate-500"
                href="/jobs/new"
              >
                Start a Job Intake
              </Link>
            </div>
          </div>
          <div className="rounded-3xl border border-slate-800 bg-gradient-to-br from-slate-900 to-slate-950 p-6">
            <h3 className="text-lg font-semibold text-white">Workflow snapshot</h3>
            <ul className="mt-4 space-y-3 text-sm text-slate-300">
              <li>1. Job parsing + requirement extraction</li>
              <li>2. Memory retrieval (RAG + Mem0)</li>
              <li>3. Resume + cover letter tailoring</li>
              <li>4. Approval gate + audit log</li>
              <li>5. ATS automation + status updates</li>
            </ul>
          </div>
        </section>

        <section className="grid gap-6 md:grid-cols-2">
          <SectionCard
            title="Unified applicant dashboard"
            description="Track every application, status update, interview loop, and follow-up reminder in one place."
          />
          <SectionCard
            title="Resume & cover letter studio"
            description="Manage versions, templates, and AI-enhanced edits tied to each job pipeline."
          />
          <SectionCard
            title="Agentic workflow engine"
            description="LangGraph workflows with MCP tool calls orchestrate parsing, tailoring, and approvals."
          />
          <SectionCard
            title="Automation with control"
            description="Playwright-based ATS automation stays behind approvals, retry policies, and audit logs."
          />
        </section>

        <section className="grid gap-6 md:grid-cols-3">
          <SectionCard
            title="FastAPI microservices"
            description="Services are split by domain: auth, resume, job ingestion, RAG, automation, notifications."
          />
          <SectionCard
            title="Vector + relational storage"
            description="Supabase/Postgres for relational data and Qdrant/pgvector for embeddings."
          />
          <SectionCard
            title="Observability baked in"
            description="OpenTelemetry, structured logs, and alerting hooks keep workflows transparent."
          />
        </section>
      </main>
    </div>
  );
}
