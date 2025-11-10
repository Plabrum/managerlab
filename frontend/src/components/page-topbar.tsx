'use client';

import { SidebarTrigger } from '@/components/ui/sidebar';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Breadcrumb } from '@/components/breadcrumb';
import { humanizeEnumValue } from '@/lib/format';

interface PageTopBarProps {
  title: string;
  state?: string;
  actions?: React.ReactNode;
  chatButton?: React.ReactNode;
  children: React.ReactNode;
}

export function PageTopBar({
  title,
  state,
  actions,
  chatButton,
  children,
}: PageTopBarProps) {
  return (
    <>
      <header className="group-has-data-[collapsible=icon]/sidebar-wrapper:h-12 flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear">
        <div className="grid w-full grid-cols-3 items-center px-4">
          {/* Left: Sidebar trigger + Breadcrumb */}
          <div className="flex items-center justify-start gap-2">
            <SidebarTrigger className="-ml-1" />
            <Separator
              orientation="vertical"
              className="mr-2 data-[orientation=vertical]:h-4"
            />
            <Breadcrumb currentPageTitle={title} />
          </div>

          {/* Center: Title + State */}
          <div className="flex items-center justify-center gap-2">
            <h1 className="text-lg font-semibold tracking-tight">{title}</h1>
            {state && <Badge>{humanizeEnumValue(state)}</Badge>}
          </div>

          {/* Right: Chat Button + Actions */}
          <div className="flex items-center justify-end gap-2">
            {chatButton}
            {actions}
          </div>
        </div>
      </header>
      {children}
    </>
  );
}
