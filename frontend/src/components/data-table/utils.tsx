import { Badge } from '@/components/ui/badge';
import { Image } from '@/components/ui/image';
import { humanizeEnumValue } from '@/lib/format';
import type {
  SortDefinition,
  ObjectListRequestFiltersItem,
  ObjectListRequest,
  ColumnDefinitionSchema,
  ObjectFieldDTO,
} from '@/openapi/ariveAPI.schemas';
import type { SortingState, ColumnFiltersState } from '@tanstack/react-table';

// Type definitions for filter values
type TextFilterValue = {
  operation: string;
  value: string;
};

type RangeFilterValue = {
  start?: number;
  finish?: number;
};

type DateFilterValue = {
  start?: string;
  finish?: string;
};

/**
 * Convert React Table SortingState to API SortDefinition array
 */
export function sortingStateToSortDefinitions(
  sorting: SortingState
): SortDefinition[] {
  return sorting.map((sort) => ({
    column: sort.id,
    direction: sort.desc ? 'sort_desc' : 'sort_asc',
  }));
}

/**
 * Convert React Table pagination state to API offset/limit
 */
export function paginationStateToRequest(paginationState: {
  pageIndex: number;
  pageSize: number;
}): { offset: number; limit: number } {
  return {
    offset: paginationState.pageIndex * paginationState.pageSize,
    limit: paginationState.pageSize,
  };
}

/**
 * Convert React Table ColumnFiltersState to API ObjectListRequestFiltersItem array
 */
export function columnFiltersToRequestFilters(
  columnFilters: ColumnFiltersState,
  columnDefs: ColumnDefinitionSchema[]
): ObjectListRequestFiltersItem[] {
  return columnFilters.map((filter) => {
    const columnDef = columnDefs.find((def) => def.key === filter.id);
    const filterType = columnDef?.filter_type || 'text_filter';

    // Handle different filter value types based on the column's filter type
    switch (filterType) {
      case 'text_filter':
        if (
          typeof filter.value === 'object' &&
          filter.value !== null &&
          'operation' in filter.value
        ) {
          const textValue = filter.value as TextFilterValue;
          return {
            column: filter.id,
            operation: textValue.operation || 'contains',
            value: textValue.value || String(filter.value),
            type: 'text_filter',
          } as ObjectListRequestFiltersItem;
        }
        return {
          column: filter.id,
          operation: 'contains',
          value: String(filter.value),
          type: 'text_filter',
        } as ObjectListRequestFiltersItem;

      case 'enum_filter':
        return {
          column: filter.id,
          values: Array.isArray(filter.value)
            ? filter.value
            : [String(filter.value)],
          type: 'enum_filter',
        } as ObjectListRequestFiltersItem;

      case 'object_filter':
        return {
          column: filter.id,
          values: Array.isArray(filter.value)
            ? filter.value
            : [String(filter.value)],
          type: 'object_filter',
        } as ObjectListRequestFiltersItem;

      case 'range_filter':
        if (typeof filter.value === 'object' && filter.value !== null) {
          const rangeValue = filter.value as RangeFilterValue;
          return {
            column: filter.id,
            start: rangeValue.start,
            finish: rangeValue.finish,
            type: 'range_filter',
          } as ObjectListRequestFiltersItem;
        }
        return {
          column: filter.id,
          start: undefined,
          finish: undefined,
          type: 'range_filter',
        } as ObjectListRequestFiltersItem;

      case 'date_filter':
        if (typeof filter.value === 'object' && filter.value !== null) {
          const dateValue = filter.value as DateFilterValue;
          return {
            column: filter.id,
            start: dateValue.start,
            finish: dateValue.finish,
            type: 'date_filter',
          } as ObjectListRequestFiltersItem;
        }
        return {
          column: filter.id,
          start: undefined,
          finish: undefined,
          type: 'date_filter',
        } as ObjectListRequestFiltersItem;

      case 'boolean_filter':
        return {
          column: filter.id,
          value: Boolean(filter.value),
          type: 'boolean_filter',
        } as ObjectListRequestFiltersItem;

      default:
        // Fallback to text filter
        return {
          column: filter.id,
          operation: 'contains',
          value: String(filter.value),
          type: 'text_filter',
        } as ObjectListRequestFiltersItem;
    }
  });
}

/**
 * Convert API ObjectListRequestFiltersItem array to React Table ColumnFiltersState
 */
export function requestFiltersToColumnFilters(
  requestFilters: ObjectListRequestFiltersItem[]
): ColumnFiltersState {
  return requestFilters.map((filter) => {
    let value: unknown;

    switch (filter.type) {
      case 'text_filter':
        value = {
          operation: filter.operation,
          value: filter.value,
        };
        break;

      case 'enum_filter':
        value = filter.values;
        break;

      case 'object_filter':
        value = filter.values;
        break;

      case 'range_filter':
        value = {
          start: filter.start,
          finish: filter.finish,
        };
        break;

      case 'date_filter':
        value = {
          start: filter.start,
          finish: filter.finish,
        };
        break;

      case 'boolean_filter':
        value = filter.value;
        break;

      default:
        value = (filter as unknown as { value: unknown }).value;
    }

    return {
      id: filter.column,
      value,
    };
  });
}

/**
 * Create a complete ObjectListRequest from table state
 */
