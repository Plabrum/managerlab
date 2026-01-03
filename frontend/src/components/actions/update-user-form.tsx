import { createTypedForm } from '@/components/forms/base';
import type { UserUpdateSchema } from '@/openapi/ariveAPI.schemas';

const { FormModal, FormString } = createTypedForm<UserUpdateSchema>();

interface UpdateUserFormProps {
  isOpen: boolean;
  onClose: () => void;
  defaultValues?: Partial<UserUpdateSchema>;
  onSubmit: (data: UserUpdateSchema) => void;
  isSubmitting: boolean;
  actionLabel: string;
}

/**
 * Form for updating user profile
 */
export function UpdateUserForm({
  isOpen,
  onClose,
  defaultValues,
  onSubmit,
  isSubmitting,
  actionLabel,
}: UpdateUserFormProps) {
  return (
    <FormModal
      isOpen={isOpen}
      onClose={onClose}
      title={actionLabel}
      subTitle="Update your profile information below."
      onSubmit={onSubmit}
      defaultValues={defaultValues}
      isSubmitting={isSubmitting}
      submitText="Update Profile"
    >
      <FormString name="name" label="Name" placeholder="Your full name" />
    </FormModal>
  );
}
