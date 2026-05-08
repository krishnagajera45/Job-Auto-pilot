import Link from "next/link";
import PageHeader from "../components/PageHeader";
import SectionCard from "../components/SectionCard";
import StatCard from "../components/StatCard";

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
      <div className="mx-auto flex max-w-6xl flex-col gap-8">
        <PageHeader
          title="Dashboard"
          subtitle="Track applications, approvals, and automation status in one view."
          actions={
            <Link className="rounded-full bg-indigo-500 px-4 py-2 text-sm font-semibold" href="/jobs/new">
              New Job Intake
            </Link>
          }
        />

        <section className="grid gap-4 md:grid-cols-4">
          <StatCard label="Applications" value="24" trend="+4 this week" />
          <StatCard label="In Review" value="6" />
          <StatCard label="Automation" value="92%" trend="Success rate" />
          <StatCard label="Interviews" value="3" trend="Next: Tue" />
        </section>

        <section className="grid gap-6 md:grid-cols-2">
          <SectionCard
            title="Active pipelines"
            description="Keep tabs on stages across all active applications."
          >
            <ul className="mt-4 space-y-3 text-sm text-slate-300">
              <li>• Senior ML Engineer @ Horizon AI — Tailoring in progress</li>
              <li>• Data Scientist @ Nova — Pending approval</li>
              <li>• AI Platform Engineer @ Solaria — Applied</li>
            </ul>
          </SectionCard>
          <SectionCard
            title="Agent status"
            description="Latest runs from the agent orchestration service."
          >
            <ul className="mt-4 space-y-3 text-sm text-slate-300">
              <li>• Workflow 9ac2 — Resume tailored (score 92)</li>
              <li>• Workflow 1b7f — Cover letter drafted</li>
              <li>• Workflow 4de1 — Awaiting approval</li>
            </ul>
          </SectionCard>
        </section>

        <section className="grid gap-6 md:grid-cols-3">
          <SectionCard
            title="Resume versions"
            description="Manage variants for each target role."
          >
            <Link className="text-sm text-indigo-300 hover:text-indigo-200" href="/resume">
              Open resume studio →
            </Link>
          </SectionCard>
          <SectionCard
            title="Cover letters"
            description="Review templates and auto-generated drafts."
          >
            <Link className="text-sm text-indigo-300 hover:text-indigo-200" href="/cover-letters">
              Manage cover letters →
            </Link>
          </SectionCard>
          <SectionCard
            title="Notifications"
            description="Configure alerts for approvals and status changes."
          >
            <Link className="text-sm text-indigo-300 hover:text-indigo-200" href="/settings">
              Update settings →
            </Link>
          </SectionCard>
        </section>
      </div>
    </div>
  );
}
