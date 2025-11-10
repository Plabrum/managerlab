'use client';

import { format } from 'date-fns';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { DeliverableResponseSchema } from '@/openapi/ariveAPI.schemas';

interface DeliverableFieldsProps {
  deliverable: DeliverableResponseSchema;
}

export function DeliverableFields({ deliverable }: DeliverableFieldsProps) {
  const formatDate = (value: string | null | undefined) => {
    if (!value) return '—';
    try {
      return format(new Date(value), 'PPP');
    } catch {
      return value;
    }
  };

  const formatValue = (value: unknown) => {
    if (value === null || value === undefined) return '—';
    return String(value);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Details</CardTitle>
      </CardHeader>
      <CardContent>
        <dl className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          {deliverable.content && (
            <div className="space-y-1 sm:col-span-2">
              <dt className="text-muted-foreground text-sm font-medium">
                Content
              </dt>
              <dd className="text-sm">{deliverable.content}</dd>
            </div>
          )}

          {deliverable.deliverable_type && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                Type
              </dt>
              <dd className="text-sm">
                <Badge variant="outline">{deliverable.deliverable_type}</Badge>
              </dd>
            </div>
          )}

          <div className="space-y-1">
            <dt className="text-muted-foreground text-sm font-medium">
              Platform
            </dt>
            <dd className="text-sm">
              <Badge variant="outline">{deliverable.platforms}</Badge>
            </dd>
          </div>

          <div className="space-y-1">
            <dt className="text-muted-foreground text-sm font-medium">Count</dt>
            <dd className="text-sm">{deliverable.count}</dd>
          </div>

          <div className="space-y-1">
            <dt className="text-muted-foreground text-sm font-medium">
              Posting Date
            </dt>
            <dd className="text-sm">{formatDate(deliverable.posting_date)}</dd>
          </div>

          {deliverable.posting_start_date && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                Posting Start Date
              </dt>
              <dd className="text-sm">
                {formatDate(deliverable.posting_start_date)}
              </dd>
            </div>
          )}

          {deliverable.posting_end_date && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                Posting End Date
              </dt>
              <dd className="text-sm">
                {formatDate(deliverable.posting_end_date)}
              </dd>
            </div>
          )}

          {deliverable.handles && deliverable.handles.length > 0 && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                Handles
              </dt>
              <dd className="text-sm">{deliverable.handles.join(', ')}</dd>
            </div>
          )}

          {deliverable.hashtags && deliverable.hashtags.length > 0 && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                Hashtags
              </dt>
              <dd className="text-sm">{deliverable.hashtags.join(', ')}</dd>
            </div>
          )}

          {deliverable.disclosures && deliverable.disclosures.length > 0 && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                Disclosures
              </dt>
              <dd className="text-sm">{deliverable.disclosures.join(', ')}</dd>
            </div>
          )}

          <div className="space-y-1">
            <dt className="text-muted-foreground text-sm font-medium">
              Approval Required
            </dt>
            <dd className="text-sm">
              <Badge
                variant={
                  deliverable.approval_required ? 'default' : 'secondary'
                }
              >
                {deliverable.approval_required ? 'Yes' : 'No'}
              </Badge>
            </dd>
          </div>

          {deliverable.approval_rounds !== null &&
            deliverable.approval_rounds !== undefined && (
              <div className="space-y-1">
                <dt className="text-muted-foreground text-sm font-medium">
                  Approval Rounds
                </dt>
                <dd className="text-sm">{deliverable.approval_rounds}</dd>
              </div>
            )}

          {deliverable.campaign_id && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                Campaign ID
              </dt>
              <dd className="text-sm">
                {formatValue(deliverable.campaign_id)}
              </dd>
            </div>
          )}

          {deliverable.assigned_roster && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                Assigned Roster
              </dt>
              <dd className="text-sm">{deliverable.assigned_roster.name}</dd>
            </div>
          )}

          <div className="space-y-1">
            <dt className="text-muted-foreground text-sm font-medium">
              Created At
            </dt>
            <dd className="text-sm">{formatDate(deliverable.created_at)}</dd>
          </div>

          <div className="space-y-1">
            <dt className="text-muted-foreground text-sm font-medium">
              Updated At
            </dt>
            <dd className="text-sm">{formatDate(deliverable.updated_at)}</dd>
          </div>
        </dl>
      </CardContent>
    </Card>
  );
}
