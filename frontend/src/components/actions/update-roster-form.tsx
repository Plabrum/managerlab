import { createTypedForm } from '@/components/forms/base';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { RosterUpdateSchema } from '@/openapi/ariveAPI.schemas';

const { FormSheet, FormString, FormDatetime, FormImageUpload, FormCustom } =
  createTypedForm<RosterUpdateSchema>();

interface UpdateRosterFormProps {
  isOpen: boolean;
  onClose: () => void;
  defaultValues?: Partial<RosterUpdateSchema>;
  onSubmit: (data: RosterUpdateSchema) => void;
  isSubmitting: boolean;
  actionLabel: string;
}

const GENDER_OPTIONS = [
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
  { value: 'other', label: 'Other' },
];

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
    <FormSheet
      isOpen={isOpen}
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
      title={actionLabel}
      subTitle="Update the roster member information below."
      onSubmit={onSubmit}
      defaultValues={defaultValues}
      isSubmitting={isSubmitting}
      submitText="Update Roster Member"
      side="right"
    >
      {/* Basic Information */}
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

      {/* Social Media Section */}
      <div className="space-y-4 rounded-lg border p-4">
        <h4 className="text-sm font-medium">Social Media</h4>

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
      </div>

      {/* Profile Photo Section */}
      <FormImageUpload
        name="profile_photo_id"
        label="Profile Photo"
        description="JPG, PNG, or GIF (max 10MB)"
      />

      {/* Address Section */}
      <div className="space-y-4 rounded-lg border p-4">
        <h4 className="text-sm font-medium">Address</h4>
        <FormString
          name="address.address1"
          label="Street Address"
          placeholder="123 Main St"
        />
        <FormString
          name="address.address2"
          label="Apt, Suite, etc."
          placeholder="Apt 4B"
        />
        <div className="grid grid-cols-2 gap-4">
          <FormString name="address.city" label="City" placeholder="New York" />
          <FormString name="address.state" label="State" placeholder="NY" />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <FormString name="address.zip" label="ZIP Code" placeholder="10001" />
          <FormString name="address.country" label="Country" placeholder="US" />
        </div>
      </div>

      {/* Birthday & Gender Section */}
      <div className="space-y-4 rounded-lg border p-4">
        <h4 className="text-sm font-medium">Personal Information</h4>

        <FormDatetime
          name="birthdate"
          label="Birthday"
          placeholder="Select date"
          showTime={false}
        />

        <FormCustom name="gender">
          {({ value, onChange }) => {
            // Determine if we should show the "other" text field
            // Show it if value is anything other than 'male' or 'female'
            const showOtherField =
              value !== 'male' &&
              value !== 'female' &&
              value !== undefined &&
              value !== null &&
              value !== '';
            const selectValue = showOtherField
              ? 'other'
              : (value as string) || '';

            return (
              <div className="space-y-3">
                <div>
                  <Label htmlFor="gender-select">Gender</Label>
                  <Select
                    value={selectValue}
                    onValueChange={(newValue) => {
                      if (newValue === 'other') {
                        // Set to empty string to show the text input with empty value
                        onChange('');
                      } else {
                        onChange(newValue);
                      }
                    }}
                  >
                    <SelectTrigger id="gender-select" className="mt-1">
                      <SelectValue placeholder="Select gender (optional)" />
                    </SelectTrigger>
                    <SelectContent>
                      {GENDER_OPTIONS.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                {selectValue === 'other' && (
                  <div>
                    <Label htmlFor="gender-custom">Please specify</Label>
                    <Input
                      id="gender-custom"
                      type="text"
                      placeholder="Enter gender identity"
                      value={(value as string) || ''}
                      onChange={(e) => onChange(e.target.value)}
                      className="mt-1"
                      autoFocus
                    />
                  </div>
                )}
              </div>
            );
          }}
        </FormCustom>
      </div>
    </FormSheet>
  );
}
