import PageHeader from "../components/PageHeader";
import SectionCard from "../components/SectionCard";

export default function SettingsPage() {
  return (
    <div className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
      <div className="mx-auto flex max-w-4xl flex-col gap-8">
        <PageHeader
          title="Settings"
          subtitle="Manage preferences, notifications, and security options."
        />

        <section className="grid gap-6 md:grid-cols-2">
          <SectionCard
            title="Notifications"
            description="Choose where you receive job application updates."
          />
          <SectionCard
            title="Messaging channels"
            description="Connect Telegram or WhatsApp to intake job links and receive PDFs."
          />
          <SectionCard
            title="Security"
            description="Enable MFA, rotate API keys, and manage sessions."
          />
          <SectionCard
            title="Integrations"
            description="Connect ATS accounts, GitHub, or LinkedIn data sources."
          />
          <SectionCard
            title="Automation policies"
            description="Define approval thresholds and retry strategies."
          />
        </section>
      </div>
    </div>
  );
}
