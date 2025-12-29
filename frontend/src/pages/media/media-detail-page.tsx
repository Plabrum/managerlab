import { useParams } from '@tanstack/react-router';
import { MediaFields } from '@/components/media-detail';
import { MediaViewer } from '@/components/media-viewer';
import { ObjectActions } from '@/components/object-detail';
import { PageTopBar } from '@/components/page-topbar';
import { ActionGroupType } from '@/openapi/ariveAPI.schemas';
import { useMediaIdGetMediaSuspense } from '@/openapi/media/media';

export function MediaDetailPage() {
  const { id } = useParams({ strict: false });
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
      <div className="container mx-auto space-y-6 p-6">
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
