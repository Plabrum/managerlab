import { createTypedForm } from '@/components/forms/base';
import { DeliverableType } from '@/openapi/ariveAPI.schemas';
import type { DeliverableUpdateSchema } from '@/openapi/ariveAPI.schemas';

const {
  FormModal,
  FormString,
  FormText,
  FormSelect,
  FormCustom,
  FormDatetime,
} = createTypedForm<DeliverableUpdateSchema>();

interface UpdateDeliverableFormProps {
  isOpen: boolean;
  onClose: () => void;
  defaultValues?: Partial<DeliverableUpdateSchema>;
  onSubmit: (data: DeliverableUpdateSchema) => void;
  isSubmitting: boolean;
  actionLabel: string;
}

/**
 * Form for updating a deliverable
 */
export function UpdateDeliverableForm({
  isOpen,
  onClose,
  defaultValues,
  onSubmit,
  isSubmitting,
  actionLabel,
}: UpdateDeliverableFormProps) {
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

  return (
    <FormModal
      isOpen={isOpen}
      onClose={onClose}
      title={actionLabel}
      subTitle="Update the deliverable information below."
      onSubmit={onSubmit}
      defaultValues={defaultValues}
      isSubmitting={isSubmitting}
      submitText="Update Deliverable"
    >
      {/* Basic Information */}
      <FormString name="title" label="Title" placeholder="Deliverable title" />

      <FormSelect
        name="deliverable_type"
        label="Deliverable Type"
        placeholder="Select type (optional)"
        options={deliverableTypeOptions}
      />

      <FormCustom name="count">
        {({ value, onChange }) => (
          <div>
            <label
              htmlFor="update-deliverable-count"
              className="mb-2 block text-sm font-medium"
            >
              Count
            </label>
            <input
              id="update-deliverable-count"
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
              <label
                htmlFor="update-deliverable-handles"
                className="mb-2 block text-sm font-medium"
              >
                Handles
              </label>
              <input
                id="update-deliverable-handles"
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
              <label
                htmlFor="update-deliverable-hashtags"
                className="mb-2 block text-sm font-medium"
              >
                Hashtags
              </label>
              <input
                id="update-deliverable-hashtags"
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
              <label
                htmlFor="update-deliverable-disclosures"
                className="mb-2 block text-sm font-medium"
              >
                Disclosures
              </label>
              <input
                id="update-deliverable-disclosures"
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
              <label
                htmlFor="update-deliverable-approval-rounds"
                className="mb-2 block text-sm font-medium"
              >
                Approval Rounds
              </label>
              <input
                id="update-deliverable-approval-rounds"
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
    </FormModal>
  );
}
