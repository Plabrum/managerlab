'use client';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
} from '@/components/ui/select';
import {
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
} from 'lucide-react';

interface DataTablePaginationProps {
  total: number;
  limit: number;
  offset: number;
  onPaginationChange: (offset: number, limit: number) => void;
}

export function DataTablePagination({
  total,
  limit,
  offset,
  onPaginationChange,
}: DataTablePaginationProps) {
  const currentPage = Math.floor(offset / limit) + 1;
  const totalPages = Math.ceil(total / limit);
  const startItem = offset + 1;
  const endItem = Math.min(offset + limit, total);

  const handlePageChange = (page: number) => {
    const newOffset = (page - 1) * limit;
    onPaginationChange(newOffset, limit);
  };

  const handleLimitChange = (newLimit: string) => {
    const limitNum = Number.parseInt(newLimit);
    const newOffset = Math.floor(offset / limitNum) * limitNum;
    onPaginationChange(newOffset, limitNum);
  };

  if (total === 0) return null;

  return (
    <div className="flex items-center justify-between px-2 py-2">
      <div className="flex items-center text-sm font-medium">
        <Select value={limit.toString()} onValueChange={handleLimitChange}>
          <SelectTrigger className="h-auto w-auto border-0 bg-transparent ">
            {limit}
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="5">5</SelectItem>
            <SelectItem value="10">10</SelectItem>
            <SelectItem value="20">20</SelectItem>
            <SelectItem value="30">30</SelectItem>
            <SelectItem value="50">50</SelectItem>
            <SelectItem value="100">100</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="flex items-center space-x-6 lg:space-x-8">
        <div className="text-sm font-medium">
          {startItem}-{endItem} of {total}
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            className="hidden h-8 w-8 bg-transparent p-0 lg:flex"
            onClick={() => handlePageChange(1)}
            disabled={currentPage === 1}
          >
            <span className="sr-only">Go to first page</span>
            <ChevronsLeft className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            className="h-8 w-8 bg-transparent p-0"
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1}
          >
            <span className="sr-only">Go to previous page</span>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            className="h-8 w-8 bg-transparent p-0"
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
          >
            <span className="sr-only">Go to next page</span>
            <ChevronRight className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            className="hidden h-8 w-8 bg-transparent p-0 lg:flex"
            onClick={() => handlePageChange(totalPages)}
            disabled={currentPage === totalPages}
          >
            <span className="sr-only">Go to last page</span>
            <ChevronsRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
