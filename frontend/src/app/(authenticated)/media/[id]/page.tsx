'use client';

import { use } from 'react';
import { ObjectActions } from '@/components/object-detail';
import { MediaFields } from '@/components/media-detail';
import { MediaViewer } from '@/components/media-viewer';
import { useMediaIdGetMediaSuspense } from '@/openapi/media/media';
import { PageTopBar } from '@/components/page-topbar';
import { ActionGroupType } from '@/openapi/ariveAPI.schemas';

export default function MediaDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const { data, refetch } = useMediaIdGetMediaSuspense(id);

  return (
    <PageTopBar
      title={data.file_name}
      state={data.state}
      actions={
        <ObjectActions
          data={data}
          actionGroup={ActionGroupType.media_actions}
          onRefetch={refetch}
        />
      }
    >
      <div className="space-y-6">
        {/* Two Column Grid */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Left Column - Fields */}
          <MediaFields media={data} />

          {/* Right Column - Media Viewer */}
          <MediaViewer url={data.view_url} alt={data.file_name} />
        </div>
      </div>
    </PageTopBar>
  );
}
