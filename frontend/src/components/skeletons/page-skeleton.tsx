import { Skeleton } from '@/components/ui/skeleton';

/**
 * Generic page skeleton shown while Suspense queries are loading.
 * Simple and lightweight - just indicates content is loading.
 */
export function PageSkeleton() {
  return (
    <div className="flex h-full flex-col p-6">
      {/* Page header */}
      <div className="mb-6 space-y-2">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-4 w-96" />
      </div>

      {/* Content area */}
      <div className="flex-1 space-y-4">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    </div>
  );
}
