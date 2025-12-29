import { createFileRoute } from '@tanstack/react-router';
import { z } from 'zod';
import ErrorPage from '@/routes/_public/error';
import { MediaFields } from '@/components/media-detail';
import { MediaViewer } from '@/components/media-viewer';
import { ObjectActions } from '@/components/object-detail';
import { PageTopBar } from '@/components/page-topbar';
import { ActionGroupType } from '@/openapi/ariveAPI.schemas';
import { useMediaIdGetMediaSuspense } from '@/openapi/media/media';

const searchSchema = z.object({
  edit: z.boolean().optional(),
  tab: z.enum(['summary', 'activity']).optional().default('summary'),
});

export const Route = createFileRoute('/_authenticated/media/$id')({
  component: MediaDetailPage,
  validateSearch: searchSchema,
  errorComponent: ({ error }) => {
    if (
      error &&
      typeof error === 'object' &&
      'status' in error &&
      error.status === 404
    ) {
      return <ErrorPage />;
    }
    throw error;
  },
});

function MediaDetailPage() {
  const { id } = Route.useParams();

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
