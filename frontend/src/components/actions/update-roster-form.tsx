'use client';

import { Button } from '@/components/ui/button';
import { createTypedForm } from '@/components/forms/base';
import type { RosterUpdateSchema } from '@/openapi/managerLab.schemas';

const { Form, FormString } = createTypedForm<RosterUpdateSchema>();

interface UpdateRosterFormProps {
  defaultValues?: Partial<RosterUpdateSchema>;
  onSubmit: (data: RosterUpdateSchema) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

/**
 * Form for updating a roster member
 */
export function UpdateRosterForm({
  defaultValues,
  onSubmit,
  onCancel,
  isSubmitting,
}: UpdateRosterFormProps) {
  return (
    <Form onSubmit={onSubmit} defaultValues={defaultValues}>
      <FormString name="name" label="Name" placeholder="Roster member name" />

      <FormString
        name="email"
        label="Email"
        type="email"
        placeholder="email@example.com"
      />

      <FormString
        name="phone"
        label="Phone"
        type="tel"
        placeholder="Phone number"
      />

      <FormString
        name="instagram_handle"
        label="Instagram Handle"
        placeholder="@username"
      />

      <FormString
        name="facebook_handle"
        label="Facebook Handle"
        placeholder="@username"
      />

      <FormString
        name="tiktok_handle"
        label="TikTok Handle"
        placeholder="@username"
      />

      <FormString
        name="youtube_channel"
        label="YouTube Channel"
        placeholder="Channel name or URL"
      />

      <div className="flex gap-3 pt-4">
        <Button type="submit" disabled={isSubmitting} className="flex-1">
          {isSubmitting ? 'Updating...' : 'Update Roster Member'}
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
