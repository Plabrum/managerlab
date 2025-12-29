import { useEffect, useState } from 'react';
import { useFormContext, useWatch } from 'react-hook-form';
import { KanbanWidgetFormFields } from './kanban-widget-form';
import { createTypedForm } from '@/components/forms/base';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { getAllWidgetTypes, widgetRegistry } from '@/lib/widgets/registry';
import type { WidgetType } from '@/lib/widgets/types';
import {
  ObjectTypes,
  TimeRange,
  AggregationType,
  type CreateWidgetSchema,
  type EditWidgetSchema,
  type WidgetQuerySchema,
  type ColumnDefinitionSchema,
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

const AGGREGATION_OPTIONS = [
  { value: AggregationType.count_, label: 'Count' },
  { value: AggregationType.sum, label: 'Sum' },
  { value: AggregationType.avg, label: 'Average' },
  { value: AggregationType.max, label: 'Maximum' },
  { value: AggregationType.min, label: 'Minimum' },
] as const;

/**
 * Inner component that handles size synchronization when widget type changes
 */
function WidgetSizeSync({ prefilledType }: { prefilledType?: string }) {
  const { setValue } = useFormContext();
  const widgetType = useWatch({ name: 'type' });

  // When widget type changes, update the size with constraints from registry
  useEffect(() => {
    if (widgetType && widgetType !== prefilledType) {
      const entry = widgetRegistry[widgetType as WidgetType];
      if (entry?.sizeConstraints) {
        setValue('size_w', entry.sizeConstraints.defaultW);
        setValue('size_h', entry.sizeConstraints.defaultH);
      }
    }
  }, [widgetType, setValue, prefilledType]);

  return null;
}

/**
 * Component that provides dynamic field options based on selected object type
 */
interface DynamicFieldSelectorProps {
  query: Partial<WidgetQuerySchema>;
  onChange: (query: WidgetQuerySchema) => void;
}

function DynamicFieldSelector({ query, onChange }: DynamicFieldSelectorProps) {
  const [availableFields, setAvailableFields] = useState<
    ColumnDefinitionSchema[]
  >([]);
  const [loadingFields, setLoadingFields] = useState(false);

  // Fetch fields when object type changes
  useEffect(() => {
    const fetchFields = async () => {
      if (!query.object_type) {
        setAvailableFields([]);
        return;
      }

      try {
        setLoadingFields(true);
        const response = await oObjectTypeSchemaGetObjectSchema(
          query.object_type as ObjectTypes
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

  const handleObjectTypeChange = (value: string) => {
    // Update both object_type and clear field in a single update
    onChange({ ...query, object_type: value, field: '' } as WidgetQuerySchema);
  };

  const updateField = (field: keyof WidgetQuerySchema, value: string) => {
    onChange({ ...query, [field]: value } as WidgetQuerySchema);
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
      </div>

      <div className="space-y-1.5">
        <label className="text-sm font-medium">Field</label>
        <Select
          value={query.field || undefined}
          onValueChange={(value) => updateField('field', value)}
          disabled={loadingFields || availableFields.length === 0}
        >
          <SelectTrigger className="w-full">
            <SelectValue
              placeholder={
                loadingFields
                  ? 'Loading fields...'
                  : availableFields.length === 0
                    ? 'Select object type first'
                    : 'Select field...'
              }
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
        {availableFields.length > 0 && (
          <p className="text-muted-foreground text-xs">
            Select the field you want to visualize
          </p>
        )}
      </div>

      <div className="space-y-1.5">
        <label className="text-sm font-medium">Time Range</label>
        <Select
          value={query.time_range || undefined}
          onValueChange={(value) => updateField('time_range', value)}
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
      </div>

      <div className="space-y-1.5">
        <label className="text-sm font-medium">Aggregation</label>
        <Select
          value={query.aggregation || undefined}
          onValueChange={(value) => updateField('aggregation', value)}
        >
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Select aggregation..." />
          </SelectTrigger>
          <SelectContent>
            {AGGREGATION_OPTIONS.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <p className="text-muted-foreground text-xs">
          How to aggregate the data (auto-detected if not specified)
        </p>
      </div>
    </div>
  );
}

/**
 * Shared form fields component
 */
interface WidgetFormFieldsProps {
  prefilledType?: string;
  showTypeField?: boolean;
}

export function WidgetFormFields({
  prefilledType,
  showTypeField = true,
}: WidgetFormFieldsProps) {
  const widgetTypes = getAllWidgetTypes();
  const typeOptions = widgetTypes.map((type) => ({
    value: type,
    label: widgetRegistry[type].metadata.name,
  }));

  const { FormString, FormSelect, FormCustom } = createTypedForm<
    CreateWidgetSchema | EditWidgetSchema
  >();

  // Watch the current widget type to conditionally render form fields
  const { watch } = useFormContext();
  const currentType = watch('type') || prefilledType;
  const isKanbanWidget = currentType === 'kanban';

  return (
    <>
      <WidgetSizeSync prefilledType={prefilledType} />

      {showTypeField && (
        <FormSelect
          name="type"
          label="Widget Type"
          options={typeOptions}
          required
        />
      )}

      <FormString
        name="title"
        label="Title"
        placeholder="Widget title"
        required
      />

      <FormString
        name="description"
        label="Description"
        placeholder="Optional description"
      />

      {/* Data Source Configuration */}
      <div className="space-y-4 rounded-lg border p-4">
        <h3 className="text-sm font-medium">Data Source</h3>

        <FormCustom name="query">
          {({ value, onChange }) => {
            const query = (value || {}) as Partial<WidgetQuerySchema>;

            // Use kanban-specific form for kanban widgets
            if (isKanbanWidget) {
              return (
                <KanbanWidgetFormFields
                  query={query}
                  onChange={onChange as (query: WidgetQuerySchema) => void}
                />
              );
            }

            // Default form for chart widgets
            return (
              <DynamicFieldSelector
                query={query}
                onChange={onChange as (query: WidgetQuerySchema) => void}
              />
            );
          }}
        </FormCustom>
      </div>
    </>
  );
}
