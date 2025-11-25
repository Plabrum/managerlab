'use client';

import { createTypedForm } from '@/components/forms/base';
import type {
  WidgetSchema,
  EditWidgetSchema,
} from '@/openapi/ariveAPI.schemas';
import {
  ObjectTypes,
  TimeRange,
  AggregationType,
} from '@/openapi/ariveAPI.schemas';
import { getAllWidgetTypes, widgetRegistry } from '@/lib/widgets/registry';

const { FormModal, FormString, FormSelect, FormCustom } =
  createTypedForm<EditWidgetSchema>();

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

interface UpdateWidgetFormProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  widget?: WidgetSchema;
  onSubmit: (data: EditWidgetSchema) => void;
  isSubmitting: boolean;
  actionLabel: string;
}

/**
 * Form for updating an existing widget
 */
export function UpdateWidgetForm({
  isOpen,
  onOpenChange,
  widget,
  onSubmit,
  isSubmitting,
  actionLabel,
}: UpdateWidgetFormProps) {
  const handleClose = () => onOpenChange(false);
  const widgetTypes = getAllWidgetTypes();
  const typeOptions = widgetTypes.map((type) => ({
    value: type,
    label: widgetRegistry[type].metadata.name,
  }));

  const defaultValues: Partial<EditWidgetSchema> = widget
    ? {
        type: widget.type,
        title: widget.title,
        description: widget.description ?? '',
        query: widget.query,
      }
    : {};

  return (
    <FormModal
      isOpen={isOpen}
      onClose={handleClose}
      title={actionLabel}
      onSubmit={onSubmit}
      defaultValues={defaultValues}
      isSubmitting={isSubmitting}
      submitText="Edit Widget"
    >
      <FormSelect name="type" label="Widget Type" options={typeOptions} />
      <FormString name="title" label="Title" placeholder="Widget title" />
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
    </FormModal>
  );
}
