import { createTypedForm } from '@/components/forms/base';
import type { RosterCreateSchema } from '@/openapi/ariveAPI.schemas';

const { FormModal, FormString, FormEmail } =
  createTypedForm<RosterCreateSchema>();

interface CreateRosterFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: RosterCreateSchema) => void;
  isSubmitting: boolean;
  actionLabel: string;
}

/**
 * Form for creating a new roster member (talent/influencer)
 */
export function CreateRosterForm({
  isOpen,
  onClose,
  onSubmit,
  isSubmitting,
  actionLabel,
}: CreateRosterFormProps) {
  return (
    <FormModal
      isOpen={isOpen}
      onClose={onClose}
      title={actionLabel}
      subTitle="Fill out the form below to create a new roster member."
      onSubmit={onSubmit}
      isSubmitting={isSubmitting}
      submitText="Create Roster Member"
    >
      <FormString
        name="name"
        label="Name"
        placeholder="Talent name"
        required="Name is required"
        autoFocus
      />

      <FormEmail name="email" label="Email" placeholder="email@example.com" />

      <FormString name="phone" label="Phone" placeholder="+1 (555) 000-0000" />

      <FormString
        name="instagram_handle"
        label="Instagram Handle"
        placeholder="@username"
      />
    </FormModal>
  );
}
