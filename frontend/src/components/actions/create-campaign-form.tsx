'use client';

import { Button } from '@/components/ui/button';
import { createTypedForm } from '@/components/forms/base';
import type { CampaignCreateSchema } from '@/openapi/managerLab.schemas';
import {
  CompensationStructure,
  CounterpartyType,
  OwnershipMode,
} from '@/openapi/managerLab.schemas';
import { ObjectSearchCombobox } from '@/components/forms/object-search-combobox';

const { Form, FormString, FormText, FormSelect, FormCustom, FormDatetime } =
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

  const counterpartyTypeOptions = [
    { value: CounterpartyType.agency, label: 'Agency' },
    { value: CounterpartyType.brand, label: 'Brand' },
  ];

  const ownershipModeOptions = [
    { value: OwnershipMode.brand_owned, label: 'Brand Owned' },
    { value: OwnershipMode.creator_owned, label: 'Creator Owned' },
    { value: OwnershipMode.shared, label: 'Shared' },
  ];

  return (
    <Form onSubmit={onSubmit}>
      {/* Basic Information */}
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

      {/* Counterparty Information */}
      <div className="space-y-4 rounded-lg border p-4">
        <h3 className="text-sm font-medium">Counterparty Information</h3>
        <FormSelect
          name="counterparty_type"
          label="Counterparty Type"
          placeholder="Select type (optional)"
          options={counterpartyTypeOptions}
        />
        <FormString
          name="counterparty_name"
          label="Counterparty Name"
          placeholder="Agency or brand name"
        />
        <FormString
          name="counterparty_email"
          label="Counterparty Email"
          placeholder="contact@example.com"
        />
      </div>

      {/* Compensation */}
      <div className="space-y-4 rounded-lg border p-4">
        <h3 className="text-sm font-medium">Compensation</h3>
        <FormSelect
          name="compensation_structure"
          label="Compensation Structure"
          placeholder="Select compensation structure (optional)"
          options={compensationOptions}
        />
        <FormCustom name="compensation_total_usd">
          {({ value, onChange }) => (
            <div>
              <label className="mb-2 block text-sm font-medium">
                Total Compensation (USD)
              </label>
              <input
                type="number"
                value={value as number | undefined}
                onChange={(e) =>
                  onChange(
                    e.target.value ? parseFloat(e.target.value) : undefined
                  )
                }
                placeholder="0.00"
                step="0.01"
                min="0"
                className="border-input bg-background ring-offset-background placeholder:text-muted-foreground focus-visible:ring-ring flex h-10 w-full rounded-md border px-3 py-2 text-sm file:border-0 file:bg-transparent file:text-sm file:font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              />
            </div>
          )}
        </FormCustom>
        <FormCustom name="payment_terms_days">
          {({ value, onChange }) => (
            <div>
              <label className="mb-2 block text-sm font-medium">
                Payment Terms (Days)
              </label>
              <input
                type="number"
                value={value as number | undefined}
                onChange={(e) =>
                  onChange(
                    e.target.value ? parseInt(e.target.value) : undefined
                  )
                }
                placeholder="30"
                min="0"
                className="border-input bg-background ring-offset-background placeholder:text-muted-foreground focus-visible:ring-ring flex h-10 w-full rounded-md border px-3 py-2 text-sm file:border-0 file:bg-transparent file:text-sm file:font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              />
            </div>
          )}
        </FormCustom>
      </div>

      {/* Flight Dates */}
      <div className="space-y-4 rounded-lg border p-4">
        <h3 className="text-sm font-medium">Flight Window</h3>
        <FormDatetime
          name="flight_start_date"
          label="Flight Start Date"
          placeholder="Start date"
        />
        <FormDatetime
          name="flight_end_date"
          label="Flight End Date"
          placeholder="End date"
        />
      </div>

      {/* Usage Rights */}
      <div className="space-y-4 rounded-lg border p-4">
        <h3 className="text-sm font-medium">Usage Rights</h3>
        <FormString
          name="ftc_string"
          label="FTC Disclosure"
          placeholder="e.g., #ad, #sponsored"
        />
        <FormString
          name="usage_duration"
          label="Usage Duration"
          placeholder="e.g., 1 year, perpetual"
        />
        <FormString
          name="usage_territory"
          label="Usage Territory"
          placeholder="e.g., Worldwide, USA only"
        />
        <FormSelect
          name="ownership_mode"
          label="Content Ownership"
          placeholder="Select ownership mode (optional)"
          options={ownershipModeOptions}
        />
      </div>

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
