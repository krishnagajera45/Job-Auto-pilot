import PageHeader from "../components/PageHeader";
import SectionCard from "../components/SectionCard";

export default function AdminPage() {
  return (
    <div className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
      <div className="mx-auto flex max-w-5xl flex-col gap-8">
        <PageHeader
          title="Admin Console"
          subtitle="Manage users, workflows, and service health."
        />

        <section className="grid gap-6 md:grid-cols-3">
          <SectionCard
            title="User management"
            description="Suspend accounts, reset MFA, and audit permissions."
          />
          <SectionCard
            title="Workflow monitoring"
            description="Review active agent runs and automation queues."
          />
          <SectionCard
            title="Service health"
            description="Check API gateway, database, and queue status."
          />
        </section>
      </div>
    </div>
  );
}
