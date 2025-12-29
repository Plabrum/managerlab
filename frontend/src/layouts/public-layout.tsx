import { Outlet } from '@tanstack/react-router';

export function PublicLayout() {
  // Simple passthrough layout for public routes
  // Can add shared public layout elements here (e.g., public nav, footer)
  return <Outlet />;
}