export function createObjectListRequest(
  _objectType: string,
  paginationState: { pageIndex: number; pageSize: number },
  sortingState: SortingState,
  columnFilters: ColumnFiltersState,
  options: {
    columnDefs?: ColumnDefinitionSchema[];
    search?: string;
  } = {}
): ObjectListRequest {
  const { offset, limit } = paginationStateToRequest(paginationState);
  const { columnDefs, search } = options;

  return {
    offset,
    limit,
    sorts: sortingStateToSortDefinitions(sortingState),
    // Only process filters if we have columnDefs, otherwise return empty array
    filters:
      columnDefs && columnFilters.length > 0
        ? columnFiltersToRequestFilters(columnFilters, columnDefs)
        : [],
    search: search && search.trim().length > 0 ? search : undefined,
  };
}

/**
 * Get color variant for enum badge based on value and available values
 */
function getEnumBadgeVariant(value: string, availableValues?: string[]) {
  if (!availableValues || availableValues.length === 0) {
    return 'secondary';
  }

  const index = availableValues.indexOf(value);
  if (index === -1) return 'secondary';

  // Color mapping based on position in available values
  const variants = [
    'default', // First value - neutral
    'secondary', // Second value - gray
    'destructive', // Third value - red
    'outline', // Fourth value - outline
  ] as const;

  return variants[index % variants.length];
}

/**
 * Get status-based color for common enum patterns
 */
function getStatusBadgeVariant(value: string) {
  const lowerValue = value.toLowerCase();

  // Success states
  if (
    [
      'active',
      'completed',
      'success',
      'approved',
      'published',
      'online',
      'enabled',
      'verified',
      'confirmed',
    ].includes(lowerValue)
  ) {
    return 'default'; // Green-ish
  }

  // Warning states
  if (
    [
      'pending',
      'draft',
      'review',
      'waiting',
      'processing',
      'scheduled',
    ].includes(lowerValue)
  ) {
    return 'secondary'; // Yellow-ish
  }

  // Error/danger states
  if (
    [
      'failed',
      'error',
      'rejected',
      'cancelled',
      'disabled',
      'offline',
      'expired',
      'blocked',
    ].includes(lowerValue)
  ) {
    return 'destructive'; // Red
  }

  // Neutral states
  return 'outline';
}

/**
 * Robust cell value formatter with proper type handling and enum color coding
 * Now handles discriminated union field values from backend
 */

export function formatCellValue(
  columnDef: ColumnDefinitionSchema,
  field?: ObjectFieldDTO
): React.ReactNode {
  if (!field || field.value === null || field.value === undefined) {
    return '-';
  }

  const value = field.value;

  switch (value.type) {
    case 'image':
      // Image field with url and optional thumbnail_url
      if (value.url) {
        return (
          <div className="flex items-center gap-2">
            <Image
              src={value.thumbnail_url || value.url}
              alt="Image"
              className="h-16 w-16 rounded-md border object-cover transition-transform hover:scale-105"
            />
          </div>
        );
      }
      return '-';

    case 'date':
    case 'datetime':
      try {
        if (value.value) {
          return new Date(value.value).toLocaleDateString();
        }
        return '-';
      } catch {
        return String(value.value);
      }

    case 'usd':
      try {
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD',
        }).format(value.value);
      } catch {
        return String(value.value);
      }

    case 'bool':
      return (
        <Badge variant={value.value ? 'default' : 'secondary'}>
          {value.value ? 'Yes' : 'No'}
        </Badge>
      );

    case 'url':
      if (value.value) {
        return (
          <a
            href={value.value}
            className="text-blue-600 hover:underline dark:text-blue-400"
            onClick={(e) => e.stopPropagation()}
            target="_blank"
            rel="noopener noreferrer"
          >
            {value.label || String(value.value)}
          </a>
        );
      }
      return '-';

    case 'object':
      if (value.value) {
        return (
          <a
            href={`/${value.object_type}/${value.value}`}
            className="text-blue-600 hover:underline dark:text-blue-400"
            onClick={(e) => e.stopPropagation()}
          >
            {value.label || String(value.value)}
          </a>
        );
      }
      return '-';

    case 'enum': {
      const stringValue = String(value.value);
      // Try status-based coloring first, then fall back to position-based
      const statusVariant = getStatusBadgeVariant(stringValue);
      const variant =
        statusVariant !== 'outline'
          ? statusVariant
          : getEnumBadgeVariant(
              stringValue,
              columnDef.available_values || undefined
            );

      return <Badge variant={variant}>{humanizeEnumValue(stringValue)}</Badge>;
    }

    case 'int':
    case 'float': {
      if (
        'value' in value &&
        value.value !== null &&
        value.value !== undefined
      ) {
        const rawValue = value.value;

        // Handle numeric values
        if (typeof rawValue === 'number') {
          return (
            <div className="text-right font-mono">
              {rawValue.toLocaleString()}
            </div>
          );
        }

        // Handle string values that might be numbers
        if (typeof rawValue === 'string') {
          const numValue = parseFloat(rawValue);
          return (
            <div className="text-right font-mono">
              {isNaN(numValue) ? rawValue : numValue.toLocaleString()}
            </div>
          );
        }

        // Fallback for other types
        return <div className="text-right font-mono">{String(rawValue)}</div>;
      }
      return '-';
    }

    case 'string':
    case 'text':
    case 'email':
    default: {
      const stringValue = String(value.value || '');
      return (
        <div className="max-w-[200px] truncate" title={stringValue}>
          {stringValue}
        </div>
      );
    }
  }
}
