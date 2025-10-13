'use client';

import { use, useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import {
  ObjectHeader,
  ObjectActions,
  ObjectFields,
  ObjectParents,
  ObjectChildren,
} from '@/components/object-detail';
import { useOObjectTypeIdGetObjectDetailSuspense } from '@/openapi/objects/objects';
import { useBreadcrumb } from '@/components/breadcrumb-provider';
import {
  ActionGroupType,
  type ActionDTO,
  type ActionExecutionResponse,
} from '@/openapi/managerLab.schemas';

export default function CampaignDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const pathname = usePathname();
  const router = useRouter();
  const { setBreadcrumb, clearBreadcrumb } = useBreadcrumb();

  const { data } = useOObjectTypeIdGetObjectDetailSuspense('campaigns', id);

  // Set breadcrumb title after data loads
  useEffect(() => {
    setBreadcrumb(pathname, data?.title);
    return () => {
      clearBreadcrumb(pathname);
    };
  }, [data?.title, pathname, setBreadcrumb, clearBreadcrumb]);

  // Handle action completion - redirect on delete
  const handleActionComplete = (
    action: ActionDTO,
    response: ActionExecutionResponse
  ) => {
    const isDeleteAction = action.action.toLowerCase().includes('delete');

    if (isDeleteAction && response.success) {
      router.push('/campaigns');
    }
  };

  return (
    <div className="container mx-auto py-6">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <ObjectHeader
            title={data.title}
            state={data.state}
            createdAt={data.created_at}
            updatedAt={data.updated_at}
          />
          <ObjectActions
            actions={data.actions}
            actionGroup={ActionGroupType.campaign_actions}
            objectId={id}
            onActionComplete={handleActionComplete}
          />
        </div>

        {/* Two Column Grid */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Left Column - Fields */}
          <ObjectFields fields={data.fields} />
        </div>

        {/* Parents */}
        <ObjectParents parents={data.parents || []} />

        {/* Children */}
        {data.children && <ObjectChildren items={data.children} />}
      </div>
    </div>
  );
}
