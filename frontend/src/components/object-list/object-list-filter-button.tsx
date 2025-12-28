'use client';

import { useState } from 'react';
import { Filter, X, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type {
  ColumnDefinitionSchema,
  ObjectListRequestFiltersItem,
  TextFilterDefinition,
  TextFilterDefinitionOperation,
  RangeFilterDefinition,
  BooleanFilterDefinition,
  EnumFilterDefinition,
} from '@/openapi/ariveAPI.schemas';
import { cn } from '@/lib/utils';

interface ObjectListFilterButtonProps {
  columns: ColumnDefinitionSchema[];
  filters: ObjectListRequestFiltersItem[];
  onFiltersChange: (filters: ObjectListRequestFiltersItem[]) => void;
}

type OperatorOption = {
  value: string;
  label: string;
};

// Operator options for each filter type
const TEXT_OPERATORS: OperatorOption[] = [
  { value: 'contains', label: 'contains' },
  { value: 'starts_with', label: 'starts with' },
  { value: 'ends_with', label: 'ends with' },
  { value: 'equals', label: 'equals' },
];

const RANGE_OPERATORS: OperatorOption[] = [
  { value: 'equals', label: 'equals' },
  { value: 'greater_than_or_equal', label: 'is at least' },
  { value: 'less_than_or_equal', label: 'is at most' },
];

const BOOLEAN_OPERATORS: OperatorOption[] = [{ value: 'equals', label: 'is' }];

const ENUM_OPERATORS: OperatorOption[] = [{ value: 'equals', label: 'is' }];

export function ObjectListFilterButton({
  columns,
  filters,
  onFiltersChange,
}: ObjectListFilterButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedColumnKey, setSelectedColumnKey] = useState<string>('');
  const [operation, setOperation] = useState<string>('');
  const [value, setValue] = useState<string>('');
  const [selectedEnumValues, setSelectedEnumValues] = useState<string[]>([]);

  // Get filterable columns (exclude columns without filter_type or null_filter)
  const filterableColumns = columns.filter(
    (col) => col.filter_type && col.filter_type !== 'null_filter'
  );

  // Auto-select first column when popover opens
  const handleOpenChange = (open: boolean) => {
    setIsOpen(open);
    if (open && !selectedColumnKey && filterableColumns.length > 0) {
      const firstCol = filterableColumns[0];
      setSelectedColumnKey(firstCol.key);
      // Set default operation based on filter type
      const operators = getOperatorsForColumn(firstCol);
      if (operators.length > 0) {
        setOperation(operators[0].value);
      }
    }
    if (!open) {
      // Reset form when closing
      setSelectedColumnKey('');
      setOperation('');
      setValue('');
      setSelectedEnumValues([]);
    }
  };

  const selectedColumn = selectedColumnKey
    ? filterableColumns.find((col) => col.key === selectedColumnKey)
    : null;

  const getOperatorsForColumn = (
    column: ColumnDefinitionSchema
  ): OperatorOption[] => {
    switch (column.filter_type) {
      case 'text_filter':
        return TEXT_OPERATORS;
      case 'range_filter':
        return RANGE_OPERATORS;
      case 'boolean_filter':
        return BOOLEAN_OPERATORS;
      case 'enum_filter':
        return ENUM_OPERATORS;
      default:
        return [];
    }
  };

  const currentOperators = selectedColumn
    ? getOperatorsForColumn(selectedColumn)
    : [];

  // Handle column change
  const handleColumnChange = (columnKey: string) => {
    setSelectedColumnKey(columnKey);
    const column = filterableColumns.find((col) => col.key === columnKey);
    if (column) {
      const operators = getOperatorsForColumn(column);
      setOperation(operators[0]?.value || '');
      setValue('');
      setSelectedEnumValues([]);
    }
  };

  // Toggle enum value selection
  const toggleEnumValue = (enumValue: string) => {
    setSelectedEnumValues((prev) =>
      prev.includes(enumValue)
        ? prev.filter((v) => v !== enumValue)
        : [...prev, enumValue]
    );
  };

  // Build filter based on column type
  const handleApplyFilter = () => {
    if (!selectedColumn || !operation) return;

    // For enum filters with multi-select
    if (
      selectedColumn.filter_type === 'enum_filter' &&
      selectedEnumValues.length === 0
    ) {
      return;
    }

    // For other filters, check value
    if (selectedColumn.filter_type !== 'enum_filter' && !value.trim()) {
      return;
    }

    let newFilter: ObjectListRequestFiltersItem;

    switch (selectedColumn.filter_type) {
      case 'text_filter':
        newFilter = {
          column: selectedColumn.key,
          operation: operation as TextFilterDefinitionOperation,
          value: value.trim(),
          type: 'text_filter',
        } as TextFilterDefinition;
        break;
      case 'range_filter': {
        const numValue = parseFloat(value);

        // Validate numeric input
        if (isNaN(numValue)) {
          return;
        }

        // Map operation to start/finish range
        let start: number | null = null;
        let finish: number | null = null;

        switch (operation) {
          case 'equals':
            start = numValue;
            finish = numValue;
            break;
          case 'greater_than_or_equal':
            start = numValue;
            break;
          case 'less_than_or_equal':
            finish = numValue;
            break;
        }

        newFilter = {
          column: selectedColumn.key,
          start: start ?? undefined,
          finish: finish ?? undefined,
          type: 'range_filter',
        } as RangeFilterDefinition;
        break;
      }
      case 'boolean_filter':
        newFilter = {
          column: selectedColumn.key,
          value: value === 'true',
          type: 'boolean_filter',
        } as BooleanFilterDefinition;
        break;
      case 'enum_filter': {
        // Create a single filter with multiple values
        const enumFilter: EnumFilterDefinition = {
          column: selectedColumn.key,
          values: selectedEnumValues,
          type: 'enum_filter',
        };
        onFiltersChange([...filters, enumFilter]);
        setIsOpen(false);
        setValue('');
        setSelectedEnumValues([]);
        return;
      }
      default:
        return;
    }

    // Add new filter to existing filters
    onFiltersChange([...filters, newFilter]);

    // Close popover and reset
    setIsOpen(false);
    setValue('');
    setSelectedEnumValues([]);
  };

  // Render value input based on column type
  const renderValueInput = () => {
    if (!selectedColumn) return null;

    switch (selectedColumn.filter_type) {
      case 'text_filter':
        return (
          <Input
            placeholder="value"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleApplyFilter();
              }
            }}
            className="border-border/50 bg-muted/30 h-9 flex-1 text-sm"
          />
        );
      case 'range_filter':
        return (
          <Input
            type="number"
            placeholder="number"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleApplyFilter();
              }
            }}
            className="border-border/50 bg-muted/30 h-9 flex-1 text-sm"
          />
        );
      case 'boolean_filter':
        return (
          <Select value={value} onValueChange={setValue}>
            <SelectTrigger className="border-border/50 bg-muted/30 h-9 flex-1 text-sm">
              <SelectValue placeholder="select" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="true">True</SelectItem>
              <SelectItem value="false">False</SelectItem>
            </SelectContent>
          </Select>
        );
      case 'enum_filter':
        return (
          <Popover>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                className="border-border/50 bg-muted/30 h-9 flex-1 justify-start text-sm font-normal"
              >
                {selectedEnumValues.length > 0
                  ? `${selectedEnumValues.length} selected`
                  : 'select values'}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-[200px] p-2" align="start">
              <div className="space-y-1">
                {(selectedColumn.available_values || []).map((val) => (
                  <button
                    key={val}
                    onClick={() => toggleEnumValue(val)}
                    className={cn(
                      'hover:bg-accent flex w-full items-center gap-2 rounded px-2 py-1.5 text-left text-sm transition-colors',
                      selectedEnumValues.includes(val) && 'bg-accent'
                    )}
                  >
                    <div
                      className={cn(
                        'border-border flex h-4 w-4 items-center justify-center rounded border',
                        selectedEnumValues.includes(val) &&
                          'bg-foreground border-foreground'
                      )}
                    >
                      {selectedEnumValues.includes(val) && (
                        <Check className="text-background h-3 w-3" />
                      )}
                    </div>
                    {val}
                  </button>
                ))}
              </div>
            </PopoverContent>
          </Popover>
        );
      default:
        return null;
    }
  };

  const activeFilterCount = filters.length;
  const hasActiveFilters = activeFilterCount > 0;
  const canApply =
    selectedColumn &&
    operation &&
    (selectedColumn.filter_type === 'enum_filter'
      ? selectedEnumValues.length > 0
      : value.trim().length > 0);

  return (
    <Popover open={isOpen} onOpenChange={handleOpenChange}>
      <PopoverTrigger asChild>
        <Button
          variant={hasActiveFilters ? 'default' : 'outline'}
          size="sm"
          className={cn(
            'gap-2 transition-all duration-200',
            hasActiveFilters &&
              'bg-foreground text-background hover:bg-foreground/90'
          )}
        >
          <Filter className="h-3.5 w-3.5" />
          <span className="text-sm font-medium">
            {hasActiveFilters ? (
              <>
                Filters{' '}
                <span className="bg-background/20 ml-1 rounded-full px-1.5 py-0.5 text-xs">
                  {activeFilterCount}
                </span>
              </>
            ) : (
              'Filter'
            )}
          </span>
        </Button>
      </PopoverTrigger>
      <PopoverContent
        align="start"
        className="border-border/50 bg-background w-[520px] p-0 shadow-lg backdrop-blur-sm"
      >
        {/* Header */}
        <div className="border-border/50 border-b px-4 py-3">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold tracking-tight">Add Filter</h4>
            <button
              onClick={() => setIsOpen(false)}
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Sentence-based filter builder */}
        <div className="p-4">
          <div className="flex items-center gap-2">
            {/* Column selector */}
            <Select
              value={selectedColumnKey}
              onValueChange={handleColumnChange}
            >
              <SelectTrigger className="border-border/50 bg-muted/30 h-9 w-[140px] text-sm font-medium">
                <SelectValue placeholder="field" />
              </SelectTrigger>
              <SelectContent>
                {filterableColumns.map((column) => (
                  <SelectItem key={column.key} value={column.key}>
                    {column.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* Operation selector */}
            <Select value={operation} onValueChange={setOperation}>
              <SelectTrigger className="border-border/50 bg-muted/30 h-9 w-[140px] text-sm">
                <SelectValue placeholder="operator" />
              </SelectTrigger>
              <SelectContent>
                {currentOperators.map((op) => (
                  <SelectItem key={op.value} value={op.value}>
                    {op.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* Value input */}
            {renderValueInput()}

            {/* Apply button */}
            <Button
              onClick={handleApplyFilter}
              disabled={!canApply}
              size="sm"
              className="h-9 gap-1.5"
            >
              <Check className="h-3.5 w-3.5" />
              Apply
            </Button>
          </div>

          {/* Helper text */}
          <p className="text-muted-foreground mt-3 text-xs">
            Filters will appear below the search bar after applying
          </p>
        </div>
      </PopoverContent>
    </Popover>
  );
}
