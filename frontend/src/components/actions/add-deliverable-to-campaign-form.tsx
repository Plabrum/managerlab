'use client';

import { Button } from '@/components/ui/button';
import { createTypedForm } from '@/components/forms/base';
import type { AddDeliverableToCampaignSchema } from '@/openapi/managerLab.schemas';
import { SocialMediaPlatforms as SocialMediaPlatformsEnum } from '@/openapi/managerLab.schemas';

const { Form, FormString, FormSelect, FormDatetime } =
  createTypedForm<AddDeliverableToCampaignSchema>();

interface AddDeliverableToCampaignFormProps {
  onSubmit: (data: AddDeliverableToCampaignSchema) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

/**
 * Minimal form for adding a deliverable to a campaign
 * Only includes required fields: title, platforms, posting_date
 */
export function AddDeliverableToCampaignForm({
  onSubmit,
  onCancel,
  isSubmitting,
}: AddDeliverableToCampaignFormProps) {
  const platformOptions = [
    { value: SocialMediaPlatformsEnum.instagram, label: 'Instagram' },
    { value: SocialMediaPlatformsEnum.facebook, label: 'Facebook' },
    { value: SocialMediaPlatformsEnum.tiktok, label: 'TikTok' },
    { value: SocialMediaPlatformsEnum.youtube, label: 'YouTube' },
  ];

  const handleFormSubmit = (data: AddDeliverableToCampaignSchema) => {
    // Convert datetime-local string to ISO format
    const submissionData: AddDeliverableToCampaignSchema = {
      ...data,
      posting_date: new Date(data.posting_date).toISOString(),
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
        autoFocus
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
        placeholder="Posting date"
        required="Posting date is required"
      />

      <div className="flex gap-3 pt-4">
        <Button type="submit" disabled={isSubmitting} className="flex-1">
          {isSubmitting ? 'Adding...' : 'Add Deliverable'}
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
