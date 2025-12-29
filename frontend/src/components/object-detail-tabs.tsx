import { useCallback } from 'react';
import { useNavigate, useSearch } from '@tanstack/react-router';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';

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
  const navigate = useNavigate();
  const search = useSearch({ strict: false }) as { tab?: string };

  // Get current tab from URL or use default
  const currentTab = search.tab || defaultTab || tabs[0]?.value;

  // Update URL when tab changes
  const handleTabChange = useCallback(
    (value: string) => {
      navigate({
        to: '.',
        search: (prev: Record<string, unknown>) =>
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          ({ ...prev, tab: value }) as any,
      });
    },
    [navigate]
  );

  return (
    <Tabs
      value={currentTab}
      onValueChange={handleTabChange}
      className="container mx-auto space-y-6 p-6"
    >
      <TabsList>
        {tabs.map((tab) => (
          <TabsTrigger key={tab.value} value={tab.value}>
            <span className="flex items-center gap-2">
              {tab.label}
              {tab.unreadCount !== undefined &&
                tab.unreadCount > 0 &&
                currentTab !== tab.value && (
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
