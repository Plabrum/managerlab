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
import { ArrowUpDown, ChevronLeft, ChevronRight } from 'lucide-react';
import { DataTableFilters } from './data-table-filters';
import { DataTableColumnSettings } from './data-table-column-settings';
import type {
  ObjectListResponse,
  ObjectListRequest,
  ObjectListRequestFiltersItem,
} from '@/openapi/managerLab.schemas';

interface DataTableProps {
  data: ObjectListResponse;
  onRequestChange: (request: ObjectListRequest) => void;
  loading?: boolean;
}

export function DataTable({
  data,
  onRequestChange,
  loading = false,
}: DataTableProps) {
  const [request, setRequest] = React.useState<ObjectListRequest>({
    limit: 10,
    offset: 0,
    filters: [],
    sorts: [],
  });

  const [visibleColumns, setVisibleColumns] = React.useState<string[]>(() =>
    data.columns
      .filter((col) => col.default_visible !== false)
      .map((col) => col.key)
  );

  const handleRequestChange = (newRequest: ObjectListRequest) => {
    setRequest(newRequest);
    onRequestChange(newRequest);
  };

  const handleSort = (columnKey: string) => {
    const existingSort = request.sorts?.find(
      (sort) => sort.column === columnKey
    );
    const filteredSorts =
      request.sorts?.filter((sort) => sort.column !== columnKey) || [];

    if (!existingSort) {
      handleRequestChange({
        ...request,
        sorts: [...filteredSorts, { column: columnKey, direction: 'sort_asc' }],
      });
    } else if (existingSort.direction === 'sort_asc') {
      handleRequestChange({
        ...request,
        sorts: [
          ...filteredSorts,
          { column: columnKey, direction: 'sort_desc' },
        ],
      });
    } else {
      // If sort_desc, remove it (already filtered out above)
      handleRequestChange({ ...request, sorts: filteredSorts });
    }
  };

  const handleFiltersChange = (filters: ObjectListRequestFiltersItem[]) => {
    handleRequestChange({ ...request, filters, offset: 0 });
  };

  const handlePageChange = (newOffset: number) => {
    handleRequestChange({ ...request, offset: newOffset });
  };

  const visibleColumnDefs = data.columns.filter((col) =>
    visibleColumns.includes(col.key)
  );

  const currentPage =
    Math.floor((request.offset || 0) / (request.limit || 10)) + 1;
  const totalPages = Math.ceil(data.total / (request.limit || 10));

  const formatCellValue = (value: unknown, type: string) => {
    if (value === null || value === undefined) return '-';

    switch (type) {
      case 'date':
        return new Date(value as string).toLocaleDateString();
      case 'datetime':
        return new Date(value as string).toLocaleString();
      case 'usd':
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD',
        }).format(value as number);
      case 'bool':
        return value ? 'Yes' : 'No';
      default:
        return String(value);
    }
  };

  return (
    <div className="space-y-4">
      {/* Header with filters and column settings */}
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <DataTableFilters
            columns={data.columns}
            filters={request.filters || []}
            onFiltersChange={handleFiltersChange}
          />
        </div>
        <DataTableColumnSettings
          columns={data.columns}
          visibleColumns={visibleColumns}
          onVisibleColumnsChange={setVisibleColumns}
        />
      </div>

      {/* Table */}
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              {visibleColumnDefs.map((column) => (
                <TableHead key={column.key} className="h-12">
                  <Button
                    variant="ghost"
                    onClick={() => column.sortable && handleSort(column.key)}
                    className="h-auto p-0 font-medium"
                    disabled={!column.sortable}
                  >
                    {column.label}
                    {column.sortable && (
                      <ArrowUpDown className="ml-2 h-4 w-4" />
                    )}
                  </Button>
                </TableHead>
              ))}
              <TableHead className="w-[100px]">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell
                  colSpan={visibleColumnDefs.length + 1}
                  className="h-24 text-center"
                >
                  Loading...
                </TableCell>
              </TableRow>
            ) : data.objects.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={visibleColumnDefs.length + 1}
                  className="h-24 text-center"
                >
                  No results found.
                </TableCell>
              </TableRow>
            ) : (
              data.objects.map((row) => (
                <TableRow key={row.id}>
                  {visibleColumnDefs.map((column) => {
                    const field = row.fields?.find((f) => f.key === column.key);
                    const value = field?.value;

                    return (
                      <TableCell key={column.key}>
                        {formatCellValue(value, column.type)}
                      </TableCell>
                    );
                  })}
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {row.actions?.map((action) => (
                        <Button
                          key={action.action}
                          variant="outline"
                          size="sm"
                          disabled={!action.available}
                        >
                          {action.label}
                        </Button>
                      ))}
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <p className="text-muted-foreground text-sm">
            Showing {Math.min((request.offset || 0) + 1, data.total)} to{' '}
            {Math.min(
              (request.offset || 0) + (request.limit || 10),
              data.total
            )}{' '}
            of {data.total} results
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() =>
              handlePageChange((request.offset || 0) - (request.limit || 10))
            }
            disabled={request.offset === 0}
          >
            <ChevronLeft className="h-4 w-4" />
            Previous
          </Button>

          <span className="text-sm">
            Page {currentPage} of {totalPages}
          </span>

          <Button
            variant="outline"
            size="sm"
            onClick={() =>
              handlePageChange((request.offset || 0) + (request.limit || 10))
            }
            disabled={
              (request.offset || 0) + (request.limit || 10) >= data.total
            }
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
