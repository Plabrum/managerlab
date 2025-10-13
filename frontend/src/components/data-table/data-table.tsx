'use client';

import * as React from 'react';
import {
  type ColumnDef,
  type ColumnFiltersState,
  flexRender,
  getCoreRowModel,
  type OnChangeFn,
  type PaginationState,
  type SortingState,
  type Table as ReactTable,
  useReactTable,
  type VisibilityState,
} from '@tanstack/react-table';
import {
  Filter,
  MoreHorizontal,
  Settings2,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
} from 'lucide-react';
import { useRouter } from 'next/navigation';

import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import type {
  ColumnDefinitionDTO,
  ObjectListDTO,
} from '@/openapi/managerLab.schemas';
import {
  formatCellValue,
  columnFiltersToRequestFilters,
  requestFiltersToColumnFilters,
} from './utils';
import { DataTablePagination } from './data-table-pagination';
import { DataTableColumnFilter } from './data-table-column-filter';

interface DataTableProps {
  columns: ColumnDefinitionDTO[];
  data: ObjectListDTO[];
  totalCount: number;
  enableRowSelection?: boolean;
  enableSorting?: boolean;
  enableColumnVisibility?: boolean;
  enableColumnFilters?: boolean; // Enable filter buttons in column headers
  showItemRange?: boolean; // Show "X-Y of Z" instead of "Page X of Y"
  onActionClick?: (action: string, row: ObjectListDTO) => void; // Handler for action clicks
  onBulkActionClick?: (action: string, rows: ObjectListDTO[]) => void; // Handler for bulk action clicks
  isLoading?: boolean; // Loading state for data fetching
  // Server-side state
  paginationState: PaginationState;
  sortingState: SortingState;
  columnFilters: ColumnFiltersState;
  // Callbacks
  onPaginationChange: OnChangeFn<PaginationState>;
  onSortingChange: OnChangeFn<SortingState>;
  onFiltersChange: OnChangeFn<ColumnFiltersState>;
}

