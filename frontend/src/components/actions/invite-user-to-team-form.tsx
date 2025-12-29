import { createTypedForm } from '@/components/forms/base';
import type { InviteUserToTeamSchema } from '@/openapi/ariveAPI.schemas';

const { FormModal, FormEmail } = createTypedForm<InviteUserToTeamSchema>();

interface InviteUserToTeamFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: InviteUserToTeamSchema) => void;
  isSubmitting: boolean;
  actionLabel: string;
}

/**
 * Form for inviting a user to a team via email
 */
export function InviteUserToTeamForm({
  isOpen,
  onClose,
  onSubmit,
  isSubmitting,
  actionLabel,
}: InviteUserToTeamFormProps) {
  return (
    <FormModal
      isOpen={isOpen}
      onClose={onClose}
      title={actionLabel}
      subTitle="Enter the email address of the user you want to invite. They will receive an invitation link valid for 72 hours."
      onSubmit={onSubmit}
      isSubmitting={isSubmitting}
      submitText="Send Invitation"
    >
      <FormEmail
        name="email"
        label="Email Address"
        placeholder="user@example.com"
        required="Email is required"
      />
    </FormModal>
  );
}
