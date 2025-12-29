import React from 'react';
import { PageSkeleton } from '@/components/skeletons';
import { PageLoading } from '@/components/ui/loading';

interface SuspenseWrapperProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  useSkeleton?: boolean;
  loadingTitle?: string;
  loadingSubtitle?: string;
  loadingMessage?: string;
}

/**
 * Wrapper around React Suspense with optional loading states.
 *
 * Note: Most routes now use `pendingComponent` directly on the route definition.
 * This wrapper is mainly for nested Suspense boundaries within pages.
 */
export function SuspenseWrapper({
  children,
  fallback,
  useSkeleton = false,
  loadingTitle,
  loadingSubtitle,
  loadingMessage,
}: SuspenseWrapperProps) {
  // Use provided fallback if available
  if (fallback) {
    return <React.Suspense fallback={fallback}>{children}</React.Suspense>;
  }

  // Use skeleton or PageLoading
  const defaultFallback = useSkeleton ? (
    <PageSkeleton />
  ) : (
    <PageLoading
      title={loadingTitle}
      subtitle={loadingSubtitle}
      message={loadingMessage}
    />
  );

  return <React.Suspense fallback={defaultFallback}>{children}</React.Suspense>;
}
