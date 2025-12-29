import {
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
} from '@/components/ui/select';
import type { Table } from '@tanstack/react-table';

interface DataTablePaginationProps<TData> {
  table: Table<TData>;
  enableRowSelection?: boolean;
  pageSizeOptions?: number[];
  showItemRange?: boolean; // Show "X-Y of Z" instead of "Page X of Y"
}

export function DataTablePagination<TData>({
  table,
  enableRowSelection = false,
  pageSizeOptions = [5, 10, 20, 30, 50, 100],
  showItemRange = false,
}: DataTablePaginationProps<TData>) {
  // Calculate range information like the old component
  const currentPage = table.getState().pagination.pageIndex + 1;
  const pageSize = table.getState().pagination.pageSize;
  const totalRows = table.getFilteredRowModel().rows.length;
  const startItem = (currentPage - 1) * pageSize + 1;
  const endItem = Math.min(currentPage * pageSize, totalRows);
  return (
    <div className="flex items-center justify-between px-2 py-2">
      {/* Left side - Page size selector (mirrors old component) */}
      <div className="flex items-center text-sm font-medium">
        <Select
          value={`${table.getState().pagination.pageSize}`}
          onValueChange={(value) => {
            table.setPageSize(Number(value));
          }}
        >
          <SelectTrigger className="h-auto w-auto border-0 bg-transparent">
            {table.getState().pagination.pageSize}
          </SelectTrigger>
          <SelectContent>
            {pageSizeOptions.map((pageSize) => (
              <SelectItem key={pageSize} value={`${pageSize}`}>
                {pageSize}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Right side - Range/Page info and controls */}
      <div className="flex items-center space-x-6 lg:space-x-8">
        {/* Row selection display (if enabled) */}
        {enableRowSelection && (
          <div className="text-muted-foreground text-sm font-medium">
            {table.getFilteredSelectedRowModel().rows.length} of{' '}
            {table.getFilteredRowModel().rows.length} row(s) selected
          </div>
        )}

        {/* Range or page display */}
        <div className="text-sm font-medium">
          {showItemRange
            ? totalRows === 0
              ? '0-0 of 0'
              : `${startItem}-${endItem} of ${totalRows}`
            : `Page ${table.getState().pagination.pageIndex + 1} of ${table.getPageCount()}`}
        </div>

        {/* Navigation buttons */}
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            className="hidden h-8 w-8 bg-transparent p-0 lg:flex"
            onClick={() => table.setPageIndex(0)}
            disabled={!table.getCanPreviousPage()}
          >
            <span className="sr-only">Go to first page</span>
            <ChevronsLeft className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            className="h-8 w-8 bg-transparent p-0"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            <span className="sr-only">Go to previous page</span>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            className="h-8 w-8 bg-transparent p-0"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            <span className="sr-only">Go to next page</span>
            <ChevronRight className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            className="hidden h-8 w-8 bg-transparent p-0 lg:flex"
            onClick={() => table.setPageIndex(table.getPageCount() - 1)}
            disabled={!table.getCanNextPage()}
          >
            <span className="sr-only">Go to last page</span>
            <ChevronsRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
