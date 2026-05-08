import PageHeader from "../components/PageHeader";
import SectionCard from "../components/SectionCard";

export default function AuthPage() {
  return (
    <div className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
      <div className="mx-auto flex max-w-3xl flex-col gap-8">
        <PageHeader
          title="Sign In"
          subtitle="Access your Job Autopilot workspace or create an account."
        />

        <section className="grid gap-6 md:grid-cols-2">
          <SectionCard
            title="Email + Password"
            description="Use your account credentials or reset your password."
          />
          <SectionCard
            title="OAuth"
            description="Continue with Google, LinkedIn, or GitHub."
          />
        </section>
      </div>
    </div>
  );
}
