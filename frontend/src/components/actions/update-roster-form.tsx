'use client';

import { createTypedForm } from '@/components/forms/base';
import type { RosterUpdateSchema } from '@/openapi/ariveAPI.schemas';

const { FormModal, FormString } = createTypedForm<RosterUpdateSchema>();

interface UpdateRosterFormProps {
  isOpen: boolean;
  onClose: () => void;
  defaultValues?: Partial<RosterUpdateSchema>;
  onSubmit: (data: RosterUpdateSchema) => void;
  isSubmitting: boolean;
  actionLabel: string;
}

/**
 * Form for updating a roster member
 */
export function UpdateRosterForm({
  isOpen,
  onClose,
  defaultValues,
  onSubmit,
  isSubmitting,
  actionLabel,
}: UpdateRosterFormProps) {
  return (
    <FormModal
      isOpen={isOpen}
      onClose={onClose}
      title={actionLabel}
      subTitle="Update the roster member information below."
      onSubmit={onSubmit}
      defaultValues={defaultValues}
      isSubmitting={isSubmitting}
      submitText="Update Roster Member"
    >
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
    </FormModal>
  );
}
