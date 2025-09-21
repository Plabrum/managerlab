import { CurrentUserTest } from '@/components/current-user-test';

export default function HomePage() {
  return (
    <div className="space-y-8">
      <section className="space-y-4 text-center">
        <h2 className="text-4xl font-bold tracking-tight">
          Welcome to ManageOS
        </h2>
        <p className="text-muted-foreground mx-auto max-w-2xl text-xl">
          Modern management platform for teams and organizations
        </p>
      </section>

      <section>
        <CurrentUserTest />
      </section>

      <section className="grid gap-6 md:grid-cols-3">
        <div className="space-y-2 rounded-lg border p-6">
          <h3 className="text-lg font-semibold">Team Management</h3>
          <p className="text-muted-foreground text-sm">
            Organize and manage your team members effectively
          </p>
        </div>

        <div className="space-y-2 rounded-lg border p-6">
          <h3 className="text-lg font-semibold">Project Tracking</h3>
          <p className="text-muted-foreground text-sm">
            Keep track of projects and deadlines in one place
          </p>
        </div>

        <div className="space-y-2 rounded-lg border p-6">
          <h3 className="text-lg font-semibold">Analytics</h3>
          <p className="text-muted-foreground text-sm">
            Get insights into your team&apos;s performance and productivity
          </p>
        </div>
      </section>

      <section className="text-center">
        <a
          href="/auth"
          className="bg-primary text-primary-foreground hover:bg-primary/90 inline-flex items-center justify-center rounded-md px-8 py-2 text-sm font-medium"
        >
          Get Started
        </a>
      </section>
    </div>
  );
}
