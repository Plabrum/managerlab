'use client';

import { createTypedForm } from '@/components/forms/base';
import type { CampaignCreateSchema } from '@/openapi/managerLab.schemas';
import {
  CompensationStructure,
  CounterpartyType,
  OwnershipMode,
} from '@/openapi/managerLab.schemas';
import { ObjectSearchCombobox } from '@/components/forms/object-search-combobox';
import { useState, useCallback } from 'react';
import { Dropzone, DropzoneEmptyState } from '@/components/ui/dropzone';
import { UploadIcon, FileText, X } from 'lucide-react';
import { useDocumentUpload } from '@/hooks/useDocumentUpload';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { CollapsibleFormSection } from '@/components/ui/collapsible-form-section';

const {
  FormModal,
  FormString,
  FormText,
  FormSelect,
  FormCustom,
  FormDatetime,
} = createTypedForm<CampaignCreateSchema>();

interface CreateCampaignFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CampaignCreateSchema) => void;
  isSubmitting: boolean;
  actionLabel: string;
}

/**
 * Form for creating a new campaign
 */
export function CreateCampaignForm({
  isOpen,
  onClose,
  onSubmit,
  isSubmitting,
  actionLabel,
}: CreateCampaignFormProps) {
  const [contractFile, setContractFile] = useState<File | null>(null);
  const { uploadFile, status: uploadStatus, progress } = useDocumentUpload();

  const handleFormSubmit = useCallback(
    async (data: CampaignCreateSchema) => {
      // If a contract file is selected, upload it first
      if (contractFile) {
        const result = await uploadFile(contractFile, {
          autoRegister: true,
        });

        if (result) {
          // Add the document ID to the form data
          data.contract_document_id = result.documentId;
        }
      }

      // Submit the form with the document ID (if uploaded)
      onSubmit(data);
    },
    [contractFile, uploadFile, onSubmit]
  );

  const handleFileRemove = useCallback(() => {
    setContractFile(null);
  }, []);

  const handleFileDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      setContractFile(file);
    }
  }, []);

  const isUploading =
    uploadStatus === 'uploading' || uploadStatus === 'registering';

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
      subTitle="Fill out the form below to create a new campaign."
      onSubmit={handleFormSubmit}
      isSubmitting={isSubmitting || isUploading}
      submitText={isUploading ? 'Uploading contract...' : 'Create Campaign'}
    >
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

      {/* Contract Upload (Optional) */}
      <div className="space-y-2">
        <label className="text-sm font-medium">Contract (Optional)</label>
        <p className="text-muted-foreground text-xs">
          Upload a contract document to attach to this campaign
        </p>
        {!contractFile ? (
          <Dropzone
            onDrop={handleFileDrop}
            accept={{
              'application/pdf': ['.pdf'],
              'application/msword': ['.doc'],
              'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                ['.docx'],
              'application/vnd.ms-excel': ['.xls'],
              'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                ['.xlsx'],
              'text/plain': ['.txt'],
              'text/markdown': ['.md'],
              'text/csv': ['.csv'],
            }}
            maxFiles={1}
            disabled={isUploading || isSubmitting}
          >
            <DropzoneEmptyState>
              <div className="flex flex-col items-center justify-center py-6">
                <div className="bg-muted text-muted-foreground flex size-10 items-center justify-center rounded-md">
                  <UploadIcon size={20} />
                </div>
                <p className="my-2 text-sm font-medium">
                  Drop contract file or click to browse
                </p>
                <p className="text-muted-foreground text-xs">
                  PDF, Word, Excel, or text files
                </p>
              </div>
            </DropzoneEmptyState>
          </Dropzone>
        ) : (
          <div className="rounded-lg border p-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <FileText className="text-muted-foreground h-8 w-8" />
                <div>
                  <p className="text-sm font-medium">{contractFile.name}</p>
                  <p className="text-muted-foreground text-xs">
                    {(contractFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>
              {!isUploading && !isSubmitting && (
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={handleFileRemove}
                >
                  <X className="h-4 w-4" />
                </Button>
              )}
            </div>
            {isUploading && (
              <div className="mt-3">
                <Progress value={progress} className="h-2" />
                <p className="text-muted-foreground mt-1 text-xs">
                  {uploadStatus === 'uploading'
                    ? 'Uploading...'
                    : 'Registering...'}
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Advanced Options - Collapsible Section */}
      <CollapsibleFormSection title="Additional options" defaultOpen={false}>
        <FormText
          name="description"
          label="Description"
          placeholder="Campaign description..."
          rows={4}
        />
        {/* Counterparty Information */}
        <div className="space-y-4 rounded-lg border p-4">
          <h4 className="text-sm font-medium">Counterparty Information</h4>
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
          <h4 className="text-sm font-medium">Compensation</h4>
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
          <h4 className="text-sm font-medium">Flight Window</h4>
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
          <h4 className="text-sm font-medium">Usage Rights</h4>
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
      </CollapsibleFormSection>
    </FormModal>
  );
}
