import { cn } from '@/lib/utils';

interface CardRowListProps {
  children: React.ReactNode;
  className?: string;
}

/**
 * Container for a list of CardRow components with consistent spacing
 */
export function CardRowList({ children, className }: CardRowListProps) {
  return <div className={cn('space-y-3', className)}>{children}</div>;
}

interface CardRowListHeaderProps {
  title: string;
  description?: string;
  actions?: React.ReactNode;
  className?: string;
}

/**
 * Header section for CardRowList with title, description, and optional actions
 */
export function CardRowListHeader({
  title,
  description,
  actions,
  className,
}: CardRowListHeaderProps) {
  return (
    <div
      className={cn(
        'flex items-baseline justify-between border-b pb-4',
        className
      )}
    >
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">{title}</h2>
        {description && (
          <p className="text-muted-foreground mt-1 text-sm">{description}</p>
        )}
      </div>
      {actions && <div>{actions}</div>}
    </div>
  );
}

interface CardRowListEmptyProps {
  title?: string;
  description?: string;
  className?: string;
}

/**
 * Empty state for CardRowList
 */
export function CardRowListEmpty({
  title = 'No items yet',
  description,
  className,
}: CardRowListEmptyProps) {
  return (
    <div
      className={cn(
        'flex h-64 items-center justify-center rounded-lg border border-dashed',
        className
      )}
    >
      <div className="text-center">
        <p className="text-muted-foreground text-sm">{title}</p>
        {description && (
          <p className="text-muted-foreground mt-1 text-xs">{description}</p>
        )}
      </div>
    </div>
  );
}
