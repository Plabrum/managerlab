import { redirect } from 'next/navigation';
import { dashboardsListDashboards } from '@/openapi/dashboards/dashboards';
import { DashboardContent } from '@/components/dashboard-content';

export default async function DashboardPage() {
  // Fetch dashboards to find the first one to redirect to
  const dashboards = await dashboardsListDashboards();

  // If there are dashboards, redirect to the first one (prioritizing default)
  if (dashboards.length > 0) {
    const firstDashboard =
      dashboards.find((d) => d.is_default) || dashboards[0];
    redirect(`/dashboard/${firstDashboard.id}`);
  }

  // If no dashboards exist, show the create dashboard UI
  return <DashboardContent />;
}
