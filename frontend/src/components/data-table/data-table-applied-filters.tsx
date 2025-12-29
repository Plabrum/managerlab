import { useMemo } from 'react';
import { X } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { humanizeEnumValue } from '@/lib/format';
import { columnFiltersToRequestFilters } from './utils';
import type {
  ColumnDefinitionSchema,
  ObjectListRequestFiltersItem,
} from '@/openapi/ariveAPI.schemas';
import type { ColumnFiltersState } from '@tanstack/react-table';

type DataTableAppliedFiltersProps = {
  filters: ColumnFiltersState;
  columnDefs: ColumnDefinitionSchema[];
  onUpdate: (filters: ColumnFiltersState) => void;
};

export function DataTableAppliedFilters({
  filters,
  columnDefs,
  onUpdate,
}: DataTableAppliedFiltersProps) {
  const filterDetails = useMemo(() => {
    const requestFilters = columnFiltersToRequestFilters(filters, columnDefs);
    return filters.map((_filter, index) => ({
      index,
      requestFilter: requestFilters[index],
    }));
  }, [filters, columnDefs]);

  const completeFilters = filterDetails.filter(({ requestFilter }) =>
    isFilterComplete(requestFilter)
  );

  if (completeFilters.length === 0) {
    return null;
  }

  const handleRemove = (indexToRemove: number) => {
    const nextFilters = filters.filter((_, idx) => idx !== indexToRemove);
    onUpdate(nextFilters);
  };

  return (
    <div className="mb-4 flex flex-wrap items-center gap-2">
      {completeFilters.map(({ requestFilter, index }) => (
        <Badge
          key={`${requestFilter.column}-${index}`}
          variant="secondary"
          className="gap-1"
        >
          {getFilterDisplayText(requestFilter, columnDefs)}
          <Button
            variant="ghost"
            size="sm"
            className="h-auto p-0 hover:bg-transparent"
            onClick={() => handleRemove(index)}
          >
            <X className="h-3 w-3" />
          </Button>
        </Badge>
      ))}
    </div>
  );
}

function isFilterComplete(filter?: ObjectListRequestFiltersItem) {
  if (!filter) return false;

  switch (filter.type) {
    case 'text_filter':
      return Boolean(filter.value);
    case 'range_filter':
      return filter.start !== null || filter.finish !== null;
    case 'date_filter':
      return Boolean(filter.start) || Boolean(filter.finish);
    case 'boolean_filter':
      return (
        'value' in filter && typeof filter.value === 'boolean' && filter.value
      );
    case 'enum_filter':
      return Array.isArray(filter.values) && filter.values.length > 0;
    default:
      return false;
  }
}

function getFilterDisplayText(
  filter: ObjectListRequestFiltersItem,
  columnDefs: ColumnDefinitionSchema[]
) {
  const column = columnDefs.find((col) => col.key === filter.column);
  if (!column) return '';

  let text = `${column.label}: `;

  switch (filter.type) {
    case 'text_filter':
      if (filter.value) {
        text += `${filter.operation} "${filter.value}"`;
      }
      break;
    case 'range_filter':
      if (filter.start !== null || filter.finish !== null) {
        text += `${filter.start ?? '∞'} - ${filter.finish ?? '∞'}`;
      }
      break;
    case 'date_filter':
      if (filter.start || filter.finish) {
        const formatDate = (value?: string | null) =>
          value ? new Date(value).toLocaleDateString() : '∞';
        text += `${formatDate(filter.start)} - ${formatDate(filter.finish)}`;
      }
      break;
    case 'boolean_filter':
      if ('value' in filter && typeof filter.value === 'boolean') {
        text += filter.value ? 'Yes' : 'No';
      }
      break;
    case 'enum_filter':
      if (Array.isArray(filter.values)) {
        text += filter.values.map(humanizeEnumValue).join(', ');
      }
      break;
    default:
      break;
  }

  return text;
}
