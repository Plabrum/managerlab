import { useEffect, useState } from 'react';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type {
  ObjectTypes,
  TimeRange,
  Granularity,
  AggregationType,
  ColumnDefinitionSchema,
} from '@/openapi/ariveAPI.schemas';
import { oObjectTypeSchemaGetObjectSchema } from '@/openapi/objects/objects';
import type { WidgetQuery } from '@/types/dashboard';

interface QueryBuilderFormProps {
  query: WidgetQuery;
  onChange: (query: WidgetQuery) => void;
}

const OBJECT_TYPES: ObjectTypes[] = [
  'brands',
  'campaigns',
  'deliverables',
  'invoices',
  'users',
  'media',
];

const TIME_RANGES: Array<{ value: TimeRange; label: string }> = [
  { value: 'last_7_days', label: 'Last 7 Days' },
  { value: 'last_30_days', label: 'Last 30 Days' },
  { value: 'last_90_days', label: 'Last 90 Days' },
  { value: 'last_6_months', label: 'Last 6 Months' },
  { value: 'last_year', label: 'Last Year' },
  { value: 'year_to_date', label: 'Year to Date' },
  { value: 'month_to_date', label: 'Month to Date' },
  { value: 'all_time', label: 'All Time' },
];

const GRANULARITIES: Array<{ value: Granularity; label: string }> = [
  { value: 'automatic', label: 'Automatic' },
  { value: 'hour', label: 'Hourly' },
  { value: 'day', label: 'Daily' },
  { value: 'week', label: 'Weekly' },
  { value: 'month', label: 'Monthly' },
  { value: 'quarter', label: 'Quarterly' },
  { value: 'year', label: 'Yearly' },
];

const AGGREGATIONS: Array<{ value: AggregationType; label: string }> = [
  { value: 'count_', label: 'Count' },
  { value: 'sum', label: 'Sum' },
  { value: 'avg', label: 'Average' },
  { value: 'max', label: 'Maximum' },
  { value: 'min', label: 'Minimum' },
];

export function QueryBuilderForm({ query, onChange }: QueryBuilderFormProps) {
  const [availableFields, setAvailableFields] = useState<
    ColumnDefinitionSchema[]
  >([]);
  const [loadingFields, setLoadingFields] = useState(false);

  useEffect(() => {
    const fetchFields = async () => {
      if (!query.object_type) return;

      try {
        setLoadingFields(true);
        // Fetch the object schema to get column definitions
        const response = await oObjectTypeSchemaGetObjectSchema(
          query.object_type
        );
        setAvailableFields(response.columns);
      } catch (error) {
        console.error('Failed to fetch fields:', error);
        setAvailableFields([]);
      } finally {
        setLoadingFields(false);
      }
    };

    fetchFields();
  }, [query.object_type]);

  const updateQuery = (updates: Partial<WidgetQuery>) => {
    onChange({ ...query, ...updates });
  };

  return (
    <div className="space-y-4">
      {/* Object Type */}
      <div className="space-y-2">
        <Label htmlFor="object-type">Object Type</Label>
        <Select
          value={query.object_type}
          onValueChange={(value) => {
            updateQuery({ object_type: value as ObjectTypes, field: '' });
          }}
        >
          <SelectTrigger id="object-type">
            <SelectValue placeholder="Select object type" />
          </SelectTrigger>
          <SelectContent>
            {OBJECT_TYPES.map((type) => (
              <SelectItem key={type} value={type}>
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Field */}
      <div className="space-y-2">
        <Label htmlFor="field">Field</Label>
        <Select
          value={query.field}
          onValueChange={(value) => updateQuery({ field: value })}
          disabled={loadingFields || availableFields.length === 0}
        >
          <SelectTrigger id="field">
            <SelectValue
              placeholder={loadingFields ? 'Loading fields...' : 'Select field'}
            />
          </SelectTrigger>
          <SelectContent>
            {availableFields.map((field) => (
              <SelectItem key={field.key} value={field.key}>
                {field.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <p className="text-muted-foreground text-xs">
          Select the field you want to visualize
        </p>
      </div>

      {/* Time Range */}
      <div className="space-y-2">
        <Label htmlFor="time-range">Time Range</Label>
        <Select
          value={query.time_range ?? undefined}
          onValueChange={(value) =>
            updateQuery({ time_range: value as TimeRange })
          }
        >
          <SelectTrigger id="time-range">
            <SelectValue placeholder="Select time range" />
          </SelectTrigger>
          <SelectContent>
            {TIME_RANGES.map((range) => (
              <SelectItem key={range.value} value={range.value}>
                {range.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Aggregation */}
      <div className="space-y-2">
        <Label htmlFor="aggregation">Aggregation</Label>
        <Select
          value={query.aggregation ?? undefined}
          onValueChange={(value) =>
            updateQuery({ aggregation: value as AggregationType })
          }
        >
          <SelectTrigger id="aggregation">
            <SelectValue placeholder="Auto (based on field type)" />
          </SelectTrigger>
          <SelectContent>
            {AGGREGATIONS.map((agg) => (
              <SelectItem key={agg.value} value={agg.value}>
                {agg.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <p className="text-muted-foreground text-xs">
          How to aggregate the data (auto-detected if not specified)
        </p>
      </div>

      {/* Granularity */}
      <div className="space-y-2">
        <Label htmlFor="granularity">Granularity</Label>
        <Select
          value={query.granularity || 'automatic'}
          onValueChange={(value) =>
            updateQuery({ granularity: value as Granularity })
          }
        >
          <SelectTrigger id="granularity">
            <SelectValue placeholder="Automatic" />
          </SelectTrigger>
          <SelectContent>
            {GRANULARITIES.map((gran) => (
              <SelectItem key={gran.value} value={gran.value}>
                {gran.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <p className="text-muted-foreground text-xs">
          Time bucket size for grouping data
        </p>
      </div>
    </div>
  );
}
