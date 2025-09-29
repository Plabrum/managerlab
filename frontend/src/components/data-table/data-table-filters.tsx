'use client';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Calendar } from '@/components/ui/calendar';
import { CalendarIcon, X } from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';
import type {
  ColumnDefinitionDTO,
  ObjectListRequestFiltersItem,
  TextFilterDefinitionOperation,
} from '@/openapi/managerLab.schemas';

interface DataTableFiltersProps {
  columns: ColumnDefinitionDTO[];
  filters: ObjectListRequestFiltersItem[];
  onFiltersChange: (filters: ObjectListRequestFiltersItem[]) => void;
}

export function DataTableFilters({
  columns,
  filters,
  onFiltersChange,
}: DataTableFiltersProps) {
  const addFilter = (column: ColumnDefinitionDTO) => {
    const filterType = column.available_filters?.[0] || 'text_filter';
    let newFilter: ObjectListRequestFiltersItem;

    if (filterType === 'text_filter') {
      newFilter = {
        column: column.key,
        type: 'text_filter',
        operation: 'contains',
        value: '',
      };
    } else if (filterType === 'range_filter') {
      newFilter = {
        column: column.key,
        type: 'range_filter',
        start: null,
        finish: null,
      };
    } else if (filterType === 'date_filter') {
      newFilter = {
        column: column.key,
        type: 'date_filter',
        start: null,
        finish: null,
      };
    } else if (filterType === 'boolean_filter') {
      newFilter = {
        column: column.key,
        type: 'boolean_filter',
        value: false,
      };
    } else {
      newFilter = {
        column: column.key,
        type: 'text_filter',
        operation: 'contains',
        value: '',
      };
    }

    onFiltersChange([...filters, newFilter]);
  };

  const updateTextFilter = (
    index: number,
    updates: Partial<{
      operation: TextFilterDefinitionOperation;
      value: string;
    }>
  ) => {
    const newFilters = [...filters];
    const currentFilter = newFilters[index];
    if (currentFilter.type === 'text_filter') {
      newFilters[index] = { ...currentFilter, ...updates };
      onFiltersChange(newFilters);
    }
  };

  const updateRangeFilter = (
    index: number,
    updates: Partial<{ start: number | null; finish: number | null }>
  ) => {
    const newFilters = [...filters];
    const currentFilter = newFilters[index];
    if (currentFilter.type === 'range_filter') {
      newFilters[index] = { ...currentFilter, ...updates };
      onFiltersChange(newFilters);
    }
  };

  const updateDateFilter = (
    index: number,
    updates: Partial<{ start: string | null; finish: string | null }>
  ) => {
    const newFilters = [...filters];
    const currentFilter = newFilters[index];
    if (currentFilter.type === 'date_filter') {
      newFilters[index] = { ...currentFilter, ...updates };
      onFiltersChange(newFilters);
    }
  };

  const updateBooleanFilter = (
    index: number,
    updates: Partial<{ value: boolean }>
  ) => {
    const newFilters = [...filters];
    const currentFilter = newFilters[index];
    if (currentFilter.type === 'boolean_filter') {
      newFilters[index] = { ...currentFilter, ...updates };
      onFiltersChange(newFilters);
    }
  };

  const removeFilter = (index: number) => {
    onFiltersChange(filters.filter((_, i) => i !== index));
  };

  const availableColumns = columns.filter(
    (col) =>
      col.available_filters &&
      col.available_filters.length > 0 &&
      !filters.some((filter) => filter.column === col.key)
  );

  return (
    <div className="space-y-2">
      {filters.map((filter, index) => (
        <FilterRow
          key={`${filter.column}-${index}`}
          filter={filter}
          columns={columns}
          onUpdateText={(updates) => updateTextFilter(index, updates)}
          onUpdateRange={(updates) => updateRangeFilter(index, updates)}
          onUpdateDate={(updates) => updateDateFilter(index, updates)}
          onUpdateBoolean={(updates) => updateBooleanFilter(index, updates)}
          onRemove={() => removeFilter(index)}
        />
      ))}

      {availableColumns.length > 0 && (
        <Select
          onValueChange={(columnKey) => {
            const column = columns.find((col) => col.key === columnKey);
            if (column) addFilter(column);
          }}
        >
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Add filter..." />
          </SelectTrigger>
          <SelectContent>
            {availableColumns.map((column) => (
              <SelectItem key={column.key} value={column.key}>
                {column.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      )}
    </div>
  );
}

interface FilterRowProps {
  filter: ObjectListRequestFiltersItem;
  columns: ColumnDefinitionDTO[];
  onUpdateText: (
    updates: Partial<{
      operation: TextFilterDefinitionOperation;
      value: string;
    }>
  ) => void;
  onUpdateRange: (
    updates: Partial<{ start: number | null; finish: number | null }>
  ) => void;
  onUpdateDate: (
    updates: Partial<{ start: string | null; finish: string | null }>
  ) => void;
  onUpdateBoolean: (updates: Partial<{ value: boolean }>) => void;
  onRemove: () => void;
}

function FilterRow({
  filter,
  columns,
  onUpdateText,
  onUpdateRange,
  onUpdateDate,
  onUpdateBoolean,
  onRemove,
}: FilterRowProps) {
  const column = columns.find((col) => col.key === filter.column);
  if (!column) return null;

  const handleTextOperationChange = (operation: string) => {
    onUpdateText({ operation: operation as TextFilterDefinitionOperation });
  };

  const handleTextValueChange = (value: string) => {
    onUpdateText({ value });
  };

  const handleRangeStartChange = (value: string) => {
    onUpdateRange({ start: value ? Number(value) : null });
  };

  const handleRangeFinishChange = (value: string) => {
    onUpdateRange({ finish: value ? Number(value) : null });
  };

  const handleDateStartChange = (date: Date | undefined) => {
    onUpdateDate({ start: date?.toISOString() || null });
  };

  const handleDateFinishChange = (date: Date | undefined) => {
    onUpdateDate({ finish: date?.toISOString() || null });
  };

  const handleBooleanValueChange = (value: string) => {
    onUpdateBoolean({ value: value === 'true' });
  };

  return (
    <div className="flex items-center gap-2 rounded-md border p-2">
      <span className="min-w-[100px] text-sm font-medium">{column.label}</span>

      {filter.type === 'text_filter' && (
        <>
          <Select
            value={filter.operation}
            onValueChange={handleTextOperationChange}
          >
            <SelectTrigger className="w-[120px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="contains">Contains</SelectItem>
              <SelectItem value="starts_with">Starts with</SelectItem>
              <SelectItem value="ends_with">Ends with</SelectItem>
              <SelectItem value="equals">Equals</SelectItem>
            </SelectContent>
          </Select>
          <Input
            placeholder="Value..."
            value={filter.value || ''}
            onChange={(e) => handleTextValueChange(e.target.value)}
            className="w-[200px]"
          />
        </>
      )}

      {filter.type === 'range_filter' && (
        <>
          <Input
            type="number"
            placeholder="Min"
            value={filter.start || ''}
            onChange={(e) => handleRangeStartChange(e.target.value)}
            className="w-[100px]"
          />
          <span className="text-muted-foreground text-sm">to</span>
          <Input
            type="number"
            placeholder="Max"
            value={filter.finish || ''}
            onChange={(e) => handleRangeFinishChange(e.target.value)}
            className="w-[100px]"
          />
        </>
      )}

      {filter.type === 'date_filter' && (
        <>
          <DatePicker
            date={filter.start ? new Date(filter.start) : undefined}
            onDateChange={handleDateStartChange}
            placeholder="Start date"
          />
          <span className="text-muted-foreground text-sm">to</span>
          <DatePicker
            date={filter.finish ? new Date(filter.finish) : undefined}
            onDateChange={handleDateFinishChange}
            placeholder="End date"
          />
        </>
      )}

      {filter.type === 'boolean_filter' && (
        <Select
          value={filter.value ? 'true' : 'false'}
          onValueChange={handleBooleanValueChange}
        >
          <SelectTrigger className="w-[120px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="true">True</SelectItem>
            <SelectItem value="false">False</SelectItem>
          </SelectContent>
        </Select>
      )}

      <Button variant="ghost" size="sm" onClick={onRemove}>
        <X className="h-4 w-4" />
      </Button>
    </div>
  );
}

interface DatePickerProps {
  date?: Date;
  onDateChange: (date: Date | undefined) => void;
  placeholder: string;
}

function DatePicker({ date, onDateChange, placeholder }: DatePickerProps) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          className={cn(
            'w-[140px] justify-start text-left font-normal',
            !date && 'text-muted-foreground'
          )}
        >
          <CalendarIcon className="mr-2 h-4 w-4" />
          {date ? format(date, 'PPP') : placeholder}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0">
        <Calendar
          mode="single"
          selected={date}
          onSelect={onDateChange}
          initialFocus
        />
      </PopoverContent>
    </Popover>
  );
}
