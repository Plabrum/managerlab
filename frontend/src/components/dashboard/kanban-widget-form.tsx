import { useEffect, useState } from 'react';
import { Plus, X } from 'lucide-react';
import { EnumFilterField, ObjectFilterField } from '@/components/forms/filters';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  ObjectTypes,
  TimeRange,
  type WidgetQuerySchema,
  type ColumnDefinitionSchema,
  type EnumFilterDefinition,
  type ObjectFilterDefinition,
} from '@/openapi/ariveAPI.schemas';
import { oObjectTypeSchemaGetObjectSchema } from '@/openapi/objects/objects';

// Shared constants
const WIDGET_OBJECT_TYPES = [
  { value: ObjectTypes.brands, label: 'Brands' },
  { value: ObjectTypes.campaigns, label: 'Campaigns' },
  { value: ObjectTypes.deliverables, label: 'Deliverables' },
  { value: ObjectTypes.invoices, label: 'Invoices' },
  { value: ObjectTypes.roster, label: 'Roster' },
] as const;

const TIME_RANGE_OPTIONS = [
  { value: TimeRange.last_7_days, label: 'Last 7 days' },
  { value: TimeRange.last_30_days, label: 'Last 30 days' },
  { value: TimeRange.last_90_days, label: 'Last 90 days' },
  { value: TimeRange.last_6_months, label: 'Last 6 months' },
  { value: TimeRange.last_year, label: 'Last year' },
  { value: TimeRange.year_to_date, label: 'Year to date' },
  { value: TimeRange.month_to_date, label: 'Month to date' },
  { value: TimeRange.all_time, label: 'All time' },
] as const;

type FilterDefinition = EnumFilterDefinition | ObjectFilterDefinition;

interface KanbanWidgetFormFieldsProps {
  query: Partial<WidgetQuerySchema>;
  onChange: (query: WidgetQuerySchema) => void;
}

