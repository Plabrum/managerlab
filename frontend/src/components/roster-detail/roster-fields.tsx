'use client';

import { format } from 'date-fns';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { RosterSchema } from '@/openapi/managerLab.schemas';

interface RosterFieldsProps {
  roster: RosterSchema;
}

export function RosterFields({ roster }: RosterFieldsProps) {
  const formatDate = (value: string | null | undefined) => {
    if (!value) return '—';
    try {
      return format(new Date(value), 'PPP');
    } catch {
      return value;
    }
  };

  const formatDateTime = (value: string | null | undefined) => {
    if (!value) return '—';
    try {
      return format(new Date(value), 'PPP p');
    } catch {
      return value;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Details</CardTitle>
      </CardHeader>
      <CardContent>
        <dl className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          {roster.email && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                Email
              </dt>
              <dd className="text-sm">
                <a
                  href={`mailto:${roster.email}`}
                  className="text-primary hover:underline"
                >
                  {roster.email}
                </a>
              </dd>
            </div>
          )}

          {roster.phone && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                Phone
              </dt>
              <dd className="text-sm">
                <a
                  href={`tel:${roster.phone}`}
                  className="text-primary hover:underline"
                >
                  {roster.phone}
                </a>
              </dd>
            </div>
          )}

          {roster.birthdate && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                Birthdate
              </dt>
              <dd className="text-sm">{formatDate(roster.birthdate)}</dd>
            </div>
          )}

          {roster.instagram_handle && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                Instagram
              </dt>
              <dd className="text-sm">
                <a
                  href={`https://instagram.com/${roster.instagram_handle.replace('@', '')}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:underline"
                >
                  {roster.instagram_handle}
                </a>
              </dd>
            </div>
          )}

          {roster.facebook_handle && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                Facebook
              </dt>
              <dd className="text-sm">
                <a
                  href={`https://facebook.com/${roster.facebook_handle}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:underline"
                >
                  {roster.facebook_handle}
                </a>
              </dd>
            </div>
          )}

          {roster.tiktok_handle && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                TikTok
              </dt>
              <dd className="text-sm">
                <a
                  href={`https://tiktok.com/@${roster.tiktok_handle.replace('@', '')}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:underline"
                >
                  {roster.tiktok_handle}
                </a>
              </dd>
            </div>
          )}

          {roster.youtube_channel && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                YouTube
              </dt>
              <dd className="text-sm">
                <a
                  href={roster.youtube_channel}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:underline"
                >
                  {roster.youtube_channel}
                </a>
              </dd>
            </div>
          )}

          <div className="space-y-1">
            <dt className="text-muted-foreground text-sm font-medium">
              Created At
            </dt>
            <dd className="text-sm">{formatDateTime(roster.created_at)}</dd>
          </div>

          <div className="space-y-1">
            <dt className="text-muted-foreground text-sm font-medium">
              Updated At
            </dt>
            <dd className="text-sm">{formatDateTime(roster.updated_at)}</dd>
          </div>
        </dl>
      </CardContent>
    </Card>
  );
}
