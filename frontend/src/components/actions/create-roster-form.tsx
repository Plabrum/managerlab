import { useRef, useState } from 'react';
import { Upload, X, Image as ImageIcon } from 'lucide-react';
import { createTypedForm } from '@/components/forms/base';
import { Button } from '@/components/ui/button';
import { CollapsibleFormSection } from '@/components/ui/collapsible-form-section';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useMediaUpload } from '@/hooks/useMediaUpload';
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
 * Profile photo upload component
 */
function ProfilePhotoUpload({
  onChange,
}: {
  onChange: (mediaId: string | null) => void;
}) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const { uploadFile, status, progress } = useMediaUpload();

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Please select an image file');
      return;
    }

    console.log('Starting upload for file:', file.name);

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result as string);
    };
    reader.readAsDataURL(file);

    // Upload file
    await uploadFile(file, {
      autoRegister: true,
      onSuccess: (result) => {
        onChange(result.mediaId);
      },
    });
  };

  const handleRemove = () => {
    setPreview(null);
    onChange(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="space-y-4 rounded-lg border p-4">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium">Profile Photo</h4>
        {preview && (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={handleRemove}
            disabled={status === 'uploading' || status === 'registering'}
          >
            <X className="h-4 w-4" />
            Remove
          </Button>
        )}
      </div>

      <div className="flex items-center gap-4">
        {/* Preview */}
        <div className="flex h-24 w-24 shrink-0 items-center justify-center overflow-hidden rounded-lg border bg-muted">
          {preview ? (
            <img
              src={preview}
              alt="Profile preview"
              className="h-full w-full object-cover"
            />
          ) : (
            <ImageIcon className="h-8 w-8 text-muted-foreground" />
          )}
        </div>

        {/* Upload Button */}
        <div className="flex-1">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
          />
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => fileInputRef.current?.click()}
            disabled={status === 'uploading' || status === 'registering'}
          >
            <Upload className="mr-2 h-4 w-4" />
            {preview ? 'Change Photo' : 'Choose File'}
          </Button>
          <p className="mt-2 text-xs text-muted-foreground">
            {status === 'uploading' && `Uploading... ${progress}%`}
            {status === 'registering' && 'Processing...'}
            {status === 'complete' && preview && 'Upload complete'}
            {status === 'idle' && 'JPG, PNG, or GIF (max 10MB)'}
          </p>
        </div>
      </div>
    </div>
  );
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
        {/* Profile Photo Section */}
        <FormCustom name="profile_photo_id">
          {({ onChange }) => <ProfilePhotoUpload onChange={onChange} />}
        </FormCustom>

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
            <FormString name="address.state" label="State" placeholder="NY" />
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
