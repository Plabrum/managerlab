'use client';

import { InstagramPost } from './instagram-post';
import { EmptyPreview } from './empty-preview';
import type {
  DeliverableResponseSchema,
  DeliverableMediaAssociationSchema,
  RosterInDeliverableSchema,
} from '@/openapi/ariveAPI.schemas';

interface DeliverablePreviewProps {
  deliverable: DeliverableResponseSchema;
  mediaAssociation: DeliverableMediaAssociationSchema | undefined;
  roster: RosterInDeliverableSchema | null | undefined;
}

export function DeliverablePreview({
  deliverable,
  mediaAssociation,
  roster,
}: DeliverablePreviewProps) {
  // Get platform directly from deliverable (type-safe!)
  const platform = deliverable.platforms;
  const content = deliverable.content || deliverable.title;
  const postingDate = deliverable.posting_date;

  // If we don't have the minimum required data, show empty preview
  if (!mediaAssociation || !roster || !platform) {
    return <EmptyPreview />;
  }

  // Get image URL from media (now includes presigned URL!)
  const imageUrl = mediaAssociation.media.view_url;

  // Platform-specific preview rendering
  switch (platform.toLowerCase()) {
    case 'instagram': {
      return (
        <InstagramPost
          image_url={imageUrl}
          title={content}
          posting_date={postingDate}
          user_name={roster.name}
          user_photo="" // TODO: Get profile photo from roster.profile_photo
          user_handle={roster.instagram_handle || roster.name}
        />
      );
    }

    case 'facebook': {
      // TODO: Implement Facebook preview
      return <EmptyPreview />;
    }

    case 'tiktok': {
      // TODO: Implement TikTok preview
      return <EmptyPreview />;
    }

    case 'youtube': {
      // TODO: Implement YouTube preview
      return <EmptyPreview />;
    }

    default:
      return <EmptyPreview />;
  }
}