// Column header component that accesses current filter state and sorting
const ColumnHeader = React.memo(
  ({
    columnDef,
    columnDefs,
    enableColumnFilters,
    columnFilters,
    onFiltersChange,
    sortingState,
    toggleSorting,
  }: {
    columnDef: ColumnDefinitionDTO;
    columnDefs: ColumnDefinitionDTO[];
    enableColumnFilters: boolean;
    columnFilters: ColumnFiltersState;
    onFiltersChange: OnChangeFn<ColumnFiltersState>;
    sortingState: SortingState;
    toggleSorting?: () => void;
  }) => {
    // Check if this column has an active filter
    const activeFilter = columnFilters.find(
      (filter) => filter.id === columnDef.key
    );
    const hasActiveFilter = Boolean(activeFilter?.value);

    // Get sort state for this column
    const sortState = sortingState.find((sort) => sort.id === columnDef.key);
    const isSorted =
      sortState?.desc === false
        ? 'asc'
        : sortState?.desc === true
          ? 'desc'
          : false;

    // Get appropriate sort icon
    const getSortIcon = () => {
      if (!isSorted) {
        return <ArrowUpDown className="ml-2 h-4 w-4 opacity-50" />;
      }
      return isSorted === 'asc' ? (
        <ArrowUp className="ml-2 h-4 w-4" />
      ) : (
        <ArrowDown className="ml-2 h-4 w-4" />
      );
    };

    const labelContent = columnDef.sortable ? (
      <Button
        variant="ghost"
        onClick={toggleSorting}
        className="h-auto p-0 font-medium hover:bg-transparent"
      >
        {columnDef.label}
        {getSortIcon()}
      </Button>
    ) : (
      <span className="font-medium">{columnDef.label}</span>
    );

    if (!enableColumnFilters) {
      return labelContent;
    }

    return (
      <div className="flex items-center">
        {labelContent}
        <Popover>
          <PopoverTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              className={`ml-1 h-6 w-6 p-0 ${
                hasActiveFilter
                  ? 'text-primary'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <Filter className="h-3 w-3" />
              <span className="sr-only">Filter {columnDef.label}</span>
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-80" align="start">
            <DataTableColumnFilter
              column={columnDef}
              filters={columnFilters
                .filter((filter) => filter.id === columnDef.key)
                .map(
                  (filter) =>
                    columnFiltersToRequestFilters([filter], columnDefs)[0]
                )
                .filter(Boolean)}
              onFiltersChange={(newFilters) => {
                // Remove existing filters for this column
                const otherFilters = columnFilters.filter(
                  (filter) => filter.id !== columnDef.key
                );

                // Convert new filters back to TanStack format
                const newTanStackFilters =
                  requestFiltersToColumnFilters(newFilters);

                // Update the filters
                onFiltersChange([...otherFilters, ...newTanStackFilters]);
              }}
            />
          </PopoverContent>
        </Popover>
      </div>
    );
  }
);

ColumnHeader.displayName = 'ColumnHeader';

function createColumnDef(
  columnDef: ColumnDefinitionDTO,
  columnDefs: ColumnDefinitionDTO[],
  enableColumnFilters: boolean,
  onFiltersChange: OnChangeFn<ColumnFiltersState>
): ColumnDef<ObjectListDTO> {
  const column: ColumnDef<ObjectListDTO> = {
    accessorKey: columnDef.key,
    header: ({ table, column }) => (
      <ColumnHeader
        columnDef={columnDef}
        columnDefs={columnDefs}
        enableColumnFilters={enableColumnFilters}
        columnFilters={table.getState().columnFilters}
        onFiltersChange={onFiltersChange}
        sortingState={table.getState().sorting}
        toggleSorting={
          columnDef.sortable
            ? () => column.toggleSorting(column.getIsSorted() === 'asc')
            : undefined
        }
      />
    ),
    enableSorting: columnDef.sortable ?? true,
    cell: ({ row }) => {
      const field = row.original.fields?.find((f) => f.key === columnDef.key);
      return formatCellValue(columnDef, field);
    },
  };

  return column;
}

export function DataTable({
  columns: columnDefs,
  data,
  totalCount,
  enableRowSelection = false,
  enableSorting = true,
  enableColumnVisibility = true,
  enableColumnFilters = true,
  showItemRange = false,
  onActionClick,
  onBulkActionClick,
  paginationState,
  sortingState,
  columnFilters,
  onPaginationChange,
  onSortingChange,
  onFiltersChange,
}: DataTableProps) {
  const router = useRouter();
  const [rowSelection, setRowSelection] = React.useState({});
  const [columnVisibility, setColumnVisibility] =
    React.useState<VisibilityState>(() => {
      const visibility: VisibilityState = {};
      columnDefs.forEach((col) => {
        visibility[col.key] = col.default_visible ?? true;
      });
      return visibility;
    });

  // Memoize individual column definitions to prevent recreation
  // Only recreate when column structure changes, not when filter values change
  const dynamicColumns = React.useMemo<ColumnDef<ObjectListDTO>[]>(() => {
    return columnDefs.map((columnDef) =>
      createColumnDef(
        columnDef,
        columnDefs,
        enableColumnFilters,
        onFiltersChange
      )
    );
  }, [columnDefs, enableColumnFilters, onFiltersChange]);

  // Memoize selection column separately since it doesn't depend on columnDefs
  const selectionColumn = React.useMemo<ColumnDef<ObjectListDTO>>(
    () => ({
      id: 'select',
      header: ({ table }) => (
        <div
          className="flex items-center justify-center"
          onClick={(e) => e.stopPropagation()}
        >
          <Checkbox
            checked={
              table.getIsAllPageRowsSelected() ||
              (table.getIsSomePageRowsSelected() && 'indeterminate')
            }
            onCheckedChange={(value) =>
              table.toggleAllPageRowsSelected(!!value)
            }
            aria-label="Select all"
          />
        </div>
      ),
      cell: ({ row }) => (
        <div
          className="flex items-center justify-center"
          onClick={(e) => e.stopPropagation()}
        >
          <Checkbox
            checked={row.getIsSelected()}
            onCheckedChange={(value) => row.toggleSelected(!!value)}
            aria-label="Select row"
          />
        </div>
      ),
      enableSorting: false,
      enableHiding: false,
    }),
    []
  );

  // Create actions column header component that can access table later
  const ActionsColumnHeader = React.useCallback(
    ({ table }: { table: ReactTable<ObjectListDTO> }) => (
      <div className="flex justify-end">
        {enableColumnVisibility && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className="text-muted-foreground hover:text-foreground h-6 w-6 p-0"
              >
                <Settings2 className="h-3 w-3" />
                <span className="sr-only">Column settings</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              {table
                .getAllColumns()
                .filter(
                  (column) =>
                    typeof column.accessorFn !== 'undefined' &&
                    column.getCanHide()
                )
                .map((column) => {
                  return (
                    <DropdownMenuCheckboxItem
                      key={column.id}
                      className="capitalize"
                      checked={column.getIsVisible()}
                      onCheckedChange={(value) =>
                        column.toggleVisibility(!!value)
                      }
                    >
                      {column.id}
                    </DropdownMenuCheckboxItem>
                  );
                })}
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </div>
    ),
    [enableColumnVisibility]
  );

  // Memoize actions column
  const actionsColumn = React.useMemo<ColumnDef<ObjectListDTO>>(
    () => ({
      id: 'actions',
      size: 60,
      minSize: 60,
      maxSize: 60,
      enableResizing: false,
      header: ({ table }) => <ActionsColumnHeader table={table} />,
      cell: ({ row }) => {
        const rowActions = row.original.actions;
        const hasRowActions = rowActions && rowActions.length > 0;

        if (!hasRowActions) {
          // If no row actions but column is shown for settings, render empty cell
          return <div className="flex justify-end" />;
        }

        // Filter available actions
        const availableActions = rowActions.filter(
          (action) => action.available !== false
        );
        if (availableActions.length === 0) {
          return <div className="flex justify-end" />;
        }

        return (
          <div className="flex justify-end">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  className="h-8 w-8 p-0"
                  onClick={(e) => e.stopPropagation()}
                >
                  <span className="sr-only">Open menu</span>
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                {availableActions
                  .sort((a, b) => (a.priority || 0) - (b.priority || 0)) // Sort by priority
                  .map((action, index) => (
                    <DropdownMenuItem
                      key={`${action.action}-${index}`}
                      onClick={(e) => {
                        e.stopPropagation();
                        if (onActionClick) {
                          onActionClick(action.action, row.original);
                        }
                      }}
                      className="cursor-pointer"
                    >
                      {action.label}
                    </DropdownMenuItem>
                  ))}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        );
      },
      enableSorting: false,
      enableHiding: false,
    }),
    [onActionClick, ActionsColumnHeader]
  );

  // Check if any row has actions to determine if we should show the actions column
  const hasActions = React.useMemo(() => {
    return data.some((row) => row.actions && row.actions.length > 0);
  }, [data]);

  // Show actions column if there are row actions OR if column visibility is enabled (for settings)
  const showActionsColumn = hasActions || enableColumnVisibility;

  // Combine columns with stable references
  const columns = React.useMemo<ColumnDef<ObjectListDTO>[]>(() => {
    const cols: ColumnDef<ObjectListDTO>[] = [];

    if (enableRowSelection) {
      cols.push(selectionColumn);
    }

    cols.push(...dynamicColumns);

    // Add actions column at the end if any row has actions or if column visibility is enabled
    if (showActionsColumn) {
      cols.push(actionsColumn);
    }

    return cols;
  }, [
    dynamicColumns,
    selectionColumn,
    actionsColumn,
    enableRowSelection,
    showActionsColumn,
  ]);

  const table = useReactTable({
    data,
    columns,
    pageCount: Math.ceil(totalCount / paginationState.pageSize),
    state: {
      sorting: sortingState,
      columnVisibility,
      rowSelection,
      columnFilters,
      pagination: paginationState,
    },
    getRowId: React.useCallback((row: ObjectListDTO) => String(row.id), []),
    enableRowSelection,
    enableSorting,
    manualPagination: true,
    manualSorting: true,
    manualFiltering: true,
    // Prevent auto-resets that cause unnecessary re-renders
    autoResetPageIndex: false,
    onRowSelectionChange: setRowSelection,
    onSortingChange: onSortingChange,
    onColumnFiltersChange: onFiltersChange,
    onColumnVisibilityChange: setColumnVisibility,
    onPaginationChange: onPaginationChange,
    getCoreRowModel: getCoreRowModel(),
  });

  // Get selected rows
  const selectedRowsData = React.useMemo(() => {
    return table.getSelectedRowModel().rows.map((row) => row.original);
  }, [table]);

  // Get common bulk actions across all selected rows
  const commonBulkActions = React.useMemo(() => {
    if (selectedRowsData.length === 0) return [];

    // Get all bulk-allowed actions from the first selected row
    const firstRowActions =
      selectedRowsData[0].actions?.filter(
        (action) => action.is_bulk_allowed && action.available !== false
      ) || [];

    // Filter to only actions that exist in ALL selected rows
    return firstRowActions.filter((action) =>
      selectedRowsData.every((row) =>
        row.actions?.some(
          (a) =>
            a.action === action.action &&
            a.is_bulk_allowed &&
            a.available !== false
        )
      )
    );
  }, [selectedRowsData]);

  const showBulkActions =
    selectedRowsData.length > 0 &&
    commonBulkActions.length > 0 &&
    onBulkActionClick;

  return (
    <div className="w-full">
      {/* Table */}
      <div className="overflow-hidden rounded-lg border">
        <Table>
          <TableHeader className="bg-muted">
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id} colSpan={header.colSpan}>
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                    </TableHead>
                  );
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => {
                const rowLink = row.original.link;
                const isClickable = Boolean(rowLink);

                return (
                  <TableRow
                    key={row.id}
                    data-state={row.getIsSelected() && 'selected'}
                    onClick={() => {
                      if (isClickable && rowLink) {
                        router.push(rowLink);
                      }
                    }}
                    className={isClickable ? 'cursor-pointer' : undefined}
                  >
                    {row.getVisibleCells().map((cell) => (
                      <TableCell key={cell.id}>
                        {flexRender(
                          cell.column.columnDef.cell,
                          cell.getContext()
                        )}
                      </TableCell>
                    ))}
                  </TableRow>
                );
              })
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Bulk Actions Bar */}
      {showBulkActions && (
        <div className="bg-muted mt-4 flex items-center justify-between rounded-md border p-3">
          <div className="text-sm font-medium">
            {selectedRowsData.length} of {data.length} row(s) selected
          </div>
          <div className="flex gap-2">
            {commonBulkActions
              .sort((a, b) => (a.priority || 0) - (b.priority || 0))
              .map((action) => (
                <Button
                  key={action.action}
                  variant="default"
                  size="sm"
                  onClick={() => {
                    onBulkActionClick(action.action, selectedRowsData);
                    setRowSelection({});
                  }}
                >
                  {action.label}
                </Button>
              ))}
          </div>
        </div>
      )}

      {/* Pagination */}
      <DataTablePagination
        table={table}
        enableRowSelection={enableRowSelection && !showBulkActions}
        showItemRange={showItemRange}
      />
    </div>
  );
}