export function KanbanWidgetFormFields({
  query,
  onChange,
}: KanbanWidgetFormFieldsProps) {
  const [availableFields, setAvailableFields] = useState<
    ColumnDefinitionSchema[]
  >([]);
  const [availableStates, setAvailableStates] = useState<string[]>([]);
  const [selectedStates, setSelectedStates] = useState<string[]>(
    (query as any).states || [] // eslint-disable-line @typescript-eslint/no-explicit-any
  );
  const [filters, setFilters] = useState<FilterDefinition[]>(
    (query.filters as FilterDefinition[]) || []
  );

  // Fetch fields when object type changes
  useEffect(() => {
    const fetchFields = async () => {
      if (!query.object_type) {
        setAvailableFields([]);
        setAvailableStates([]);
        return;
      }

      try {
        const response = await oObjectTypeSchemaGetObjectSchema(
          query.object_type as ObjectTypes
        );
        setAvailableFields(response.columns);

        // Extract state field values for column filter
        const stateField = response.columns.find(
          (col) => col.key === 'state' && col.type === 'enum'
        );
        if (stateField?.available_values) {
          setAvailableStates(stateField.available_values);
          // If no states selected yet, select all by default
          if (!selectedStates.length) {
            setSelectedStates(stateField.available_values);
          }
        } else {
          setAvailableStates([]);
        }
      } catch (error) {
        console.error('Failed to fetch fields:', error);
        setAvailableFields([]);
        setAvailableStates([]);
      }
    };

    fetchFields();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query.object_type]);

  const handleObjectTypeChange = (value: string) => {
    // Update object_type and reset filters
    const newQuery: WidgetQuerySchema = {
      ...query,
      object_type: value as ObjectTypes,
      field: 'state', // Kanban always uses state field
      filters: [],
      states: selectedStates,
    } as any; // eslint-disable-line @typescript-eslint/no-explicit-any
    setFilters([]);
    onChange(newQuery);
  };

  const handleTimeRangeChange = (value: string) => {
    const newQuery: WidgetQuerySchema = {
      ...query,
      time_range: value as TimeRange,
      field: query.field || 'state',
      object_type: query.object_type as ObjectTypes,
      states: selectedStates,
    } as any; // eslint-disable-line @typescript-eslint/no-explicit-any
    onChange(newQuery);
  };

  const handleStatesChange = (values: string[]) => {
    setSelectedStates(values);
    const newQuery: WidgetQuerySchema = {
      ...query,
      field: query.field || 'state',
      object_type: query.object_type as ObjectTypes,
      states: values,
    } as any; // eslint-disable-line @typescript-eslint/no-explicit-any
    onChange(newQuery);
  };

  const handleAddFilter = () => {
    const newFilter: EnumFilterDefinition = {
      column: '',
      values: [],
      type: 'enum_filter',
    };
    const newFilters = [...filters, newFilter];
    setFilters(newFilters);
    updateQueryWithFilters(newFilters);
  };

  const handleRemoveFilter = (index: number) => {
    const newFilters = filters.filter((_, i) => i !== index);
    setFilters(newFilters);
    updateQueryWithFilters(newFilters);
  };

  const handleFilterColumnChange = (index: number, column: string) => {
    const newFilters = [...filters];
    const selectedField = availableFields.find((f) => f.key === column);

    // Reset values when column changes and update type based on field type
    if (selectedField?.type === 'object') {
      newFilters[index] = {
        column,
        values: [],
        type: 'object_filter',
      };
    } else {
      newFilters[index] = {
        column,
        values: [],
        type: 'enum_filter',
      };
    }

    setFilters(newFilters);
    updateQueryWithFilters(newFilters);
  };

  const handleFilterValuesChange = (index: number, values: string[]) => {
    const newFilters = [...filters];
    newFilters[index] = { ...newFilters[index], values };
    setFilters(newFilters);
    updateQueryWithFilters(newFilters);
  };

  const updateQueryWithFilters = (newFilters: FilterDefinition[]) => {
    const newQuery: WidgetQuerySchema = {
      ...query,
      field: query.field || 'state',
      object_type: query.object_type as ObjectTypes,
      filters: newFilters,
      states: selectedStates,
    } as any; // eslint-disable-line @typescript-eslint/no-explicit-any
    onChange(newQuery);
  };

  const getFieldOptions = (field: ColumnDefinitionSchema | undefined) => {
    if (!field || !field.available_values) return [];
    return field.available_values;
  };

  return (
    <div className="space-y-4">
      <div className="space-y-1.5">
        <label className="text-sm font-medium">Object Type</label>
        <Select
          value={query.object_type || undefined}
          onValueChange={handleObjectTypeChange}
        >
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Select object type..." />
          </SelectTrigger>
          <SelectContent>
            {WIDGET_OBJECT_TYPES.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <p className="text-muted-foreground text-xs">
          Select which type of objects to display in the kanban board
        </p>
      </div>

      <div className="space-y-1.5">
        <label className="text-sm font-medium">Time Range (Optional)</label>
        <Select
          value={query.time_range || undefined}
          onValueChange={handleTimeRangeChange}
        >
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Select time range..." />
          </SelectTrigger>
          <SelectContent>
            {TIME_RANGE_OPTIONS.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <p className="text-muted-foreground text-xs">
          Filter objects by creation date
        </p>
      </div>

      {/* Columns to Display */}
      {availableStates.length > 0 && (
        <div className="space-y-1.5">
          <label className="text-sm font-medium">Columns to Display</label>
          <div className="rounded-md border p-2">
            <EnumFilterField
              availableValues={availableStates}
              selectedValues={selectedStates}
              onChange={handleStatesChange}
              maxHeight="max-h-40"
            />
          </div>
          <p className="text-muted-foreground text-xs">
            Select which status columns to show on the kanban board
          </p>
        </div>
      )}

      {/* Filters Section */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium">Filters</label>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={handleAddFilter}
            disabled={!query.object_type}
          >
            <Plus className="mr-1 h-4 w-4" />
            Add Filter
          </Button>
        </div>

        {filters.length === 0 ? (
          <p className="text-muted-foreground text-xs">
            No filters applied. Click &quot;Add Filter&quot; to filter objects.
          </p>
        ) : (
          <div className="space-y-3">
            {filters.map((filter, index) => {
              const selectedField = availableFields.find(
                (f) => f.key === filter.column
              );
              const isEnumField =
                selectedField?.type === 'enum' &&
                selectedField.available_values;
              const isObjectField = selectedField?.type === 'object';

              return (
                <div key={index} className="space-y-2 rounded-md border p-3">
                  <div className="flex items-start justify-between">
                    <span className="text-sm font-medium">
                      Filter {index + 1}
                    </span>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveFilter(index)}
                      className="h-6 w-6 p-0"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>

                  <div className="space-y-3">
                    {/* Field selector */}
                    <div className="space-y-1">
                      <label className="text-xs font-medium">Field</label>
                      <Select
                        value={filter.column}
                        onValueChange={(value) =>
                          handleFilterColumnChange(index, value)
                        }
                      >
                        <SelectTrigger className="w-full" size="sm">
                          <SelectValue placeholder="Select field..." />
                        </SelectTrigger>
                        <SelectContent>
                          {availableFields
                            .filter(
                              (f) =>
                                f.type === 'enum' ||
                                f.type === 'object' ||
                                f.key === 'state'
                            )
                            .map((field) => (
                              <SelectItem key={field.key} value={field.key}>
                                {field.label}
                              </SelectItem>
                            ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Enum filter UI using generic component */}
                    {filter.column && isEnumField && (
                      <div className="space-y-1">
                        <label className="text-xs font-medium">Values</label>
                        <div className="rounded-md border p-2">
                          <EnumFilterField
                            availableValues={getFieldOptions(selectedField)}
                            selectedValues={filter.values}
                            onChange={(values) =>
                              handleFilterValuesChange(index, values)
                            }
                            maxHeight="max-h-24"
                          />
                        </div>
                      </div>
                    )}

                    {/* Object filter UI using generic component */}
                    {filter.column && isObjectField && (
                      <div className="space-y-1">
                        <label className="text-xs font-medium">
                          Select Objects
                        </label>
                        <ObjectFilterField
                          objectType={
                            (selectedField?.object_type as ObjectTypes) ||
                            ObjectTypes.roster
                          }
                          selectedIds={filter.values}
                          onChange={(values) =>
                            handleFilterValuesChange(index, values)
                          }
                          placeholder={`Search ${selectedField?.label || 'objects'}...`}
                        />
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
