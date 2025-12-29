import { createFileRoute, Outlet } from '@tanstack/react-router';

export const Route = createFileRoute('/_public')({
  component: PublicLayout,
});

function PublicLayout() {
  // Simple passthrough layout for public routes
  // Can add shared public layout elements here (e.g., public nav, footer)
  return <Outlet />;
}
