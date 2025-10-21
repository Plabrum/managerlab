'use client';

import { Button } from '@/components/ui/button';
import { createTypedForm } from '@/components/forms/base';
import type { DeliverableCreateSchema } from '@/openapi/managerLab.schemas';
import { SocialMediaPlatforms as SocialMediaPlatformsEnum } from '@/openapi/managerLab.schemas';
import { useListObjectsSuspense } from '@/openapi/objects/objects';

const { Form, FormString, FormText, FormSelect, FormDatetime } =
  createTypedForm<DeliverableCreateSchema>();

interface CreateDeliverableFormProps {
  onSubmit: (data: DeliverableCreateSchema) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

/**
 * Form for creating a new deliverable
 */
export function CreateDeliverableForm({
  onSubmit,
  onCancel,
  isSubmitting,
}: CreateDeliverableFormProps) {
  // Fetch campaigns for the dropdown
  const { data: campaignsData } = useListObjectsSuspense('campaigns', {
    offset: 0,
    limit: 100,
    sorts: [],
    filters: [],
  });

  const platformOptions = [
    { value: SocialMediaPlatformsEnum.instagram, label: 'Instagram' },
    { value: SocialMediaPlatformsEnum.facebook, label: 'Facebook' },
    { value: SocialMediaPlatformsEnum.tiktok, label: 'TikTok' },
    { value: SocialMediaPlatformsEnum.youtube, label: 'YouTube' },
  ];

  const campaignOptions =
    campaignsData?.objects.map((campaign) => ({
      value: campaign.id.toString(),
      label: campaign.title,
    })) || [];

  const handleFormSubmit = (data: DeliverableCreateSchema) => {
    // Convert datetime-local string to ISO format
    const submissionData: DeliverableCreateSchema = {
      ...data,
      posting_date: new Date(data.posting_date).toISOString(),
      // Convert campaign_id from string to number if provided
      campaign_id: data.campaign_id
        ? parseInt(data.campaign_id as unknown as string, 10)
        : undefined,
    };
    onSubmit(submissionData);
  };

  return (
    <Form onSubmit={handleFormSubmit}>
      <FormString
        name="title"
        label="Title"
        placeholder="Deliverable title"
        required="Title is required"
      />

      <FormSelect
        name="platforms"
        label="Platform"
        placeholder="Select platform"
        options={platformOptions}
        required="Platform is required"
      />

      <FormDatetime
        name="posting_date"
        label="Posting Date"
        required="Posting date is required"
      />

      <FormText
        name="content"
        label="Content"
        placeholder="Deliverable content..."
        rows={4}
      />

      <FormSelect
        name="campaign_id"
        label="Campaign"
        placeholder="Select campaign (optional)"
        options={campaignOptions}
      />

      <div className="flex gap-3 pt-4">
        <Button type="submit" disabled={isSubmitting} className="flex-1">
          {isSubmitting ? 'Creating...' : 'Create Deliverable'}
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
