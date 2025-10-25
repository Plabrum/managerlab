'use client';

import { useCallback } from 'react';
import { useRouter, useSearchParams, usePathname } from 'next/navigation';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';

interface Tab {
  value: string;
  label: string;
  unreadCount?: number;
}

interface ObjectDetailTabsProps {
  tabs: Tab[];
  defaultTab?: string;
  children: React.ReactNode;
}

/**
 * ObjectDetailTabs provides a flexible tabbed interface wrapper with URL sync.
 * Accepts an array of tab definitions and renders children as tab content.
 * Syncs active tab with URL parameter `?tab=<value>` for bookmarkable tabs.
 *
 * Usage:
 * <ObjectDetailTabs tabs={[{ value: 'summary', label: 'Summary' }]}>
 *   <TabsContent value="summary">Content here</TabsContent>
 * </ObjectDetailTabs>
 */
export function ObjectDetailTabs({
  tabs,
  defaultTab,
  children,
}: ObjectDetailTabsProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  // Get current tab from URL or use default
  const currentTab = searchParams.get('tab') || defaultTab || tabs[0]?.value;

  // Update URL when tab changes
  const handleTabChange = useCallback(
    (value: string) => {
      const params = new URLSearchParams(searchParams.toString());
      params.set('tab', value);
      router.push(`${pathname}?${params.toString()}`, { scroll: false });
    },
    [pathname, router, searchParams]
  );

  return (
    <Tabs
      value={currentTab}
      onValueChange={handleTabChange}
      className="space-y-6"
    >
      <TabsList>
        {tabs.map((tab) => (
          <TabsTrigger key={tab.value} value={tab.value}>
            <span className="flex items-center gap-2">
              {tab.label}
              {tab.unreadCount !== undefined && tab.unreadCount > 0 && (
                <Badge
                  variant="destructive"
                  className="h-5 min-w-5 px-1 text-xs"
                >
                  {tab.unreadCount > 99 ? '99+' : tab.unreadCount}
                </Badge>
              )}
            </span>
          </TabsTrigger>
        ))}
      </TabsList>
      {children}
    </Tabs>
  );
}
