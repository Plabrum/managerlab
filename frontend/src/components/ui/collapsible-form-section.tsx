'use client';

import { ChevronRight } from 'lucide-react';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from './collapsible';

interface CollapsibleFormSectionProps {
  title: string;
  description?: string;
  defaultOpen?: boolean;
  children: React.ReactNode;
}

/**
 * A reusable collapsible section for forms that can contain optional fields.
 * Displays as an inline trigger with content at the same indentation level.
 */
export function CollapsibleFormSection({
  title,
  defaultOpen = false,
  children,
}: CollapsibleFormSectionProps) {
  return (
    <Collapsible
      defaultOpen={defaultOpen}
      className="group/collapsible space-y-4"
    >
      <CollapsibleTrigger className="flex items-center gap-1 text-sm font-medium hover:opacity-80">
        <span>{title}</span>
        <ChevronRight className="h-4 w-4 transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90" />
      </CollapsibleTrigger>
      <CollapsibleContent>
        <div className="space-y-4">{children}</div>
      </CollapsibleContent>
    </Collapsible>
  );
}
