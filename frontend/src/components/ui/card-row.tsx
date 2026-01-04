import { cn } from '@/lib/utils';

interface CardRowProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

/**
 * A horizontal card row component with hover effects.
 * Useful for list items, team members, settings rows, etc.
 */
export function CardRow({ children, className, onClick }: CardRowProps) {
  return (
    <div
      className={cn(
        'bg-card group flex items-center justify-between rounded-lg border p-4 shadow-sm transition-all hover:shadow-md',
        onClick && 'cursor-pointer',
        className
      )}
      onClick={onClick}
      onKeyDown={
        onClick
          ? (e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onClick();
              }
            }
          : undefined
      }
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      {children}
    </div>
  );
}

interface CardRowLeftProps {
  children: React.ReactNode;
  className?: string;
}

/**
 * Left section of CardRow - typically contains primary information
 */
export function CardRowLeft({ children, className }: CardRowLeftProps) {
  return (
    <div className={cn('flex flex-1 items-center gap-4', className)}>
      {children}
    </div>
  );
}

interface CardRowRightProps {
  children: React.ReactNode;
  className?: string;
}

/**
 * Right section of CardRow - typically contains badges, actions, or metadata
 */
export function CardRowRight({ children, className }: CardRowRightProps) {
  return (
    <div className={cn('flex items-center gap-3', className)}>{children}</div>
  );
}

interface CardRowAvatarProps {
  children: React.ReactNode;
  className?: string;
}

/**
 * Avatar component for CardRow with hover effect
 */
export function CardRowAvatar({ children, className }: CardRowAvatarProps) {
  return (
    <div
      className={cn(
        'bg-primary/5 group-hover:bg-primary/10 flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full transition-colors',
        className
      )}
    >
      {children}
    </div>
  );
}

interface CardRowContentProps {
  children: React.ReactNode;
  className?: string;
}

/**
 * Main content area of CardRow - typically contains title and description
 */
export function CardRowContent({ children, className }: CardRowContentProps) {
  return <div className={cn('min-w-0 flex-1', className)}>{children}</div>;
}

interface CardRowTitleProps {
  children: React.ReactNode;
  className?: string;
}

/**
 * Title for CardRow content
 */
export function CardRowTitle({ children, className }: CardRowTitleProps) {
  return (
    <h3 className={cn('truncate font-semibold', className)}>{children}</h3>
  );
}

interface CardRowDescriptionProps {
  children: React.ReactNode;
  className?: string;
}

/**
 * Description for CardRow content
 */
export function CardRowDescription({
  children,
  className,
}: CardRowDescriptionProps) {
  return (
    <div className={cn('text-muted-foreground text-sm', className)}>
      {children}
    </div>
  );
}
