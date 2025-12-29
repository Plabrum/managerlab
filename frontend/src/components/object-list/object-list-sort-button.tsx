import { ArrowUpDown, ArrowUp, ArrowDown, X, Check } from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { cn } from '@/lib/utils';
import type {
  ColumnDefinitionSchema,
  SortDefinition,
} from '@/openapi/ariveAPI.schemas';
import { SortDirection } from '@/openapi/ariveAPI.schemas';

interface ObjectListSortButtonProps {
  columns: ColumnDefinitionSchema[];
  sorting: SortDefinition[];
  onSortingChange: (sorting: SortDefinition[]) => void;
}

export function ObjectListSortButton({
  columns,
  sorting,
  onSortingChange,
}: ObjectListSortButtonProps) {
  const [open, setOpen] = useState(false);
  const [selectedColumn, setSelectedColumn] = useState<string | null>(null);
  const sortableColumns = columns.filter((col) => col.sortable !== false);

  // Get current sort for display
  const currentSort = sorting.length > 0 ? sorting[0] : null;
  const currentColumn = currentSort
    ? columns.find((col) => col.key === currentSort.column)
    : null;

  const handleSort = (
    column: string,
    direction: typeof SortDirection.sort_asc | typeof SortDirection.sort_desc
  ) => {
    onSortingChange([{ column, direction }]);
    setOpen(false);
    setSelectedColumn(null);
  };

  const handleClearSort = () => {
    onSortingChange([]);
    setSelectedColumn(null);
  };

  // Build display label
  const hasActiveSort = currentSort && currentColumn;

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant={hasActiveSort ? 'default' : 'outline'}
          size="sm"
          className={cn(
            'gap-2 transition-all duration-200',
            hasActiveSort &&
              'bg-foreground text-background hover:bg-foreground/90'
          )}
        >
          <ArrowUpDown className="h-3.5 w-3.5" />
          <span className="text-sm font-medium">
            {hasActiveSort ? (
              <>
                {currentColumn.label}{' '}
                <span className="text-xs opacity-75">
                  {currentSort.direction === SortDirection.sort_asc ? '↑' : '↓'}
                </span>
              </>
            ) : (
              'Sort'
            )}
          </span>
        </Button>
      </PopoverTrigger>
      <PopoverContent
        align="start"
        className="border-border/50 bg-background w-[280px] p-0 shadow-lg backdrop-blur-sm"
      >
        {/* Header */}
        <div className="border-border/50 border-b px-4 py-3">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold tracking-tight">Sort by</h4>
            {currentSort && (
              <button
                onClick={handleClearSort}
                className="text-muted-foreground hover:text-foreground flex items-center gap-1.5 text-xs transition-colors"
              >
                <X className="h-3 w-3" />
                Clear
              </button>
            )}
          </div>
        </div>

        {/* Two-step selection */}
        <div className="p-2">
          {!selectedColumn ? (
            // Step 1: Select column
            <div className="space-y-0.5">
              {sortableColumns.map((col) => {
                const isActive = currentSort?.column === col.key;
                return (
                  <button
                    key={col.key}
                    onClick={() => setSelectedColumn(col.key)}
                    className={cn(
                      'hover:bg-accent flex w-full items-center justify-between rounded-md px-3 py-2.5 text-left text-sm transition-colors',
                      isActive && 'bg-accent/50'
                    )}
                  >
                    <span className="font-medium">{col.label}</span>
                    {isActive && (
                      <div className="flex items-center gap-1 text-xs">
                        {currentSort.direction === SortDirection.sort_asc ? (
                          <ArrowUp className="h-3.5 w-3.5" />
                        ) : (
                          <ArrowDown className="h-3.5 w-3.5" />
                        )}
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          ) : (
            // Step 2: Select direction
            <div className="space-y-1">
              <button
                onClick={() => setSelectedColumn(null)}
                className="text-muted-foreground hover:text-foreground mb-2 flex items-center gap-1.5 text-xs transition-colors"
              >
                <ArrowUp className="h-3 w-3 rotate-[-90deg]" />
                Back
              </button>
              <div className="space-y-0.5">
                <button
                  onClick={() =>
                    handleSort(selectedColumn, SortDirection.sort_asc)
                  }
                  className={cn(
                    'hover:bg-accent flex w-full items-center gap-3 rounded-md px-3 py-2.5 text-left transition-colors',
                    currentSort?.column === selectedColumn &&
                      currentSort?.direction === SortDirection.sort_asc &&
                      'bg-accent'
                  )}
                >
                  <ArrowUp className="text-muted-foreground h-4 w-4" />
                  <div className="flex-1">
                    <div className="text-sm font-medium">Ascending</div>
                    <div className="text-muted-foreground text-xs">A → Z</div>
                  </div>
                  {currentSort?.column === selectedColumn &&
                    currentSort?.direction === SortDirection.sort_asc && (
                      <Check className="h-4 w-4" />
                    )}
                </button>
                <button
                  onClick={() =>
                    handleSort(selectedColumn, SortDirection.sort_desc)
                  }
                  className={cn(
                    'hover:bg-accent flex w-full items-center gap-3 rounded-md px-3 py-2.5 text-left transition-colors',
                    currentSort?.column === selectedColumn &&
                      currentSort?.direction === SortDirection.sort_desc &&
                      'bg-accent'
                  )}
                >
                  <ArrowDown className="text-muted-foreground h-4 w-4" />
                  <div className="flex-1">
                    <div className="text-sm font-medium">Descending</div>
                    <div className="text-muted-foreground text-xs">Z → A</div>
                  </div>
                  {currentSort?.column === selectedColumn &&
                    currentSort?.direction === SortDirection.sort_desc && (
                      <Check className="h-4 w-4" />
                    )}
                </button>
              </div>
            </div>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
}
