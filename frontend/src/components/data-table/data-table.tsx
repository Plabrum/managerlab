'use client';

import * as React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Checkbox } from '@/components/ui/checkbox';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Badge } from '@/components/ui/badge';
import { DataTableColumnSettings } from './data-table-column-settings';
import { DataTableColumnFilter } from './data-table-column-filter';
import { DataTablePagination } from './data-table-pagination';
import { useNavigation } from '@/hooks/use-navigation';
import {
  MoreHorizontal,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Search,
  X,
  Filter,
  Funnel,
} from 'lucide-react';
import {
  ObjectListDTO,
  ObjectListRequestFiltersItem,
  ObjectListResponse,
  SortDefinition,
} from '@/openapi/managerLab.schemas';

interface DataTableProps {
  data: ObjectListResponse;
  onSearch?: (query: string) => void;
  onFiltersChange?: (filters: ObjectListRequestFiltersItem[]) => void;
  onSortChange?: (sorts: SortDefinition[]) => void;
  onRowAction?: (action: string, row: ObjectListDTO) => void;
  onBulkAction?: (action: string, selectedRows: ObjectListDTO[]) => void;
  onRowClick?: (row: ObjectListDTO) => void;
  onPaginationChange?: (offset: number, limit: number) => void;
  baseUrl?: string;
  searchQuery?: string;
  filters?: ObjectListRequestFiltersItem[];
  sorts?: SortDefinition[];
  loading?: boolean;
}

