import { createTypedForm } from '@/components/forms/base';
import {
  SocialMediaPlatforms as SocialMediaPlatformsEnum,
  DeliverableType,
} from '@/openapi/ariveAPI.schemas';
import { useListObjectsSuspense } from '@/openapi/objects/objects';
import type { DeliverableCreateSchema } from '@/openapi/ariveAPI.schemas';

const {
  FormModal,
  FormString,
  FormText,
  FormSelect,
  FormCustom,
  FormDatetime,
} = createTypedForm<DeliverableCreateSchema>();

interface CreateDeliverableFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: DeliverableCreateSchema) => void;
  isSubmitting: boolean;
  actionLabel: string;
}

/**
 * Form for creating a new deliverable
 */
export function CreateDeliverableForm({
  isOpen,
  onClose,
  onSubmit,
  isSubmitting,
  actionLabel,
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

  const deliverableTypeOptions = [
    {
      value: DeliverableType.instagram_feed_post,
      label: 'Instagram Feed Post',
    },
    {
      value: DeliverableType.instagram_story_frame,
      label: 'Instagram Story Frame',
    },
    { value: DeliverableType.instagram_reel, label: 'Instagram Reel' },
    {
      value: DeliverableType.instagram_carousel,
      label: 'Instagram Carousel',
    },
    { value: DeliverableType.tiktok_video, label: 'TikTok Video' },
    { value: DeliverableType.tiktok_photo_post, label: 'TikTok Photo Post' },
    { value: DeliverableType.youtube_video, label: 'YouTube Video' },
    { value: DeliverableType.youtube_short, label: 'YouTube Short' },
    {
      value: DeliverableType.youtube_community_post,
      label: 'YouTube Community Post',
    },
    { value: DeliverableType.facebook_post, label: 'Facebook Post' },
    { value: DeliverableType.facebook_story, label: 'Facebook Story' },
    { value: DeliverableType.facebook_reel, label: 'Facebook Reel' },
    { value: DeliverableType.blog_post, label: 'Blog Post' },
    { value: DeliverableType.podcast_episode, label: 'Podcast Episode' },
    { value: DeliverableType.email_newsletter, label: 'Email Newsletter' },
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
    <FormModal
      isOpen={isOpen}
      onClose={onClose}
      title={actionLabel}
      subTitle="Fill out the form below to create a new deliverable."
      onSubmit={handleFormSubmit}
      isSubmitting={isSubmitting}
      submitText="Create Deliverable"
    >
      {/* Basic Information */}
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

      <FormSelect
        name="deliverable_type"
        label="Deliverable Type"
        placeholder="Select type (optional)"
        options={deliverableTypeOptions}
      />

      <FormCustom name="count">
        {({ value, onChange }) => (
          <div>
            <label className="mb-2 block text-sm font-medium">Count</label>
            <input
              type="number"
              value={value as number | undefined}
              onChange={(e) =>
                onChange(e.target.value ? parseInt(e.target.value) : undefined)
              }
              placeholder="1"
              min="1"
              className="border-input bg-background ring-offset-background placeholder:text-muted-foreground focus-visible:ring-ring flex h-10 w-full rounded-md border px-3 py-2 text-sm file:border-0 file:bg-transparent file:text-sm file:font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            />
          </div>
        )}
      </FormCustom>

      <FormText
        name="content"
        label="Content"
        placeholder="Post content..."
        rows={4}
      />

      {/* Posting Dates */}
      <div className="space-y-4 rounded-lg border p-4">
        <h3 className="text-sm font-medium">Posting Window</h3>
        <FormDatetime
          name="posting_date"
          label="Posting Date"
          placeholder="Posting date"
          required="Posting date is required"
        />
        <FormDatetime
          name="posting_start_date"
          label="Posting Start Date"
          placeholder="Start date (optional)"
        />
        <FormDatetime
          name="posting_end_date"
          label="Posting End Date"
          placeholder="End date (optional)"
        />
      </div>

      {/* Caption Requirements */}
      <div className="space-y-4 rounded-lg border p-4">
        <h3 className="text-sm font-medium">Caption Requirements</h3>
        <FormCustom name="handles">
          {({ value, onChange }) => (
            <div>
              <label className="mb-2 block text-sm font-medium">Handles</label>
              <input
                type="text"
                value={
                  Array.isArray(value) ? (value as string[]).join(', ') : ''
                }
                onChange={(e) =>
                  onChange(
                    e.target.value
                      ? e.target.value.split(',').map((s) => s.trim())
                      : []
                  )
                }
                placeholder="@brand, @creator (comma separated)"
                className="border-input bg-background ring-offset-background placeholder:text-muted-foreground focus-visible:ring-ring flex h-10 w-full rounded-md border px-3 py-2 text-sm file:border-0 file:bg-transparent file:text-sm file:font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              />
              <p className="text-muted-foreground mt-1 text-xs">
                Separate multiple handles with commas
              </p>
            </div>
          )}
        </FormCustom>
        <FormCustom name="hashtags">
          {({ value, onChange }) => (
            <div>
              <label className="mb-2 block text-sm font-medium">Hashtags</label>
              <input
                type="text"
                value={
                  Array.isArray(value) ? (value as string[]).join(', ') : ''
                }
                onChange={(e) =>
                  onChange(
                    e.target.value
                      ? e.target.value.split(',').map((s) => s.trim())
                      : []
                  )
                }
                placeholder="#brand, #campaign (comma separated)"
                className="border-input bg-background ring-offset-background placeholder:text-muted-foreground focus-visible:ring-ring flex h-10 w-full rounded-md border px-3 py-2 text-sm file:border-0 file:bg-transparent file:text-sm file:font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              />
              <p className="text-muted-foreground mt-1 text-xs">
                Separate multiple hashtags with commas
              </p>
            </div>
          )}
        </FormCustom>
        <FormCustom name="disclosures">
          {({ value, onChange }) => (
            <div>
              <label className="mb-2 block text-sm font-medium">
                Disclosures
              </label>
              <input
                type="text"
                value={
                  Array.isArray(value) ? (value as string[]).join(', ') : ''
                }
                onChange={(e) =>
                  onChange(
                    e.target.value
                      ? e.target.value.split(',').map((s) => s.trim())
                      : []
                  )
                }
                placeholder="#ad, #sponsored (comma separated)"
                className="border-input bg-background ring-offset-background placeholder:text-muted-foreground focus-visible:ring-ring flex h-10 w-full rounded-md border px-3 py-2 text-sm file:border-0 file:bg-transparent file:text-sm file:font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              />
              <p className="text-muted-foreground mt-1 text-xs">
                Separate multiple disclosures with commas
              </p>
            </div>
          )}
        </FormCustom>
      </div>

      {/* Approval Settings */}
      <div className="space-y-4 rounded-lg border p-4">
        <h3 className="text-sm font-medium">Approval Settings</h3>
        <FormCustom name="approval_required">
          {({ value, onChange }) => (
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="approval_required"
                checked={value as boolean}
                onChange={(e) => onChange(e.target.checked)}
                className="text-primary focus:ring-primary h-4 w-4 rounded border-gray-300 focus:ring-2"
              />
              <label
                htmlFor="approval_required"
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                Approval Required
              </label>
            </div>
          )}
        </FormCustom>
        <FormCustom name="approval_rounds">
          {({ value, onChange }) => (
            <div>
              <label className="mb-2 block text-sm font-medium">
                Approval Rounds
              </label>
              <input
                type="number"
                value={value as number | undefined}
                onChange={(e) =>
                  onChange(
                    e.target.value ? parseInt(e.target.value) : undefined
                  )
                }
                placeholder="1"
                min="1"
                className="border-input bg-background ring-offset-background placeholder:text-muted-foreground focus-visible:ring-ring flex h-10 w-full rounded-md border px-3 py-2 text-sm file:border-0 file:bg-transparent file:text-sm file:font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              />
            </div>
          )}
        </FormCustom>
      </div>

      <FormSelect
        name="campaign_id"
        label="Campaign"
        placeholder="Select campaign (optional)"
        options={campaignOptions}
      />
    </FormModal>
  );
}
