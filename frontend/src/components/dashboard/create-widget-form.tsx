'use client';

import { useEffect } from 'react';
import { useFormContext, useWatch } from 'react-hook-form';
import { createTypedForm } from '@/components/forms/base';
import {
  ObjectTypes,
  TimeRange,
  AggregationType,
  type CreateWidgetSchema,
} from '@/openapi/ariveAPI.schemas';
import { getAllWidgetTypes, widgetRegistry } from '@/lib/widgets/registry';
import type { WidgetType } from '@/lib/widgets/types';

const { FormSheet, FormString, FormSelect, FormCustom } =
  createTypedForm<CreateWidgetSchema>();

// Object types that make sense for dashboard widgets
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

// Common fields available for most object types
const COMMON_FIELD_OPTIONS = [
  { value: 'created_at', label: 'Created Date' },
  { value: 'updated_at', label: 'Updated Date' },
  { value: 'status', label: 'Status' },
] as const;

interface CreateWidgetFormProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  dashboardId: string;
  prefilledType?: string;
  onSubmit: (data: CreateWidgetSchema) => void;
  isSubmitting: boolean;
  actionLabel: string;
}

/**
 * Inner component that handles query field synchronization
 */
function QueryFieldsSync({ prefilledType }: { prefilledType?: string }) {
  const { setValue, getValues } = useFormContext<CreateWidgetSchema>();
  const widgetType = useWatch<CreateWidgetSchema, 'type'>({ name: 'type' });

  // When widget type changes, update the query with defaults from registry
  useEffect(() => {
    if (widgetType) {
      const entry = widgetRegistry[widgetType as WidgetType];
      if (entry?.defaults?.query) {
        const currentQuery = getValues('query') || {};
        // Only set defaults if query is empty or this is the initial type selection
        if (
          Object.keys(currentQuery).length === 0 ||
          widgetType !== prefilledType
        ) {
          setValue('query', {
            object_type: entry.defaults.query.object_type || ObjectTypes.brands,
            field: entry.defaults.query.field || 'created_at',
            time_range:
              entry.defaults.query.time_range || TimeRange.last_30_days,
            aggregation:
              entry.defaults.query.aggregation || AggregationType.count_,
          });
        }
      }
    }
  }, [widgetType, setValue, getValues, prefilledType]);

  return null;
}

/**
 * Form for creating a new widget
 */
export function CreateWidgetForm({
  isOpen,
  onOpenChange,
  dashboardId,
  prefilledType,
  onSubmit,
  isSubmitting,
  actionLabel,
}: CreateWidgetFormProps) {
  const widgetTypes = getAllWidgetTypes();
  const typeOptions = widgetTypes.map((type) => ({
    value: type,
    label: widgetRegistry[type].metadata.name,
  }));

  // Get default query from registry based on prefilled type
  const defaultQuery = prefilledType
    ? widgetRegistry[prefilledType as WidgetType]?.defaults?.query
    : widgetRegistry[widgetTypes[0]]?.defaults?.query;

  const defaultValues: Partial<CreateWidgetSchema> = {
    dashboard_id: dashboardId,
    type: prefilledType || widgetTypes[0],
    title: '',
    description: '',
    query: {
      object_type: defaultQuery?.object_type || ObjectTypes.brands,
      field: defaultQuery?.field || 'created_at',
      time_range: defaultQuery?.time_range || TimeRange.last_30_days,
      aggregation: defaultQuery?.aggregation || AggregationType.count_,
    },
    position_x: 0,
    position_y: 0,
    size_w: 1,
    size_h: 1,
  };

  return (
    <FormSheet
      isOpen={isOpen}
      onOpenChange={onOpenChange}
      title={actionLabel}
      subTitle="Add a new widget to your dashboard"
      onSubmit={onSubmit}
      defaultValues={defaultValues}
      isSubmitting={isSubmitting}
      submitText="Add Widget"
    >
      <QueryFieldsSync prefilledType={prefilledType} />

      <FormSelect
        name="type"
        label="Widget Type"
        options={typeOptions}
        required
      />
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
            const query = (value || {}) as Record<string, string>;
            const updateField = (field: string, val: string) => {
              onChange({ ...query, [field]: val });
            };

            return (
              <div className="space-y-4">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Object Type</label>
                  <select
                    value={query.object_type || ObjectTypes.brands}
                    onChange={(e) => updateField('object_type', e.target.value)}
                    className="bg-background w-full rounded-md border px-3 py-2 text-sm"
                  >
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
                    value={query.field || 'created_at'}
                    onChange={(e) => updateField('field', e.target.value)}
                    className="bg-background w-full rounded-md border px-3 py-2 text-sm"
                  >
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
                    value={query.time_range || TimeRange.last_30_days}
                    onChange={(e) => updateField('time_range', e.target.value)}
                    className="bg-background w-full rounded-md border px-3 py-2 text-sm"
                  >
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
                    value={query.aggregation || AggregationType.count_}
                    onChange={(e) => updateField('aggregation', e.target.value)}
                    className="bg-background w-full rounded-md border px-3 py-2 text-sm"
                  >
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
    </FormSheet>
  );
}
