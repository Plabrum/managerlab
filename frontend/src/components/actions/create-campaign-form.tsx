'use client';

import { Button } from '@/components/ui/button';
import { createTypedForm } from '@/components/forms/base';
import type { CampaignCreateSchema } from '@/openapi/managerLab.schemas';
import { CompensationStructure } from '@/openapi/managerLab.schemas';
import { useListObjectsSuspense } from '@/openapi/objects/objects';

const { Form, FormString, FormText, FormSelect } =
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
  // Fetch brands for the dropdown
  const { data: brandsData } = useListObjectsSuspense('brands', {
    offset: 0,
    limit: 100,
    sorts: [],
    filters: [],
  });

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

  const brandOptions =
    brandsData?.objects.map((brand) => ({
      value: brand.id.toString(),
      label: brand.title,
    })) || [];

  const handleFormSubmit = (data: CampaignCreateSchema) => {
    // Convert brand_id from string to number
    const submissionData: CampaignCreateSchema = {
      ...data,
      brand_id: parseInt(data.brand_id as unknown as string, 10),
    };
    onSubmit(submissionData);
  };

  return (
    <Form onSubmit={handleFormSubmit}>
      <FormString
        name="name"
        label="Campaign Name"
        placeholder="Campaign name"
        required="Campaign name is required"
        autoFocus
      />

      <FormSelect
        name="brand_id"
        label="Brand"
        placeholder="Select brand"
        options={brandOptions}
        required="Brand is required"
      />

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
