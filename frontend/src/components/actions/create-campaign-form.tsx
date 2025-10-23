'use client';

import { Button } from '@/components/ui/button';
import { createTypedForm } from '@/components/forms/base';
import type { CampaignCreateSchema } from '@/openapi/managerLab.schemas';
import { CompensationStructure } from '@/openapi/managerLab.schemas';
import { ObjectSearchCombobox } from '@/components/forms/object-search-combobox';

const { Form, FormString, FormText, FormSelect, FormCustom } =
  createTypedForm<CampaignCreateSchema>();

interface CreateCampaignFormProps {
  onSubmit: (data: CampaignCreateSchema) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

/**
 * Form for creating a new campaign
 */
export function CreateCampaignForm({
  onSubmit,
  onCancel,
  isSubmitting,
}: CreateCampaignFormProps) {
  const compensationOptions = [
    { value: CompensationStructure.flat_fee, label: 'Flat Fee' },
    {
      value: CompensationStructure.per_deliverable,
      label: 'Per Deliverable',
    },
    {
      value: CompensationStructure.performance_based,
      label: 'Performance Based',
    },
  ];

  return (
    <Form onSubmit={onSubmit}>
      <FormString
        name="name"
        label="Campaign Name"
        placeholder="Campaign name"
        required="Campaign name is required"
        autoFocus
      />

      <FormCustom name="brand_id">
        {({ value, onChange }) => (
          <ObjectSearchCombobox
            objectType="brands"
            value={(value as string) || null}
            onValueChange={(id) => onChange(id)}
            label="Brand"
            required
          />
        )}
      </FormCustom>

      <FormText
        name="description"
        label="Description"
        placeholder="Campaign description..."
        rows={4}
      />

      <FormSelect
        name="compensation_structure"
        label="Compensation Structure"
        placeholder="Select compensation structure (optional)"
        options={compensationOptions}
      />

      <div className="flex gap-3 pt-4">
        <Button type="submit" disabled={isSubmitting} className="flex-1">
          {isSubmitting ? 'Creating...' : 'Create Campaign'}
        </Button>
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          disabled={isSubmitting}
          className="flex-1"
        >
          Cancel
        </Button>
      </div>
    </Form>
  );
}
