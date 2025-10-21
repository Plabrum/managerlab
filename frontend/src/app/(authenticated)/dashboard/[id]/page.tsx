import { DashboardContent } from '@/components/dashboard-content';

export default async function DashboardByIdPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <DashboardContent dashboardId={id} />;
}
