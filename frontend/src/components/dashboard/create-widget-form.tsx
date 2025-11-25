'use client';

import { createTypedForm } from '@/components/forms/base';
import {
  ObjectTypes,
  TimeRange,
  AggregationType,
  type CreateWidgetSchema,
} from '@/openapi/ariveAPI.schemas';
import { widgetRegistry } from '@/lib/widgets/registry';
import type { WidgetType } from '@/lib/widgets/types';
import { WidgetFormFields } from './widget-form';

const { FormModal } = createTypedForm<CreateWidgetSchema>();

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
  const handleClose = () => onOpenChange(false);

  // Get default query from registry based on prefilled type
  const defaultQuery = prefilledType
    ? widgetRegistry[prefilledType as WidgetType]?.defaults?.query
    : undefined;

  const defaultValues: Partial<CreateWidgetSchema> = {
    dashboard_id: dashboardId,
    type: prefilledType,
    title: '',
    description: '',
    query: defaultQuery
      ? {
          object_type: defaultQuery.object_type || ObjectTypes.brands,
          field: defaultQuery.field || 'created_at',
          time_range: defaultQuery.time_range || TimeRange.last_30_days,
          aggregation: defaultQuery.aggregation || AggregationType.count_,
        }
      : undefined,
    position_x: 0,
    position_y: 0,
    size_w: 1,
    size_h: 1,
  };

  return (
    <FormModal
      isOpen={isOpen}
      onClose={handleClose}
      title={actionLabel}
      onSubmit={onSubmit}
      defaultValues={defaultValues}
      isSubmitting={isSubmitting}
      submitText="Add Widget"
    >
      <WidgetFormFields prefilledType={prefilledType} showTypeField={true} />
    </FormModal>
  );
}
