'use client';

import { Badge } from '@/components/ui/badge';
import { useHeader } from '@/components/header-provider';

export function DynamicPageHeader() {
  const { headerData } = useHeader();
  if (!headerData) {
    return null;
  }

  const { title, state } = headerData;

  return (
    <div className="flex items-center gap-2">
      <h1 className="text-lg font-semibold tracking-tight">{title}</h1>
      <Badge>{state}</Badge>
    </div>
  );
}
