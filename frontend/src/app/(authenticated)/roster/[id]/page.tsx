'use client';

import { use, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import {
  ObjectHeader,
  ObjectFields,
  ObjectParents,
  ObjectChildren,
} from '@/components/object-detail';
import { useOObjectTypeIdGetObjectDetailSuspense } from '@/openapi/objects/objects';
import { useBreadcrumb } from '@/components/breadcrumb-provider';

export default function RosterDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const pathname = usePathname();
  const { setBreadcrumb, clearBreadcrumb } = useBreadcrumb();

  const { data } = useOObjectTypeIdGetObjectDetailSuspense('roster', id);

  // Set breadcrumb title after data loads
  useEffect(() => {
    setBreadcrumb(pathname, data?.title);
    return () => {
      clearBreadcrumb(pathname);
    };
  }, [data?.title, pathname, setBreadcrumb, clearBreadcrumb]);

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
          {/* TODO: Add ObjectActions when roster_actions ActionGroupType is added to backend */}
        </div>

        {/* Fields */}
        <ObjectFields fields={data.fields} />

        {/* Parents */}
        <ObjectParents parents={data.parents || []} />

        {/* Children */}
        {data.children && <ObjectChildren items={data.children} />}
      </div>
    </div>
  );
}
