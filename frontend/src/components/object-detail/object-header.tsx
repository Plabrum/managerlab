import { format } from 'date-fns';
import { Badge } from '@/components/ui/badge';

interface ObjectHeaderProps {
  title: string;
  state: string;
  createdAt: string;
  updatedAt: string;
}

export function ObjectHeader({
  title,
  state,
  createdAt,
  updatedAt,
}: ObjectHeaderProps) {
  return (
    <div className="space-y-1">
      <div className="flex items-center gap-2">
        <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
        <Badge>{state}</Badge>
      </div>
      <p className="text-muted-foreground text-sm">
        Created {format(new Date(createdAt), 'PPP')} • Updated{' '}
        {format(new Date(updatedAt), 'PPP')}
      </p>
    </div>
  );
}
