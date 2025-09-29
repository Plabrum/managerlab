import { Loader2 } from 'lucide-react';

interface LoadingProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function Loading({
  message = 'Loading...',
  size = 'md',
  className = '',
}: LoadingProps) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };

  const containerClasses = {
    sm: 'h-32',
    md: 'h-64',
    lg: 'h-96',
  };

  return (
    <div
      className={`flex items-center justify-center ${containerClasses[size]} ${className}`}
    >
      <div className="text-center">
        <Loader2
          className={`${sizeClasses[size]} text-muted-foreground mx-auto mb-2 animate-spin`}
        />
        <p className="text-muted-foreground text-sm">{message}</p>
      </div>
    </div>
  );
}

interface PageLoadingProps {
  title?: string;
  subtitle?: string;
  message?: string;
}

export function PageLoading({
  title = 'Loading',
  subtitle,
  message = 'Please wait while we load your data...',
}: PageLoadingProps) {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{title}</h1>
        {subtitle && <p className="text-muted-foreground">{subtitle}</p>}
      </div>
      <Loading message={message} size="md" />
    </div>
  );
}
