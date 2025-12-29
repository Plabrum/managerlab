import { useRouter } from '@tanstack/react-router';
import { AlertCircle, Home, RefreshCw } from 'lucide-react';
import { PageTopBar } from '@/components/page-topbar';
import { Button } from '@/components/ui/button';

interface RouteErrorProps {
  error: Error;
  reset?: () => void;
}

/**
 * Route-level error display component.
 * Shown when a route-specific error occurs (data fetching, etc).
 * Provides options to retry or navigate home.
 */
export function RouteError({ error, reset }: RouteErrorProps) {
  const router = useRouter();

  const handleRetry = () => {
    if (reset) {
      reset();
    } else {
      router.invalidate();
    }
  };

  const showDetails = import.meta.env.DEV;

  return (
    <PageTopBar title="Error">
      <div className="container mx-auto max-w-2xl space-y-6 p-6">
        <div className="border-destructive/50 bg-destructive/10 rounded-lg border p-6">
          <div className="mb-4 flex items-start gap-3">
            <div className="bg-destructive/20 flex h-10 w-10 shrink-0 items-center justify-center rounded-full">
              <AlertCircle className="text-destructive h-5 w-5" />
            </div>
            <div className="flex-1">
              <h2 className="mb-1 text-lg font-semibold">
                Failed to load this page
              </h2>
              <p className="text-muted-foreground text-sm">
                {error.message || 'An unexpected error occurred'}
              </p>
            </div>
          </div>

          {showDetails && error.stack && (
            <details className="mt-4">
              <summary className="cursor-pointer text-sm font-medium hover:underline">
                Show error details (dev only)
              </summary>
              <pre className="bg-muted mt-2 max-h-60 overflow-auto rounded p-3 text-xs">
                {error.stack}
              </pre>
            </details>
          )}
        </div>

        <div className="flex gap-3">
          <Button onClick={handleRetry} variant="default" className="flex-1">
            <RefreshCw className="mr-2 h-4 w-4" />
            Try Again
          </Button>
          <Button
            onClick={() => router.navigate({ to: '/' })}
            variant="outline"
            className="flex-1"
          >
            <Home className="mr-2 h-4 w-4" />
            Go Home
          </Button>
        </div>
      </div>
    </PageTopBar>
  );
}
