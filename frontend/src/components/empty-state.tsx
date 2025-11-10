'use client';

import { Button } from '@/components/ui/button';
import {
  Empty,
  EmptyContent,
  EmptyHeader,
  EmptyTitle,
} from '@/components/ui/empty';

interface EmptyStateProps {
  /**
   * The title/message to display
   */
  title: string;
  /**
   * Call-to-action button configuration
   */
  cta: {
    label: string;
    onClick: () => void;
  };
  /**
   * Optional className for custom styling
   */
  className?: string;
}

export function EmptyState({ title, cta, className }: EmptyStateProps) {
  return (
    <Empty className={className}>
      <EmptyHeader>
        <EmptyTitle>{title}</EmptyTitle>
      </EmptyHeader>
      <EmptyContent>
        <Button onClick={cta.onClick}>{cta.label}</Button>
      </EmptyContent>
    </Empty>
  );
}
