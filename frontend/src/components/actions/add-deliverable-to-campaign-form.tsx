import { createTypedForm } from '@/components/forms/base';
import type { AddDeliverableToCampaignSchema } from '@/openapi/ariveAPI.schemas';
import { SocialMediaPlatforms as SocialMediaPlatformsEnum } from '@/openapi/ariveAPI.schemas';

const { FormModal, FormString, FormSelect, FormDatetime } =
  createTypedForm<AddDeliverableToCampaignSchema>();

interface AddDeliverableToCampaignFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: AddDeliverableToCampaignSchema) => void;
  isSubmitting: boolean;
  actionLabel: string;
}

/**
 * Minimal form for adding a deliverable to a campaign
 * Only includes required fields: title, platforms, posting_date
 */
export function AddDeliverableToCampaignForm({
  isOpen,
  onClose,
  onSubmit,
  isSubmitting,
  actionLabel,
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
    <FormModal
      isOpen={isOpen}
      onClose={onClose}
      title={actionLabel}
      subTitle="Add a deliverable to this campaign."
      onSubmit={handleFormSubmit}
      isSubmitting={isSubmitting}
      submitText="Add Deliverable"
    >
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
    </FormModal>
  );
}
