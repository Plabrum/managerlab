import React from 'react';
import { PageLoading } from '@/components/ui/loading';

interface SuspenseWrapperProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  loadingTitle?: string;
  loadingSubtitle?: string;
  loadingMessage?: string;
}

export function SuspenseWrapper({
  children,
  fallback,
  loadingTitle,
  loadingSubtitle,
  loadingMessage,
}: SuspenseWrapperProps) {
  const defaultFallback = (
    <PageLoading
      title={loadingTitle}
      subtitle={loadingSubtitle}
      message={loadingMessage}
    />
  );

  return (
    <React.Suspense fallback={fallback || defaultFallback}>
      {children}
    </React.Suspense>
  );
}
