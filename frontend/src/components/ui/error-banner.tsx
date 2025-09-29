import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ErrorBannerProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorBanner({
  title = 'Error',
  message = 'Something went wrong. Please try again later.',
  onRetry,
  className = '',
}: ErrorBannerProps) {
  return (
    <div className={`rounded-lg bg-red-900 p-6 ${className}`}>
      <div className="flex items-start gap-3">
        <AlertTriangle className="mt-0.5 h-5 w-5 flex-shrink-0 text-red-200" />
        <div className="flex-1">
          <h2 className="mb-2 text-xl font-semibold text-white">{title}</h2>
          <p className="mb-4 text-red-200">{message}</p>
          {onRetry && (
            <Button
              variant="outline"
              size="sm"
              onClick={onRetry}
              className="border-red-700 bg-red-800 text-red-100 hover:bg-red-700 hover:text-white"
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              Try Again
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
