'use client';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import type { DeliverableUpdateSchema } from '@/openapi/managerLab.schemas';
import { useState } from 'react';

interface UpdateDeliverableFormProps {
  defaultValues?: Partial<DeliverableUpdateSchema>;
  onSubmit: (data: DeliverableUpdateSchema) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

/**
 * Example form for updating a deliverable
 * This demonstrates how to create action-specific forms
 */
export function UpdateDeliverableForm({
  defaultValues,
  onSubmit,
  onCancel,
  isSubmitting,
}: UpdateDeliverableFormProps) {
  const [title, setTitle] = useState(defaultValues?.title || '');
  const [content, setContent] = useState(defaultValues?.content || '');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      title,
      content: content || null,
      // Include other optional fields from defaultValues
      platforms: defaultValues?.platforms || undefined,
      posting_date: defaultValues?.posting_date || undefined,
      notes: defaultValues?.notes || undefined,
      campaign_id: defaultValues?.campaign_id || undefined,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="title">Title</Label>
        <Input
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Deliverable title"
          disabled={isSubmitting}
          required
        />
      </div>

      <div>
        <Label htmlFor="content">Content</Label>
        <Textarea
          id="content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Post content..."
          rows={4}
          disabled={isSubmitting}
        />
      </div>

      <div className="flex gap-3 pt-4">
        <Button type="submit" disabled={isSubmitting} className="flex-1">
          {isSubmitting ? 'Updating...' : 'Update Deliverable'}
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
