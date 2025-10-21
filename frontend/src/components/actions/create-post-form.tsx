'use client';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type {
  PostCreateSchema,
  SocialMediaPlatforms,
  CompensationStructure,
} from '@/openapi/managerLab.schemas';
import { SocialMediaPlatforms as SocialMediaPlatformsEnum } from '@/openapi/managerLab.schemas';
import { CompensationStructure as CompensationStructureEnum } from '@/openapi/managerLab.schemas';
import { useState } from 'react';
import { useListObjectsSuspense } from '@/openapi/objects/objects';

interface CreatePostFormProps {
  onSubmit: (data: PostCreateSchema) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

/**
 * Form for creating a new post
 */
export function CreatePostForm({
  onSubmit,
  onCancel,
  isSubmitting,
}: CreatePostFormProps) {
  const [title, setTitle] = useState('');
  const [platforms, setPlatforms] = useState<SocialMediaPlatforms | ''>('');
  const [postingDate, setPostingDate] = useState('');
  const [content, setContent] = useState('');
  const [compensationStructure, setCompensationStructure] = useState<
    CompensationStructure | ''
  >('');
  const [campaignId, setCampaignId] = useState<string>('');
  const [notes, setNotes] = useState('');

  // Fetch campaigns for the dropdown
  const { data: campaignsData } = useListObjectsSuspense('campaigns', {
    offset: 0,
    limit: 100,
    sorts: [],
    filters: [],
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validate required fields
    if (!title.trim() || !platforms || !postingDate) {
      return;
    }

    // Parse notes JSON if provided
    let parsedNotes: { [key: string]: unknown } | undefined;
    if (notes.trim()) {
      try {
        parsedNotes = JSON.parse(notes);
      } catch {
        // If JSON parsing fails, wrap in object
        parsedNotes = { text: notes };
      }
    }

    const postData: PostCreateSchema = {
      title: title.trim(),
      platforms: platforms as SocialMediaPlatforms,
      posting_date: new Date(postingDate).toISOString(),
      content: content.trim() || undefined,
      compensation_structure: compensationStructure || undefined,
      campaign_id: campaignId ? parseInt(campaignId, 10) : undefined,
      notes: parsedNotes,
    };

    onSubmit(postData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="title">
          Title <span className="text-destructive">*</span>
        </Label>
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
        <Label htmlFor="platforms">
          Platform <span className="text-destructive">*</span>
        </Label>
        <Select
          value={platforms}
          onValueChange={(value) => setPlatforms(value as SocialMediaPlatforms)}
          disabled={isSubmitting}
          required
        >
          <SelectTrigger id="platforms">
            <SelectValue placeholder="Select platform" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={SocialMediaPlatformsEnum.instagram}>
              Instagram
            </SelectItem>
            <SelectItem value={SocialMediaPlatformsEnum.facebook}>
              Facebook
            </SelectItem>
            <SelectItem value={SocialMediaPlatformsEnum.tiktok}>
              TikTok
            </SelectItem>
            <SelectItem value={SocialMediaPlatformsEnum.youtube}>
              YouTube
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div>
        <Label htmlFor="posting_date">
          Posting Date <span className="text-destructive">*</span>
        </Label>
        <Input
          id="posting_date"
          type="datetime-local"
          value={postingDate}
          onChange={(e) => setPostingDate(e.target.value)}
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

      <div>
        <Label htmlFor="compensation_structure">Compensation Structure</Label>
        <Select
          value={compensationStructure}
          onValueChange={(value) =>
            setCompensationStructure(value as CompensationStructure)
          }
          disabled={isSubmitting}
        >
          <SelectTrigger id="compensation_structure">
            <SelectValue placeholder="Select compensation structure" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={CompensationStructureEnum.flat_fee}>
              Flat Fee
            </SelectItem>
            <SelectItem value={CompensationStructureEnum.per_deliverable}>
              Per Deliverable
            </SelectItem>
            <SelectItem value={CompensationStructureEnum.performance_based}>
              Performance Based
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div>
        <Label htmlFor="campaign_id">Campaign</Label>
        <Select
          value={campaignId}
          onValueChange={setCampaignId}
          disabled={isSubmitting}
        >
          <SelectTrigger id="campaign_id">
            <SelectValue placeholder="Select campaign (optional)" />
          </SelectTrigger>
          <SelectContent>
            {campaignsData?.objects.map((campaign) => (
              <SelectItem key={campaign.id} value={campaign.id.toString()}>
                {campaign.title}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div>
        <Label htmlFor="notes">Notes (JSON format)</Label>
        <Textarea
          id="notes"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder='{"key": "value"}'
          rows={3}
          disabled={isSubmitting}
        />
        <p className="text-muted-foreground mt-1 text-xs">
          Optional: Enter valid JSON or plain text
        </p>
      </div>

      <div className="flex gap-3 pt-4">
        <Button type="submit" disabled={isSubmitting} className="flex-1">
          {isSubmitting ? 'Creating...' : 'Create Post'}
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
