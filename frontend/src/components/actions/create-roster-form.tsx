'use client';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import type { RosterCreateSchema } from '@/openapi/managerLab.schemas';
import { useState } from 'react';

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
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [instagramHandle, setInstagramHandle] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validate required fields
    if (!name.trim()) {
      return;
    }

    const rosterData: RosterCreateSchema = {
      name: name.trim(),
      email: email.trim() || undefined,
      phone: phone.trim() || undefined,
      instagram_handle: instagramHandle.trim() || undefined,
    };

    onSubmit(rosterData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="name">
          Name <span className="text-destructive">*</span>
        </Label>
        <Input
          id="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Talent name"
          disabled={isSubmitting}
          required
        />
      </div>

      <div>
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="email@example.com"
          disabled={isSubmitting}
        />
      </div>

      <div>
        <Label htmlFor="phone">Phone</Label>
        <Input
          id="phone"
          type="tel"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          placeholder="+1 (555) 000-0000"
          disabled={isSubmitting}
        />
      </div>

      <div>
        <Label htmlFor="instagram_handle">Instagram Handle</Label>
        <Input
          id="instagram_handle"
          value={instagramHandle}
          onChange={(e) => setInstagramHandle(e.target.value)}
          placeholder="@username"
          disabled={isSubmitting}
        />
      </div>

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
    </form>
  );
}
