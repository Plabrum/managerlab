'use client';

import { createTypedForm } from '@/components/forms/base';
import type { CampaignUpdateSchema } from '@/openapi/managerLab.schemas';
import {
  CompensationStructure,
  CounterpartyType,
  OwnershipMode,
} from '@/openapi/managerLab.schemas';
import { ObjectSearchCombobox } from '@/components/forms/object-search-combobox';

const {
  FormModal,
  FormString,
  FormText,
  FormSelect,
  FormCustom,
  FormDatetime,
} = createTypedForm<CampaignUpdateSchema>();

interface UpdateCampaignFormProps {
  isOpen: boolean;
  onClose: () => void;
  defaultValues?: Partial<CampaignUpdateSchema>;
  onSubmit: (data: CampaignUpdateSchema) => void;
  isSubmitting: boolean;
  actionLabel: string;
}

/**
 * Form for updating an existing campaign
 */
export function UpdateCampaignForm({
  isOpen,
  onClose,
  defaultValues,
  onSubmit,
  isSubmitting,
  actionLabel,
}: UpdateCampaignFormProps) {
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
    <FormModal
      isOpen={isOpen}
      onClose={onClose}
      title={actionLabel}
      subTitle="Update the campaign information below."
      onSubmit={onSubmit}
      defaultValues={defaultValues}
      isSubmitting={isSubmitting}
      submitText="Update Campaign"
    >
      {/* Basic Information */}
      <FormString
        name="name"
        label="Campaign Name"
        placeholder="Campaign name"
        autoFocus
      />

      <FormCustom name="brand_id">
        {({ value, onChange }) => (
          <ObjectSearchCombobox
            objectType="brands"
            value={value ? String(value) : null}
            onValueChange={(id) => onChange(id ? Number(id) : null)}
            label="Brand"
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
                  onChange(e.target.value ? parseFloat(e.target.value) : null)
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
                  onChange(e.target.value ? parseInt(e.target.value) : null)
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
        <FormCustom name="usage_paid_media_option">
          {({ value, onChange }) => (
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="usage_paid_media_option"
                checked={value as boolean | undefined}
                onChange={(e) => onChange(e.target.checked ? true : null)}
                className="h-4 w-4 rounded border-gray-300"
              />
              <label
                htmlFor="usage_paid_media_option"
                className="text-sm font-medium"
              >
                Paid Media Option
              </label>
            </div>
          )}
        </FormCustom>
        <FormSelect
          name="ownership_mode"
          label="Content Ownership"
          placeholder="Select ownership mode (optional)"
          options={ownershipModeOptions}
        />
      </div>

      {/* Exclusivity */}
      <div className="space-y-4 rounded-lg border p-4">
        <h3 className="text-sm font-medium">Exclusivity</h3>
        <FormString
          name="exclusivity_category"
          label="Exclusivity Category"
          placeholder="e.g., Beauty, Fashion"
        />
        <FormCustom name="exclusivity_days_before">
          {({ value, onChange }) => (
            <div>
              <label className="mb-2 block text-sm font-medium">
                Days Before Campaign
              </label>
              <input
                type="number"
                value={value as number | undefined}
                onChange={(e) =>
                  onChange(e.target.value ? parseInt(e.target.value) : null)
                }
                placeholder="0"
                min="0"
                className="border-input bg-background ring-offset-background placeholder:text-muted-foreground focus-visible:ring-ring flex h-10 w-full rounded-md border px-3 py-2 text-sm file:border-0 file:bg-transparent file:text-sm file:font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              />
            </div>
          )}
        </FormCustom>
        <FormCustom name="exclusivity_days_after">
          {({ value, onChange }) => (
            <div>
              <label className="mb-2 block text-sm font-medium">
                Days After Campaign
              </label>
              <input
                type="number"
                value={value as number | undefined}
                onChange={(e) =>
                  onChange(e.target.value ? parseInt(e.target.value) : null)
                }
                placeholder="0"
                min="0"
                className="border-input bg-background ring-offset-background placeholder:text-muted-foreground focus-visible:ring-ring flex h-10 w-full rounded-md border px-3 py-2 text-sm file:border-0 file:bg-transparent file:text-sm file:font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              />
            </div>
          )}
        </FormCustom>
      </div>

      {/* Approval Process */}
      <div className="space-y-4 rounded-lg border p-4">
        <h3 className="text-sm font-medium">Approval Process</h3>
        <FormCustom name="approval_rounds">
          {({ value, onChange }) => (
            <div>
              <label className="mb-2 block text-sm font-medium">
                Number of Approval Rounds
              </label>
              <input
                type="number"
                value={value as number | undefined}
                onChange={(e) =>
                  onChange(e.target.value ? parseInt(e.target.value) : null)
                }
                placeholder="1"
                min="1"
                className="border-input bg-background ring-offset-background placeholder:text-muted-foreground focus-visible:ring-ring flex h-10 w-full rounded-md border px-3 py-2 text-sm file:border-0 file:bg-transparent file:text-sm file:font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              />
            </div>
          )}
        </FormCustom>
        <FormCustom name="approval_sla_hours">
          {({ value, onChange }) => (
            <div>
              <label className="mb-2 block text-sm font-medium">
                Approval SLA (Hours)
              </label>
              <input
                type="number"
                value={value as number | undefined}
                onChange={(e) =>
                  onChange(e.target.value ? parseInt(e.target.value) : null)
                }
                placeholder="24"
                min="1"
                className="border-input bg-background ring-offset-background placeholder:text-muted-foreground focus-visible:ring-ring flex h-10 w-full rounded-md border px-3 py-2 text-sm file:border-0 file:bg-transparent file:text-sm file:font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              />
            </div>
          )}
        </FormCustom>
      </div>
    </FormModal>
  );
}
