'use client';

import { Button } from '@/components/ui/button';
import { createTypedForm } from '@/components/forms/base';
import type { RosterCreateSchema } from '@/openapi/managerLab.schemas';

const { Form, FormString, FormEmail } = createTypedForm<RosterCreateSchema>();

interface CreateRosterFormProps {
  onSubmit: (data: RosterCreateSchema) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

/**
 * Form for creating a new roster member (talent/influencer)
 */
export function CreateRosterForm({
  onSubmit,
  onCancel,
  isSubmitting,
}: CreateRosterFormProps) {
  return (
    <Form onSubmit={onSubmit}>
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

      <div className="flex gap-3 pt-4">
        <Button type="submit" disabled={isSubmitting} className="flex-1">
          {isSubmitting ? 'Creating...' : 'Create Roster Member'}
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
