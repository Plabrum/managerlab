import { createTypedForm } from '@/components/forms/base';
import { CollapsibleFormSection } from '@/components/ui/collapsible-form-section';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import type { RosterCreateSchema } from '@/openapi/ariveAPI.schemas';

const { FormModal, FormString, FormEmail, FormDatetime, FormCustom } =
  createTypedForm<RosterCreateSchema>();

interface CreateRosterFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: RosterCreateSchema) => void;
  isSubmitting: boolean;
  actionLabel: string;
}

const GENDER_OPTIONS = [
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
  { value: 'other', label: 'Other' },
];

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
      {/* Basic Information */}
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

      {/* Additional Options - Collapsible */}
      <CollapsibleFormSection title="Additional options" defaultOpen={false}>
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
            <FormString
              name="address.city"
              label="City"
              placeholder="New York"
            />
            <FormString
              name="address.state"
              label="State"
              placeholder="NY"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <FormString
              name="address.zip"
              label="ZIP Code"
              placeholder="10001"
            />
            <FormString
              name="address.country"
              label="Country"
              placeholder="US"
            />
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
              // Check if current value is a custom gender (not male/female)
              const isCustomGender =
                value && value !== 'male' && value !== 'female';
              // For the dropdown, show 'other' if we have a custom value or if value is explicitly 'other'
              const selectValue = isCustomGender || value === 'other' ? 'other' : (value as string) || '';

              return (
                <div className="space-y-3">
                  <div>
                    <Label htmlFor="gender-select">Gender</Label>
                    <Select
                      value={selectValue}
                      onValueChange={(newValue) => {
                        if (newValue === 'other') {
                          // Set to 'other' so the select shows it selected
                          onChange('other');
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
                        value={isCustomGender ? (value as string) : ''}
                        onChange={(e) => {
                          // Update to the custom text, but keep it as 'other' if empty
                          onChange(e.target.value || 'other');
                        }}
                        className="mt-1"
                      />
                    </div>
                  )}
                </div>
              );
            }}
          </FormCustom>
        </div>

        {/* Social Media Section */}
        <div className="space-y-4 rounded-lg border p-4">
          <h4 className="text-sm font-medium">Social Media</h4>

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
      </CollapsibleFormSection>
    </FormModal>
  );
}
