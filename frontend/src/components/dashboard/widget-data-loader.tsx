import { Suspense } from 'react';
import { useSuspenseQuery } from '@tanstack/react-query';
import { ErrorBoundary } from 'react-error-boundary';
import { Skeleton } from '@/components/ui/skeleton';
import { getTimeSeriesData } from '@/openapi/objects/objects';
import type { TimeSeriesDataResponse } from '@/openapi/ariveAPI.schemas';
import type { WidgetQuery } from '@/types/dashboard';

interface WidgetDataLoaderProps {
  query: WidgetQuery;
  children: (data: TimeSeriesDataResponse) => React.ReactNode;
}

/**
 * Inner component that uses Suspense query
 */
function WidgetDataFetcher({ query, children }: WidgetDataLoaderProps) {
  const { data } = useSuspenseQuery({
    queryKey: ['widget-data', query.object_type, query.field, query],
    queryFn: () =>
      getTimeSeriesData(query.object_type, {
        field: query.field,
        time_range: query.time_range,
        start_date: query.start_date,
        end_date: query.end_date,
        aggregation: query.aggregation,
        filters: query.filters ?? [],
        granularity: query.granularity,
        fill_missing: false,
      }),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  return <>{children(data)}</>;
}

/**
 * Skeleton loading state for widgets
 */
function WidgetSkeleton() {
  return (
    <div className="flex h-full w-full items-center justify-center p-4">
      <div className="flex h-full w-full flex-col gap-4">
        <Skeleton className="h-8 w-3/4" />
        <Skeleton className="h-full w-full" />
      </div>
    </div>
  );
}

/**
 * Error fallback for widgets
 */
function WidgetError({
  error,
  resetErrorBoundary,
}: {
  error: Error;
  resetErrorBoundary: () => void;
}) {
  return (
    <div className="flex h-full items-center justify-center p-4">
      <div className="text-center">
        <div className="text-destructive mb-2 text-sm">
          {error.message || 'Failed to load widget data'}
        </div>
        <button
          onClick={resetErrorBoundary}
          className="text-muted-foreground hover:text-foreground text-xs underline"
        >
          Try again
        </button>
      </div>
    </div>
  );
}

/**
 * Widget data loader with Suspense and Error boundaries.
 *
 * Eliminates the need for manual loading/error states in each widget.
 * Widgets become pure presentational components that receive data.
 *
 * @example
 * <WidgetDataLoader query={widget.query}>
 *   {(data) => <PieChartWidget data={data} />}
 * </WidgetDataLoader>
 */
export function WidgetDataLoader({ query, children }: WidgetDataLoaderProps) {
  return (
    <ErrorBoundary FallbackComponent={WidgetError}>
      <Suspense fallback={<WidgetSkeleton />}>
        <WidgetDataFetcher query={query}>{children}</WidgetDataFetcher>
      </Suspense>
    </ErrorBoundary>
  );
}
