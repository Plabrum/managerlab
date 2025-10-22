'use client';

import { use } from 'react';
import { ObjectFields } from '@/components/object-detail';
import { MediaGallery } from '@/components/object-detail/media-gallery';
import { useOObjectTypeIdGetObjectDetailSuspense } from '@/openapi/objects/objects';
import { DetailPageLayout } from '@/components/detail-page-layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

export default function DeliverableDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const { data } = useOObjectTypeIdGetObjectDetailSuspense('deliverables', id);

  // Find media and campaign relations
  const mediaRelation = data.relations?.find(
    (rel) => rel.relation_name === 'media'
  );
  const campaignRelation = data.relations?.find(
    (rel) => rel.relation_name === 'campaign'
  );

  return (
    <DetailPageLayout
      title={data.title}
      state={data.state}
      createdAt={data.created_at}
      updatedAt={data.updated_at}
      actions={data.actions}
      actionGroup="deliverable_actions"
      objectId={id}
      objectData={data}
    >
      <div className="container mx-auto py-6">
        <div className="space-y-6">
          {/* Two Column Grid */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {/* Left Column - Fields */}
            <ObjectFields fields={data.fields} />

            {/* Right Column - Campaign (if exists) */}
            {campaignRelation && campaignRelation.objects.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>{campaignRelation.relation_label}</CardTitle>
                </CardHeader>
                <CardContent>
                  {campaignRelation.objects.map((campaign) => (
                    <div
                      key={campaign.id}
                      className="flex items-center justify-between rounded-lg border p-3"
                    >
                      <div>
                        <p className="font-medium">{campaign.title}</p>
                        {campaign.subtitle && (
                          <p className="text-muted-foreground text-sm">
                            {campaign.subtitle}
                          </p>
                        )}
                      </div>
                      <Button variant="ghost" size="sm" asChild>
                        <Link href={`/${campaign.object_type}/${campaign.id}`}>
                          View
                        </Link>
                      </Button>
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}
          </div>

          {/* Media Gallery - Full Width at Bottom */}
          {mediaRelation && mediaRelation.objects.length > 0 && (
            <MediaGallery items={mediaRelation.objects} />
          )}
        </div>
      </div>
    </DetailPageLayout>
  );
}