export function DataTable({
  data,
  onSearch,
  onFiltersChange,
  onSortChange,
  onRowAction,
  onBulkAction,
  onRowClick,
  onPaginationChange,
  baseUrl = '',
  searchQuery = '',
  filters = [],
  sorts = [],
  loading = false,
}: DataTableProps) {
  const [selectedRows, setSelectedRows] = React.useState<Set<string>>(
    new Set()
  );
  const [visibleColumnKeys, setVisibleColumnKeys] = React.useState<string[]>(
    () => {
      const hasDefaultVisible = data.columns.some(
        (col) => col.default_visible !== undefined
      );
      return hasDefaultVisible
        ? data.columns
            .filter((col) => col.default_visible)
            .map((col) => col.key)
        : data.columns.map((col) => col.key);
    }
  );
  const [columnFilterOpen, setColumnFilterOpen] = React.useState<string | null>(
    null
  );

  const { navigateToLink } = useNavigation(baseUrl);

  const visibleColumns = React.useMemo(() => {
    return data.columns.filter((col) => visibleColumnKeys.includes(col.key));
  }, [data.columns, visibleColumnKeys]);

  const selectedRowsArray = data.objects.filter((row) =>
    selectedRows.has(row.id)
  );
  const completeFilters = filters.filter(isFilterComplete);

  return (
    <div className="w-full">
      <div className="pb-2">
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="text-muted-foreground absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 transform" />
            <Input
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => onSearch?.(e.target.value)}
              className="pl-10"
            />
          </div>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" className="gap-2 bg-transparent">
                <Funnel className="ml-2 h-4 w-4" />
                {completeFilters.length > 0 && (
                  <Badge
                    variant="secondary"
                    className="ml-1 px-1.5 py-0.5 text-xs"
                  >
                    {completeFilters.length}
                  </Badge>
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {data.columns.map((column) => (
                <DropdownMenuSub key={column.key}>
                  <DropdownMenuSubTrigger>
                    {column.label}
                  </DropdownMenuSubTrigger>
                  <DropdownMenuSubContent className="p-0">
                    <DataTableColumnFilter
                      column={column}
                      filters={filters}
                      onFiltersChange={onFiltersChange || (() => {})}
                    />
                  </DropdownMenuSubContent>
                </DropdownMenuSub>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>

          <DataTableColumnSettings
            columns={data.columns}
            visibleColumns={visibleColumnKeys}
            onVisibleColumnsChange={setVisibleColumnKeys}
          />

          {/* Global actions menu */}
          {data.actions && data.actions.length > 0 && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="icon">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                {data.actions.map((action) => (
                  <DropdownMenuItem
                    key={action.action}
                    disabled={!action.available}
                    onClick={() =>
                      onBulkAction?.(action.action, selectedRowsArray)
                    }
                  >
                    {action.label}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>

        {completeFilters.length > 0 && (
          <div className="mt-2 flex flex-wrap items-center gap-2">
            {completeFilters.map((filter) => {
              const actualIndex = filters.findIndex((f) => f === filter);
              return (
                <Badge
                  key={`${filter.column}-${actualIndex}`}
                  variant="secondary"
                  className="gap-1"
                >
                  {getFilterDisplayText(filter)}
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-auto p-0 hover:bg-transparent"
                    onClick={() => removeFilter(actualIndex)}
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </Badge>
              );
            })}
          </div>
        )}
      </div>

      <div>
        <div className="relative">
          {loading && (
            <div className="bg-background/50 absolute inset-0 z-10 flex items-center justify-center">
              <div className="border-primary h-8 w-8 animate-spin rounded-full border-b-2"></div>
            </div>
          )}

          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12">
                  <Checkbox
                    checked={
                      selectedRows.size === data.objects.length &&
                      data.objects.length > 0
                    }
                    onCheckedChange={handleSelectAll}
                  />
                </TableHead>
                {visibleColumns.map((column) => (
                  <TableHead key={column.key}>
                    <div className="flex items-center">
                      {column.sortable ? (
                        <Button
                          variant="ghost"
                          onClick={() => handleSort(column.key)}
                          className="h-auto p-0 font-medium hover:bg-transparent"
                        >
                          {column.label}
                          {getSortIcon(column.key)}
                        </Button>
                      ) : (
                        <span className="font-medium">{column.label}</span>
                      )}
                      <Popover
                        open={columnFilterOpen === column.key}
                        onOpenChange={(open) => {
                          setColumnFilterOpen(open ? column.key : null);
                        }}
                      >
                        <PopoverTrigger asChild>
                          <Button
                            variant="ghost"
                            size="sm"
                            className={`ml-1 h-6 w-6 p-0 ${
                              hasActiveFilter(column.key)
                                ? 'text-primary'
                                : 'text-muted-foreground hover:text-foreground'
                            }`}
                          >
                            <Filter className="h-3 w-3" />
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="p-0" align="start">
                          <DataTableColumnFilter
                            column={column}
                            filters={filters}
                            onFiltersChange={onFiltersChange || (() => {})}
                          />
                        </PopoverContent>
                      </Popover>
                    </div>
                  </TableHead>
                ))}
                <TableHead className="w-12"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.objects.map((row) => (
                <TableRow
                  key={row.id}
                  className="hover:bg-muted/50 cursor-pointer"
                  onClick={(e) => handleRowClick(row, e)}
                >
                  <TableCell data-row-action>
                    <Checkbox
                      checked={selectedRows.has(row.id)}
                      onCheckedChange={(checked) =>
                        handleSelectRow(row.id, !!checked)
                      }
                    />
                  </TableCell>
                  {visibleColumns.map((column) => {
                    const field = row.fields?.find((f) => f.key === column.key);
                    const value =
                      field?.value ??
                      (row as unknown as Record<string, unknown>)[column.key];

                    return (
                      <TableCell key={column.key}>
                        {formatCellValue(value, column.type)}
                      </TableCell>
                    );
                  })}
                  <TableCell data-row-action>
                    {row.actions && row.actions.length > 0 && (
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          {row.actions.map((action) => (
                            <DropdownMenuItem
                              key={action.action}
                              disabled={!action.available}
                              onClick={(e) => {
                                e.stopPropagation();
                                onRowAction?.(action.action, row);
                              }}
                            >
                              {action.label}
                            </DropdownMenuItem>
                          ))}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          {data.objects.length === 0 && (
            <div className="text-muted-foreground py-8 text-center">
              No data available
            </div>
          )}
        </div>

        {onPaginationChange && (
          <DataTablePagination
            total={data.total}
            limit={data.limit}
            offset={data.offset}
            onPaginationChange={onPaginationChange}
          />
        )}
      </div>

      {selectedRows.size > 0 && (
        <div className="bg-muted/30 border-t p-3">
          <div className="flex items-center gap-2">
            <span className="text-muted-foreground text-sm">
              {selectedRows.size} row{selectedRows.size !== 1 ? 's' : ''}{' '}
              selected
            </span>
            {data.actions &&
              data.actions.map((action) => (
                <Button
                  key={action.action}
                  variant="outline"
                  size="sm"
                  disabled={!action.available}
                  onClick={() =>
                    onBulkAction?.(action.action, selectedRowsArray)
                  }
                >
                  {action.label}
                </Button>
              ))}
          </div>
        </div>
      )}
    </div>
  );

  function handleRowClick(row: ObjectListDTO, event: React.MouseEvent) {
    // Don't trigger row click if clicking on checkbox or action menu
    if ((event.target as HTMLElement).closest('[data-row-action]')) {
      return;
    }

    if (onRowClick) {
      onRowClick(row);
    } else if (row.link) {
      navigateToLink(row.link);
    }
  }

  function handleSelectAll(checked: boolean) {
    if (checked) {
      setSelectedRows(new Set(data.objects.map((row) => row.id)));
    } else {
      setSelectedRows(new Set());
    }
  }

  function handleSelectRow(rowId: string, checked: boolean) {
    const newSelected = new Set(selectedRows);
    if (checked) {
      newSelected.add(rowId);
    } else {
      newSelected.delete(rowId);
    }
    setSelectedRows(newSelected);
  }

  function handleSort(columnKey: string) {
    if (!onSortChange) return;

    const existingSort = sorts.find((sort) => sort.column === columnKey);
    let newSorts: SortDefinition[];

    if (!existingSort) {
      newSorts = [{ column: columnKey, direction: 'sort_asc' }];
    } else if (existingSort.direction === 'sort_asc') {
      newSorts = [{ column: columnKey, direction: 'sort_desc' }];
    } else {
      newSorts = sorts.filter((sort) => sort.column !== columnKey);
    }

    onSortChange(newSorts);
  }

  function hasActiveFilter(columnKey: string) {
    return filters.some(
      (filter) => filter.column === columnKey && isFilterComplete(filter)
    );
  }

  function isFilterComplete(filter: ObjectListRequestFiltersItem) {
    switch (filter.type) {
      case 'text_filter':
        return !!filter.value;
      case 'range_filter':
        return filter.start !== null || filter.finish !== null;
      case 'date_filter':
        return !!filter.start || !!filter.finish;
      case 'boolean_filter':
        return (
          'value' in filter && typeof filter.value === 'boolean' && filter.value
        );
      case 'enum_filter':
        return (
          'values' in filter &&
          Array.isArray(filter.values) &&
          filter.values.length > 0
        );
      default:
        return false;
    }
  }

  function getSortIcon(columnKey: string) {
    const sort = sorts.find((sort) => sort.column === columnKey);
    const hasFilter = hasActiveFilter(columnKey);

    if (!sort && !hasFilter) return null;
    if (!sort) return <ArrowUpDown className="ml-2 h-4 w-4 opacity-50" />;
    return sort.direction === 'sort_asc' ? (
      <ArrowUp className="ml-2 h-4 w-4" />
    ) : (
      <ArrowDown className="ml-2 h-4 w-4" />
    );
  }

  function formatCellValue(value: unknown, type: string) {
    if (value === null || value === undefined) return '-';

    switch (type) {
      case 'date':
      case 'datetime':
        return new Date(value as string).toLocaleDateString();
      case 'usd':
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD',
        }).format(value as number);
      case 'bool':
        return value ? 'Yes' : 'No';
      case 'url':
        return (
          <a
            href={value as string}
            className="text-blue-600 hover:underline"
            onClick={(e) => e.stopPropagation()}
          >
            {value as string}
          </a>
        );
      case 'email':
        return (
          <a
            href={`mailto:${value}`}
            className="text-blue-600 hover:underline"
            onClick={(e) => e.stopPropagation()}
          >
            {value as string}
          </a>
        );
      case 'enum':
        return <Badge variant="secondary">{value as string}</Badge>;
      default:
        return String(value);
    }
  }

  function getFilterDisplayText(filter: ObjectListRequestFiltersItem) {
    const column = data.columns.find((col) => col.key === filter.column);
    if (!column) return '';

    let text = column.label + ': ';

    switch (filter.type) {
      case 'text_filter':
        if (filter.value) {
          text += `${filter.operation} "${filter.value}"`;
        }
        break;
      case 'range_filter':
        if (filter.start !== null || filter.finish !== null) {
          text += `${filter.start || '∞'} - ${filter.finish || '∞'}`;
        }
        break;
      case 'date_filter':
        if (filter.start || filter.finish) {
          const startDate = filter.start
            ? new Date(filter.start as string).toLocaleDateString()
            : '∞';
          const endDate = filter.finish
            ? new Date(filter.finish as string).toLocaleDateString()
            : '∞';
          text += `${startDate} - ${endDate}`;
        }
        break;
      case 'boolean_filter':
        text +=
          'value' in filter && typeof filter.value === 'boolean'
            ? filter.value
              ? 'Yes'
              : 'No'
            : '';
        break;
      case 'enum_filter':
        text +=
          'values' in filter && Array.isArray(filter.values)
            ? filter.values.join(', ')
            : '';
        break;
    }

    return text;
  }

  function removeFilter(index: number) {
    if (onFiltersChange) {
      onFiltersChange(filters.filter((_, i) => i !== index));
    }
  }
}
