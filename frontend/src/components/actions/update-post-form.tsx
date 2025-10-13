'use client';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import type { PostUpdateSchema } from '@/openapi/managerLab.schemas';
import { useState } from 'react';

interface UpdatePostFormProps {
  defaultValues?: Partial<PostUpdateSchema>;
  onSubmit: (data: PostUpdateSchema) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

/**
 * Example form for updating a post
 * This demonstrates how to create action-specific forms
 */
export function UpdatePostForm({
  defaultValues,
  onSubmit,
  onCancel,
  isSubmitting,
}: UpdatePostFormProps) {
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
      compensation_structure:
        defaultValues?.compensation_structure || undefined,
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
          placeholder="Post title"
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
          {isSubmitting ? 'Updating...' : 'Update Post'}
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
