'use client';

import { useEffect } from 'react';
import { useFormContext, useWatch } from 'react-hook-form';
import { createTypedForm } from '@/components/forms/base';
import {
  ObjectTypes,
  TimeRange,
  AggregationType,
  type CreateWidgetSchema,
  type EditWidgetSchema,
  type WidgetQuerySchema,
} from '@/openapi/ariveAPI.schemas';
import { getAllWidgetTypes, widgetRegistry } from '@/lib/widgets/registry';
import type { WidgetType } from '@/lib/widgets/types';

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

const COMMON_FIELD_OPTIONS = [
  { value: 'created_at', label: 'Created Date' },
  { value: 'updated_at', label: 'Updated Date' },
  { value: 'status', label: 'Status' },
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
            const updateField = (
              field: keyof WidgetQuerySchema,
              val: string
            ) => {
              onChange({ ...query, [field]: val } as WidgetQuerySchema);
            };

            return (
              <div className="space-y-4">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Object Type</label>
                  <select
                    value={query.object_type || ''}
                    onChange={(e) => updateField('object_type', e.target.value)}
                    className="bg-background w-full rounded-md border px-3 py-2 text-sm"
                  >
                    <option value="">Select object type...</option>
                    {WIDGET_OBJECT_TYPES.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Field</label>
                  <select
                    value={query.field || ''}
                    onChange={(e) => updateField('field', e.target.value)}
                    className="bg-background w-full rounded-md border px-3 py-2 text-sm"
                  >
                    <option value="">Select field...</option>
                    {COMMON_FIELD_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Time Range</label>
                  <select
                    value={query.time_range || ''}
                    onChange={(e) => updateField('time_range', e.target.value)}
                    className="bg-background w-full rounded-md border px-3 py-2 text-sm"
                  >
                    <option value="">Select time range...</option>
                    {TIME_RANGE_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Aggregation</label>
                  <select
                    value={query.aggregation || ''}
                    onChange={(e) => updateField('aggregation', e.target.value)}
                    className="bg-background w-full rounded-md border px-3 py-2 text-sm"
                  >
                    <option value="">Select aggregation...</option>
                    {AGGREGATION_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            );
          }}
        </FormCustom>
      </div>
    </>
  );
}
